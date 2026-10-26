[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'work\decoded\base'
$candidate = Join-Path $root 'work\decoded\exynos-diagnostic'
$outputDir = Join-Path $root 'work\native'
$output = Join-Path $outputDir 'exynos-diagnostic-base-unsigned.apk'
$smali = Join-Path $candidate 'smali\com\bandainamcoent\ultimateninjastorm\MainActivity.smali'

if (-not (Test-Path -LiteralPath (Join-Path $source 'apktool.yml') -PathType Leaf)) {
    throw "Base Apktool ausente ou incompleto: $source"
}
if (Test-Path -LiteralPath $candidate) {
    throw "A pasta de candidato já existe; revise ou remova a cópia manualmente: $candidate"
}
if (Test-Path -LiteralPath $output) {
    throw "O APK de saída já existe; preserve-o e escolha outro fluxo: $output"
}

$apktool = Get-Command apktool -ErrorAction Stop
Copy-Item -LiteralPath $source -Destination $candidate -Recurse
if (-not (Test-Path -LiteralPath $smali -PathType Leaf)) {
    throw "MainActivity.smali ausente no candidato: $smali"
}

$content = [IO.File]::ReadAllText($smali)
$pattern = '(?s)    const/4 p1, 0x0\r?\n.*?    invoke-static \{p0, v1, v2\}, Landroidx/core/app/ActivityCompat;->requestPermissions\(Landroid/app/Activity;\[Ljava/lang/String;I\)V\r?\n'
$matches = [regex]::Matches($content, $pattern)
if ($matches.Count -ne 1) {
    throw "Esperava exatamente um bloco de pedido de permissões; encontrei $($matches.Count). Nenhuma alteração aplicada."
}

$patched = [regex]::Replace($content, $pattern, '', 1)
[IO.File]::WriteAllText($smali, $patched, [Text.UTF8Encoding]::new($false))
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
& $apktool.Source b $candidate -o $output
if ($LASTEXITCODE -ne 0) { throw "Apktool falhou com código $LASTEXITCODE" }
if (-not (Test-Path -LiteralPath $output -PathType Leaf)) { throw "APK de saída não foi criado: $output" }

Write-Output "Candidato diagnóstico (não assinado): $output"
Write-Output 'Mudança: removida somente a chamada ActivityCompat.requestPermissions de MainActivity.onCreate.'
Write-Output 'O base decodificado original e os cinco APKs em original/ não foram alterados.'
