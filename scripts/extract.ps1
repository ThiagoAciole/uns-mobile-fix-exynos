[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$original = Join-Path $root 'original'
$work = Join-Path $root 'work'
$apkNames = @(
    'base.apk',
    'split_InstallPack.apk',
    'split_config.arm64_v8a.apk',
    'split_config.pt.apk',
    'split_config.xxhdpi.apk'
)

foreach ($name in $apkNames) {
    if (-not (Test-Path -LiteralPath (Join-Path $original $name) -PathType Leaf)) {
        throw "APK ausente: $name"
    }
}

$apktool = Get-Command apktool -ErrorAction Stop
$decodedBase = Join-Path $work 'decoded\base'
if (Test-Path -LiteralPath $decodedBase) {
    if (-not (Test-Path -LiteralPath (Join-Path $decodedBase 'apktool.yml') -PathType Leaf)) {
        throw "Saída existente parece incompleta: $decodedBase"
    }
} else {
    & $apktool.Source d (Join-Path $original 'base.apk') -o $decodedBase
    if ($LASTEXITCODE -ne 0) { throw "Apktool falhou com código $LASTEXITCODE" }
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$nativeDir = Join-Path $work 'native'
$nativePath = Join-Path $nativeDir 'libultimateninjastorm.so'
New-Item -ItemType Directory -Force -Path $nativeDir | Out-Null
$nativeApk = [IO.Compression.ZipFile]::OpenRead((Join-Path $original 'split_config.arm64_v8a.apk'))
try {
    $nativeEntry = $nativeApk.GetEntry('lib/arm64-v8a/libultimateninjastorm.so')
    if ($null -eq $nativeEntry) { throw 'Biblioteca ARM64 ausente no split.' }
    if (-not (Test-Path -LiteralPath $nativePath)) {
        [IO.Compression.ZipFileExtensions]::ExtractToFile($nativeEntry, $nativePath)
    }
} finally {
    $nativeApk.Dispose()
}

$assetsDir = Join-Path $work 'assets'
New-Item -ItemType Directory -Force -Path $assetsDir | Out-Null
$pack = [IO.Compression.ZipFile]::OpenRead((Join-Path $original 'split_InstallPack.apk'))
try {
    $inventory = foreach ($entry in $pack.Entries) {
        [pscustomobject]@{
            Path = $entry.FullName
            SizeBytes = $entry.Length
            CompressedBytes = $entry.CompressedLength
        }
    }
    $inventory | Export-Csv -LiteralPath (Join-Path $assetsDir 'installpack-inventory.csv') -NoTypeInformation -Encoding UTF8
} finally {
    $pack.Dispose()
}

Write-Output "Base decodificado: $decodedBase"
Write-Output "Biblioteca: $nativePath"
Write-Output "Inventário InstallPack: $(Join-Path $assetsDir 'installpack-inventory.csv')"
