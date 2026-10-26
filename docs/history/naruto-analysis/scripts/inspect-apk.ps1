param(
    [Parameter(Mandatory = $true)]
    [string]$Apk
)

$ErrorActionPreference = 'Stop'
$Apk = (Resolve-Path -LiteralPath $Apk).Path
$sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$buildTools = Get-ChildItem -LiteralPath (Join-Path $sdk 'build-tools') -Directory |
    Sort-Object { [version]$_.Name } -Descending |
    Select-Object -First 1
if (-not $buildTools) { throw "Android build-tools não encontrados em $sdk" }

$aapt = Join-Path $buildTools.FullName 'aapt.exe'
$apksigner = Join-Path $buildTools.FullName 'apksigner.bat'
if (-not (Test-Path -LiteralPath $aapt) -or -not (Test-Path -LiteralPath $apksigner)) {
    throw "aapt/apksigner não encontrados em $($buildTools.FullName)"
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($Apk)
try {
    $entries = @($archive.Entries)
    [pscustomobject]@{
        Path = $Apk
        Bytes = (Get-Item -LiteralPath $Apk).Length
        SHA256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Apk).Hash
        EntryCount = $entries.Count
        NativeLibraries = (($entries | Where-Object FullName -Like 'lib/*.so' | ForEach-Object FullName) -join ', ')
        OBBEntries = (($entries | Where-Object FullName -Like '*.obb' | ForEach-Object FullName) -join ', ')
    } | Format-List
}
finally {
    $archive.Dispose()
}

& $aapt dump badging $Apk |
    Select-String "^(package:|sdkVersion:|targetSdkVersion:|native-code:|launchable-activity:)"
& $apksigner verify --verbose --print-certs $Apk |
    Select-String '^(Verifies|Verified using|Number of signers:|Signer #1 certificate DN:|Signer #1 certificate SHA-256 digest:)'
