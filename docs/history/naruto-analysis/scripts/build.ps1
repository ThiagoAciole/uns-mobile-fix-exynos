param([string]$DecodedPath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'work\decoded'))
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Jar = Get-ChildItem -LiteralPath (Join-Path $Root 'work\tools') -File -Filter 'apktool*.jar' | Sort-Object Name -Descending | Select-Object -First 1
if (-not $Jar) { throw 'Apktool ausente. Coloque apktool*.jar em work\tools.' }
if (-not (Test-Path -LiteralPath (Join-Path $DecodedPath 'apktool.yml'))) { throw "Diretório Apktool inválido: $DecodedPath" }
$DecodedPath = (Resolve-Path -LiteralPath $DecodedPath).Path
$Unsigned = Join-Path $Root 'output\naruto-storm-mod-unsigned.apk'
New-Item -ItemType Directory -Force -Path (Split-Path $Unsigned) | Out-Null
Push-Location $Root
try { & java -jar $Jar.FullName b $DecodedPath -o $Unsigned; if ($LASTEXITCODE -ne 0) { throw "Apktool build falhou: $LASTEXITCODE" } }
finally { Pop-Location }
& (Join-Path $PSScriptRoot 'sign.ps1') -ApkPath $Unsigned
