[CmdletBinding()]
param(
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path.TrimEnd('\')
$ExpectedRoot = 'C:\Users\Thiago Aciole\Projetos\Jogos\Naruto Ultimate Ninja Storm'

if (-not $ProjectRoot.Equals($ExpectedRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Raiz inesperada. Esperado '$ExpectedRoot'; encontrado '$ProjectRoot'."
}

$OriginApk = Join-Path $ProjectRoot 'origin\Ultimate-Ninja-Storm-1.2.10.apk'
$FinalApk = Join-Path $ProjectRoot 'build\Naruto Ultimate Ninja Storm.apk'
$OldOriginalApk = Join-Path $ProjectRoot 'original\Naruto Ultimate Ninja Storm.apk'

if (-not (Test-Path -LiteralPath $OriginApk -PathType Leaf)) { throw "APK origin ausente: $OriginApk" }
if (-not (Test-Path -LiteralPath $FinalApk -PathType Leaf)) { throw "APK final ausente: $FinalApk" }
$finalHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $FinalApk).Hash
if ($finalHash -ne '5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86') {
    throw "Hash do APK final não confere; nada foi apagado. Hash encontrado: $finalHash"
}

# O candidato antigo duplicado deve ser o hash já identificado no inventário.
foreach ($oldApk in @($OldOriginalApk)) {
    if (Test-Path -LiteralPath $oldApk -PathType Leaf) {
        $oldHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $oldApk).Hash
        if ($oldHash -ne '717A253525F03E3F5D7FE308F7C3BDDDC1927B9A97B01BF5C0FBABB4375A2B3D') {
            throw "Hash inesperado em '$oldApk'; nada foi apagado. Hash encontrado: $oldHash"
        }
    }
}

$buildEntries = @(Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'build') -Force | ForEach-Object Name)
if ($buildEntries.Count -ne 1 -or $buildEntries[0] -ne [IO.Path]::GetFileName($FinalApk)) {
    throw 'build/ não contém exatamente o APK funcional; revise os itens antes da limpeza.'
}

$originalDir = Join-Path $ProjectRoot 'original'
if (Test-Path -LiteralPath $originalDir) {
    $originalEntries = @(Get-ChildItem -LiteralPath $originalDir -Force | ForEach-Object Name)
    if ($originalEntries.Count -ne 1 -or $originalEntries[0] -ne [IO.Path]::GetFileName($OldOriginalApk)) {
        throw 'Há conteúdo inesperado em original/; nada foi apagado.'
    }
}

$dirRel = @(
    'audity history',
    'original',
    'work\audit-history-evidence',
    'work\external-1.2.9',
    'work\original-redump',
    'work\s24-coverage'
)
$auditRoot = Join-Path $ProjectRoot 'audit'
for ($frame = 1; $frame -le 29; $frame++) {
    $framePath = Join-Path $auditRoot ('frame_{0:D3}.jpg' -f $frame)
    if (-not (Test-Path -LiteralPath $framePath -PathType Leaf)) {
        throw "Frame de referência ausente ($framePath); limpeza cancelada para preservar a análise widescreen."
    }
}

$dirTargets = @()
foreach ($relativePath in $dirRel) {
    $candidate = Join-Path $ProjectRoot $relativePath
    if (Test-Path -LiteralPath $candidate) {
        $resolved = (Resolve-Path -LiteralPath $candidate).Path
        if (-not $resolved.StartsWith("$ProjectRoot\", [StringComparison]::OrdinalIgnoreCase)) {
            throw "Alvo fora do projeto: $resolved"
        }
        $reparsePoints = Get-ChildItem -LiteralPath $resolved -Force -Recurse -Attributes ReparsePoint -ErrorAction SilentlyContinue
        if ($reparsePoints) { throw "Ponto de junção/link encontrado em '$resolved'; nada foi apagado." }
        $dirTargets += $resolved
    }
}

$workRoot = Join-Path $ProjectRoot 'work'
$workApks = @()
if (Test-Path -LiteralPath $workRoot) {
    $workApks = @(Get-ChildItem -LiteralPath $workRoot -Filter '*.apk' -File -Recurse -Force | ForEach-Object FullName)
}
foreach ($path in $workApks) {
    $resolved = (Resolve-Path -LiteralPath $path).Path
    if (-not $resolved.StartsWith("$workRoot\", [StringComparison]::OrdinalIgnoreCase)) {
        throw "APK fora de work/: $resolved"
    }
}
$auditDocs = @(
    'docs\BUILD_COMPARISON_20261024.md',
    'docs\ANDROID_WIDESCREEN_REMAINING.md',
    'docs\WIDESCREEN_TRANSFORM_AUDIT.md'
) | ForEach-Object { Join-Path $ProjectRoot $_ } | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf }

$plan = @($workApks) + @($auditDocs) + @($dirTargets)
$filesToCount = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($target in $plan) {
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        [void]$filesToCount.Add((Resolve-Path -LiteralPath $target).Path)
    } elseif (Test-Path -LiteralPath $target -PathType Container) {
        Get-ChildItem -LiteralPath $target -File -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
            [void]$filesToCount.Add($_.FullName)
        }
    }
}
$estimatedBytes = [long](($filesToCount | ForEach-Object { (Get-Item -LiteralPath $_).Length } | Measure-Object -Sum).Sum)

