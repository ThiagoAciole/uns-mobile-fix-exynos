[CmdletBinding()]
param(
    [string]$InputLibrary = 'work\native\libultimateninjastorm.so',
    [string]$OutputLibrary,
    [switch]$Reverse
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not $OutputLibrary) {
    $OutputLibrary = if ($Reverse) { 'work\native\exynos-depth-restored\libultimateninjastorm.so' }
                     else { 'work\native\exynos-depth-d32s8\libultimateninjastorm.so' }
}
$source = [IO.Path]::GetFullPath((Join-Path $root $InputLibrary))
$destination = [IO.Path]::GetFullPath((Join-Path $root $OutputLibrary))
$originalRoot = [IO.Path]::GetFullPath((Join-Path $root 'original')) + [IO.Path]::DirectorySeparatorChar
if ($source -eq $destination -or $destination.StartsWith($originalRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'O patch exige uma saída separada fora de original/.'
}
$manifest = $destination + '.patch.json'
foreach ($path in @($destination, $manifest)) {
    if (Test-Path -LiteralPath $path) { throw "Saída já existe; preservada: $path" }
}
$bytes = [IO.File]::ReadAllBytes($source)
if ($bytes.Length -lt 0x328 -or [BitConverter]::ToString($bytes, 0, 6) -ne '7F-45-4C-46-02-01') {
    throw 'Esperado ELF64 little-endian do jogo.'
}
$buildId = [BitConverter]::ToString($bytes, 0x318, 16).Replace('-', '').ToLowerInvariant()
$offsets = @{
    'c3e506f9be350dfb4a00c79228754028' = 0x6bf964
    'd6c3c1ca40aa936ceb5b585da96f4a4a' = 0x6c6164
}
if (-not $offsets.ContainsKey($buildId)) { throw "Build ID incompatível: $buildId" }
# Nos dois ELF verificados, o primeiro PT_LOAD tem VMA=offset.
$offset = $offsets[$buildId]
if ($bytes.Length -lt $offset + 4) { throw 'Tabela fora dos limites do ELF.' }
$before = if ($Reverse) { 130 } else { 129 }
$after = if ($Reverse) { 129 } else { 130 }
if ([BitConverter]::ToUInt32($bytes, $offset) -ne $before) {
    throw ('Entrada da tabela inesperada em 0x{0:x}; esperado {1}.' -f $offset, $before)
}
$sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
[Array]::Copy([BitConverter]::GetBytes([uint32]$after), 0, $bytes, $offset, 4)
$sha = [Security.Cryptography.SHA256]::Create()
try { $expectedHash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '') }
finally { $sha.Dispose() }
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($destination)) | Out-Null
[IO.File]::WriteAllBytes($destination, $bytes)
$outputHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
if ($outputHash -ne $expectedHash) { throw 'A verificação da saída gravada falhou.' }
if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $sourceHash) {
    throw 'A origem mudou durante a operação.'
}
[ordered]@{
    status = 'diagnostic-only-not-game-validated'
    buildId = $buildId
    source = $source
    destination = $destination
    sourceSha256 = $sourceHash
    outputSha256 = $outputHash
    fileOffset = ('0x{0:x}' -f $offset)
    ghidraAddress = ('0x{0:x}' -f ($offset + 0x100000))
    tableIndex = 15
    oldVkFormat = $before
    newVkFormat = $after
    reverse = [bool]$Reverse
    limit = 'Global mapping change; logical bits-per-pixel stays 32. Requires full game validation.'
} | ConvertTo-Json | Set-Content -LiteralPath $manifest -Encoding UTF8
Write-Output "Candidato diagnóstico gravado e verificado: $destination"
