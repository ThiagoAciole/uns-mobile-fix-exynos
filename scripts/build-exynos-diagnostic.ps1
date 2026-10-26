[CmdletBinding()]
param([string]$OutputDirectory = 'output\exynos-depth-diagnostic')

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$output = Join-Path $root $OutputDirectory
$scratch = Join-Path $root ('work\build-' + (Split-Path -Leaf $output))
$library = Join-Path $root 'work\native\exynos-depth-d32s8\libultimateninjastorm.so'
$names = @('base.apk', 'split_config.arm64_v8a.apk', 'split_config.pt.apk', 'split_config.xxhdpi.apk', 'split_InstallPack.apk')
foreach ($path in @($output, $scratch)) {
    if (Test-Path -LiteralPath $path) { throw "Diretório já existe; preservado: $path" }
}
foreach ($name in $names) {
    if (-not (Test-Path -LiteralPath (Join-Path $root "original\$name"))) { throw "APK ausente: $name" }
}
if (-not (Test-Path -LiteralPath $library)) { throw 'Execute scripts/patch-exynos-depth.ps1 antes do build.' }
$zipalign = (Get-Command zipalign -ErrorAction Stop).Source
$apksigner = (Get-Command apksigner -ErrorAction Stop).Source
$keytool = (Get-Command keytool -ErrorAction Stop).Source
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Get-ApkEntryHash([string]$Apk, [string]$Entry) {
    $zip = [IO.Compression.ZipFile]::OpenRead($Apk)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $member = $zip.GetEntry($Entry)
        if (-not $member) { throw "Entrada ausente: $Entry em $Apk" }
        $stream = $member.Open()
        try { return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-', '') }
        finally { $stream.Dispose() }
    } finally { $sha.Dispose(); $zip.Dispose() }
}
[IO.Directory]::CreateDirectory($output) | Out-Null
[IO.Directory]::CreateDirectory($scratch) | Out-Null
$signing = Join-Path $root 'work\signing'
[IO.Directory]::CreateDirectory($signing) | Out-Null
$key = Join-Path $signing 'naruto-local.p12'
$passwordFile = Join-Path $signing 'naruto-local.password'
if (-not (Test-Path -LiteralPath $key)) {
    if (Test-Path -LiteralPath $passwordFile) { throw 'Senha existente sem keystore; revise work/signing.' }
    $random = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($random) } finally { $rng.Dispose() }
    [IO.File]::WriteAllText($passwordFile, [Convert]::ToBase64String($random), [Text.Encoding]::ASCII)
    & $keytool -genkeypair -noprompt -storetype PKCS12 -keystore $key -storepass:file $passwordFile -keypass:file $passwordFile -alias naruto-local -dname 'CN=Naruto Local Diagnostic' -keyalg RSA -keysize 2048 -validity 10000
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar keystore local.' }
}
if (-not (Test-Path -LiteralPath $passwordFile)) { throw 'Senha local do keystore ausente.' }
$nativeApk = Join-Path $scratch 'native-unsigned.apk'
Copy-Item -LiteralPath (Join-Path $root 'original\split_config.arm64_v8a.apk') -Destination $nativeApk
$archive = [IO.Compression.ZipFile]::Open($nativeApk, [IO.Compression.ZipArchiveMode]::Update)
try {
    $entry = $archive.GetEntry('lib/arm64-v8a/libultimateninjastorm.so')
    if (-not $entry) { throw 'Biblioteca não encontrada no split ARM64.' }
    $entry.Delete()
    [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $library, 'lib/arm64-v8a/libultimateninjastorm.so', [IO.Compression.CompressionLevel]::NoCompression) | Out-Null
} finally { $archive.Dispose() }
$nativeAligned = Join-Path $scratch 'native-aligned.apk'
& $zipalign -f -P 16 4 $nativeApk $nativeAligned
if ($LASTEXITCODE -ne 0) { throw 'Alinhamento do split ARM64 falhou.' }
$certificate = $null
$artifacts = @()
foreach ($name in $names) {
    $original = Join-Path $root "original\$name"
    $inputApk = if ($name -eq 'split_config.arm64_v8a.apk') { $nativeAligned } else { $original }
    & $zipalign -c -P 16 4 $inputApk
    if ($LASTEXITCODE -ne 0) { throw "Entrada desalinhada: $name" }
    $signed = Join-Path $output $name
    & $apksigner sign --ks $key --ks-key-alias naruto-local --ks-pass "file:$passwordFile" --v4-signing-enabled false --out $signed $inputApk
    if ($LASTEXITCODE -ne 0) { throw "Assinatura falhou: $name" }
    $verification = @(& $apksigner verify --verbose --print-certs $signed 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Verificação falhou: $name" }
    $verification | Set-Content -LiteralPath (Join-Path $scratch "$name.verify.txt") -Encoding UTF8
    $digestLine = $verification | Where-Object { "$_" -match '^Signer #1 certificate SHA-256 digest:' } | Select-Object -First 1
    if (-not $digestLine) { throw "Certificado não identificado: $name" }
    $digest = ("$digestLine" -split ': ', 2)[1]
    if ($certificate -and $certificate -ne $digest) { throw 'Os splits têm certificados diferentes.' }
    $certificate = $digest
    & $zipalign -c -P 16 4 $signed
    if ($LASTEXITCODE -ne 0) { throw "Saída desalinhada: $name" }
    if ((Get-ApkEntryHash $original 'AndroidManifest.xml') -ne (Get-ApkEntryHash $signed 'AndroidManifest.xml')) {
        throw "Manifest alterado inesperadamente: $name"
    }
    $artifacts += [ordered]@{ name = $name; sha256 = (Get-FileHash -LiteralPath $signed).Hash }
    Write-Output "Assinado, alinhado e verificado: $name"
}
if ((Get-ApkEntryHash (Join-Path $output 'split_config.arm64_v8a.apk') 'lib/arm64-v8a/libultimateninjastorm.so') -ne (Get-FileHash -LiteralPath $library).Hash) {
    throw 'Biblioteca empacotada diferente do candidato.'
}
[ordered]@{
    status = 'diagnostic-only-not-game-validated'
    patch = 'mmDataFormat15: VkFormat129 -> VkFormat130'
    certificateSha256 = $certificate
    nativeSha256 = (Get-FileHash -LiteralPath $library).Hash
    apks = $artifacts
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding UTF8
Write-Output "Conjunto diagnóstico: $output"