Write-Host "Projeto: $ProjectRoot"
Write-Host "Preservados: origin/Ultimate-Ninja-Storm-1.2.10.apk e build/$([IO.Path]::GetFileName($FinalApk))"
Write-Host "APK intermediários em work/: $($workApks.Count)"
Write-Host "Tamanho aproximado dos alvos: $([math]::Round($estimatedBytes / 1GB, 2)) GiB"
Write-Host 'Alvos:'
$plan | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" }

if (-not $Apply) {
    Write-Host "Prévia apenas. Confira a lista; para confirmar, rode novamente com -Apply."
    return
}

$answer = Read-Host 'Digite APAGAR para remover exatamente os alvos listados acima'
if ($answer -cne 'APAGAR') {
    Write-Host 'Cancelado; nenhum arquivo foi removido.'
    return
}

foreach ($path in $workApks) {
    if (Test-Path -LiteralPath $path -PathType Leaf) { Remove-Item -LiteralPath $path -Force }
}
foreach ($path in $auditDocs) {
    if (Test-Path -LiteralPath $path -PathType Leaf) { Remove-Item -LiteralPath $path -Force }
}
foreach ($path in $dirTargets) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force }
}

# Atualiza as notas de estado para não deixá-las afirmando que a limpeza está pendente.
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$readmePath = Join-Path $ProjectRoot 'README.md'
$readme = [IO.File]::ReadAllText($readmePath)
$readme = $readme.Replace('| `build/` | APK integrado aceito e um candidato anterior substituído; a remoção está pendente. |', '| `build/` | Somente o APK integrado aceito para uso no S24. |')
$readme = [regex]::Replace($readme, '(?m)^\| `original/` \| Cópia duplicada do candidato anterior substituído; a remoção está pendente\. \|\r?\n', '')
$auditRow = '| `audit/` | Frames de referência para análise visual widescreen; preservar. |'
if (-not $readme.Contains($auditRow)) {
    $readme = $readme.Replace('| `docs/` | Guias de uso, evidências, limites e histórico. |', "| ``docs/`` | Guias de uso, evidências, limites e histórico. |`r`n$auditRow")
}
$readme = $readme.Replace('| `work/` | Insumos de extração, patch e assinatura, além de APKs de teste e auditorias antigas; limpeza pendente. |', '| `work/` | Insumos temporários de extração, patch e assinatura; APKs de teste e conjuntos antigos de auditoria foram removidos. |')
$readme = $readme.Replace('A organização desejada é manter somente a entrada em `origin/` e a saída aceita em `build/`; a revisão automática bloqueou a exclusão dos artefatos antigos nesta execução.', 'Os únicos APKs mantidos são a entrada em `origin/` e a saída aceita em `build/`. APKs de teste e candidatos antigos foram removidos de `work/`.')
[IO.File]::WriteAllText($readmePath, $readme, $utf8NoBom)

$historyReadmePath = Join-Path $ProjectRoot 'docs\history\README.md'
$historyReadme = [IO.File]::ReadAllText($historyReadmePath)
$historyReadme = $historyReadme.Replace('Em 26/10/2026, foi mapeada a remoção dos APKs históricos/intermediários e dos dados de auditoria descartáveis. A exclusão foi bloqueada pela revisão automática; os arquivos continuam no projeto. Os relatórios textuais desta pasta permanecem como registro histórico.', 'Em 26/10/2026, os APKs históricos/intermediários e os dados de auditoria descartáveis foram removidos. Os relatórios textuais desta pasta permanecem como registro histórico e não reconstroem os artefatos removidos.')
[IO.File]::WriteAllText($historyReadmePath, $historyReadme, $utf8NoBom)

$exynosPath = Join-Path $ProjectRoot 'docs\EXYNOS_FIX.md'
$exynos = [IO.File]::ReadAllText($exynosPath)
$exynos = $exynos.Replace('Os binários antigos da 1.2.9 e das análises anteriores ainda estão no disco; a revisão automática bloqueou sua remoção nesta execução.', 'Os binários antigos da 1.2.9 e das análises anteriores foram removidos; esta documentação preserva o registro técnico histórico.')
[IO.File]::WriteAllText($exynosPath, $exynos, $utf8NoBom)

$remainingWorkApks = @(Get-ChildItem -LiteralPath $workRoot -Filter '*.apk' -File -Recurse -Force -ErrorAction SilentlyContinue)
$remainingBuildApks = @(Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'build') -Filter '*.apk' -File -Force)
$remainingOriginApks = @(Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'origin') -Filter '*.apk' -File -Force)
if ($remainingWorkApks.Count -ne 0) { throw "Restaram $($remainingWorkApks.Count) APK(s) em work/. Revise manualmente." }
if ($remainingBuildApks.Count -ne 1 -or $remainingBuildApks[0].FullName -ne $FinalApk) { throw 'Conteúdo inesperado em build/. Revise manualmente.' }
if ($remainingOriginApks.Count -ne 1 -or $remainingOriginApks[0].FullName -ne $OriginApk) { throw 'Conteúdo inesperado em origin/. Revise manualmente.' }
if (-not (Test-Path -LiteralPath $auditRoot -PathType Container)) { throw 'A pasta audit/ deveria ter sido preservada.' }
for ($frame = 1; $frame -le 29; $frame++) {
    $framePath = Join-Path $auditRoot ('frame_{0:D3}.jpg' -f $frame)
    if (-not (Test-Path -LiteralPath $framePath -PathType Leaf)) { throw "Frame removido inesperadamente: $framePath" }
}

Write-Host 'Limpeza concluída. origin/ e build/ contêm somente os APKs preservados.'
