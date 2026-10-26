[CmdletBinding()]
param([string]$OutputDirectory = 'work\probe')

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$probe = Join-Path $root $OutputDirectory
$manifest = Join-Path $root 'patches\exynos\ProbeManifest.xml'
$sdk = 'C:\Users\Thiago Aciole\AppData\Local\Android\Sdk'
$ndk = Join-Path $sdk 'ndk\27.2.12479018'
$api = Join-Path $sdk 'platforms\android-37.0\android.jar'
$clang = Join-Path $ndk 'toolchains\llvm\prebuilt\windows-x86_64\bin\aarch64-linux-android28-clang.cmd'
$d8 = Join-Path $sdk 'build-tools\36.0.0\d8.bat'
$classDir = Join-Path $probe 'classes'
$dexDir = Join-Path $probe 'dex'
$javaSource = Join-Path $root 'patches\exynos\ProbeActivity.java'
$library = Join-Path $probe 'libvulkanprobe.so'
$unsigned = Join-Path $probe 'vulkan-probe-unsigned.apk'
$aligned = Join-Path $probe 'vulkan-probe-aligned.apk'
$signed = Join-Path $probe 'VulkanProbe.apk'
$key = Join-Path $probe 'probe.p12'
$password = 'probe-only-local'

foreach ($path in @($clang, $d8, $api, $manifest, (Join-Path $root 'patches\exynos\vulkan_probe.c'), $javaSource)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Pré-requisito ausente: $path" }
}
foreach ($path in @($unsigned, $aligned, $signed, $library)) {
    if (Test-Path -LiteralPath $path) { throw "Saída já existe; revise antes de sobrescrever: $path" }
}

$aapt = (Get-Command aapt -ErrorAction Stop).Source
$zipalign = (Get-Command zipalign -ErrorAction Stop).Source
$apksigner = (Get-Command apksigner -ErrorAction Stop).Source
$keytool = (Get-Command keytool -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $probe | Out-Null
$buildManifest = Join-Path $probe 'AndroidManifest.xml'
Copy-Item -LiteralPath $manifest -Destination $buildManifest

& $clang -shared -fPIC -std=c11 (Join-Path $root 'patches\exynos\vulkan_probe.c') -o $library -llog -landroid -lvulkan
if ($LASTEXITCODE -ne 0) { throw "NDK clang falhou com código $LASTEXITCODE" }

New-Item -ItemType Directory -Force -Path $classDir, $dexDir | Out-Null
$javac = (Get-Command javac -ErrorAction Stop).Source
& $javac -source 8 -target 8 -classpath $api -d $classDir $javaSource
if ($LASTEXITCODE -ne 0) { throw "javac falhou com código $LASTEXITCODE" }
$classFiles = @(Get-ChildItem -LiteralPath $classDir -Recurse -Filter '*.class' | ForEach-Object FullName)
& $d8 --release --min-api 28 --lib $api --output $dexDir $classFiles
if ($LASTEXITCODE -ne 0) { throw "d8 falhou com código $LASTEXITCODE" }
$dex = Join-Path $dexDir 'classes.dex'
if (-not (Test-Path -LiteralPath $dex -PathType Leaf)) { throw "D8 não gerou classes.dex: $dex" }

& $aapt package -f -M $buildManifest -I $api -F $unsigned
if ($LASTEXITCODE -ne 0) { throw "aapt falhou com código $LASTEXITCODE" }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::Open($unsigned, [IO.Compression.ZipArchiveMode]::Update)
try {
    [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $dex, 'classes.dex', [IO.Compression.CompressionLevel]::Optimal) | Out-Null
    [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $library, 'lib/arm64-v8a/libvulkanprobe.so', [IO.Compression.CompressionLevel]::Optimal) | Out-Null
} finally {
    $archive.Dispose()
}

& $zipalign -f -p 4 $unsigned $aligned
if ($LASTEXITCODE -ne 0) { throw "zipalign falhou com código $LASTEXITCODE" }
if (-not (Test-Path -LiteralPath $key)) {
    & $keytool -genkeypair -noprompt -storetype PKCS12 -keystore $key -storepass $password -keypass $password -alias probe -dname 'CN=Local Vulkan Probe, O=Local Test' -keyalg RSA -keysize 2048 -validity 3650
    if ($LASTEXITCODE -ne 0) { throw "keytool falhou com código $LASTEXITCODE" }
}
& $apksigner sign --ks $key --ks-key-alias probe --ks-pass "pass:$password" --key-pass "pass:$password" --out $signed $aligned
if ($LASTEXITCODE -ne 0) { throw "apksigner falhou com código $LASTEXITCODE" }
& $apksigner verify --verbose $signed
if ($LASTEXITCODE -ne 0) { throw "Verificação de assinatura falhou com código $LASTEXITCODE" }

Write-Output "Probe arm64 assinado e validado: $signed"
