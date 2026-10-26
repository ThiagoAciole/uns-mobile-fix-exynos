param(
    [Parameter(Mandatory=$true)][string]$ApkPath,
    [string]$OutputPath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'output\naruto-storm-mod.apk'),
    [string]$KeystorePath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'work\keys\personal-mod.jks'),
    [string]$Alias = 'personal-mod'
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Sdk = if ($env:ANDROID_SDK_ROOT) { $env:ANDROID_SDK_ROOT } elseif ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$BuildTools = Get-ChildItem -LiteralPath (Join-Path $Sdk 'build-tools') -Directory | Sort-Object { try { [version]$_.Name } catch { [version]'0.0' } } -Descending | Select-Object -First 1
if (-not $BuildTools) { throw "Android Build Tools não encontrados em $Sdk" }
$Align = Join-Path $BuildTools.FullName 'zipalign.exe'
$Signer = Join-Path $BuildTools.FullName 'apksigner.bat'
if (-not (Test-Path $Align) -or -not (Test-Path $Signer)) { throw 'zipalign/apksigner não encontrados no Android Build Tools.' }
if (-not (Test-Path -LiteralPath $ApkPath -PathType Leaf)) { throw "APK unsigned não encontrado: $ApkPath" }
$ApkPath = (Resolve-Path -LiteralPath $ApkPath).Path
New-Item -ItemType Directory -Force -Path (Split-Path $OutputPath),(Split-Path $KeystorePath) | Out-Null
$SecurePassword = Read-Host 'Senha local do keystore (será pedida novamente em futuras assinaturas)' -AsSecureString
$Ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)
try { $Password = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ptr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr) }
$env:STORM_SIGNING_PASSWORD = $Password
try {
    if (-not (Test-Path -LiteralPath $KeystorePath)) {
        & keytool -genkeypair -keystore $KeystorePath -storepass:env STORM_SIGNING_PASSWORD -keypass:env STORM_SIGNING_PASSWORD -alias $Alias -keyalg RSA -keysize 3072 -validity 10000 -dname 'CN=Personal Android Mod,O=Local' -noprompt
        if ($LASTEXITCODE -ne 0) { throw "keytool falhou: $LASTEXITCODE" }
    }
    $Aligned = Join-Path $Root 'work\aligned.apk'
    & $Align -f -P 16 4 $ApkPath $Aligned
    if ($LASTEXITCODE -ne 0) { throw "zipalign falhou: $LASTEXITCODE" }
    & $Signer sign --ks $KeystorePath --ks-key-alias $Alias --ks-pass env:STORM_SIGNING_PASSWORD --key-pass env:STORM_SIGNING_PASSWORD --out $OutputPath $Aligned
    if ($LASTEXITCODE -ne 0) { throw "apksigner falhou: $LASTEXITCODE" }
    & $Signer verify --verbose $OutputPath
    if ($LASTEXITCODE -ne 0) { throw 'A verificação da assinatura falhou.' }
} finally { Remove-Item Env:\STORM_SIGNING_PASSWORD -ErrorAction SilentlyContinue; $Password = $null }
Write-Host "APK alinhado e assinado: $OutputPath"
