param([string]$ApkPath)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if (-not $ApkPath) {
    $Apks = @(Get-ChildItem -LiteralPath $Root -File -Filter '*.apk')
    if ($Apks.Count -ne 1) { throw "Esperado exatamente 1 APK na raiz; encontrados: $($Apks.Count). Informe -ApkPath." }
    $ApkPath = $Apks[0].FullName
}
if (-not (Test-Path -LiteralPath $ApkPath -PathType Leaf)) { throw "APK não encontrado: $ApkPath" }
$ApkPath = (Resolve-Path -LiteralPath $ApkPath).Path
$Jar = Get-ChildItem -LiteralPath (Join-Path $Root 'work\tools') -File -Filter 'apktool*.jar' | Sort-Object Name -Descending | Select-Object -First 1
if (-not $Jar) { throw 'Apktool ausente. Coloque apktool*.jar em work\tools.' }
$Decoded = Join-Path $Root 'work\decoded'
New-Item -ItemType Directory -Force -Path (Split-Path $Decoded) | Out-Null
Push-Location $Root
try { & java -jar $Jar.FullName d $ApkPath -o $Decoded -f; if ($LASTEXITCODE -ne 0) { throw "Apktool falhou: $LASTEXITCODE" } }
finally { Pop-Location }
Write-Host "Extraído em $Decoded"
