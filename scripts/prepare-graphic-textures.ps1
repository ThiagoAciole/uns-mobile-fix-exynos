param(
    [Parameter(Mandatory=$true)][string]$GeneratedDirectory,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent
$generated = (Resolve-Path -LiteralPath $GeneratedDirectory).Path
$output = [System.IO.Path]::GetFullPath((Join-Path $root $OutputDirectory))
if (Test-Path -LiteralPath $output) { throw "Output already exists: $output" }
New-Item -ItemType Directory -Path $output | Out-Null

$items = @(
    @{ Name='mission'; Generated='mission-full.png'; Original='work\graphic-ptbr\mode-original\xmode_fd_mission00.png'; File='xmode_fd_mission00.png'; MaxWidth=1090; MaxHeight=625; Left=32; Top=24; PreservePatch=$true },
    @{ Name='battle'; Generated='battle-full.png'; Original='work\graphic-ptbr\mode-original\xmode_fd_battle00.png'; File='xmode_fd_battle00.png'; MaxWidth=1090; MaxHeight=625; Left=32; Top=24; PreservePatch=$true },
    @{ Name='option'; Generated='option-full.png'; Original='work\graphic-ptbr\mode-original\xmode_fd_option00.png'; File='xmode_fd_option00.png'; MaxWidth=1090; MaxHeight=625; Left=32; Top=24; PreservePatch=$true },
    @{ Name='tap'; Generated='tap.png'; Original='work\graphic-ptbr\title-original\xtitle_fd01.png'; File='xtitle_fd01.png'; MaxWidth=982; MaxHeight=90; Left=5; Top=10; PreservePatch=$false },
    @{ Name='mode-select'; Generated='mode-select.png'; Original='work\graphic-ptbr\index-mode-original\mode_indexname_fd.png'; File='mode_indexname_fd.png'; MaxWidth=750; MaxHeight=84; Left=8; Top=6; PreservePatch=$false },
    @{ Name='option-index-android'; Generated='option-index-android.png'; Original='work\graphic-ptbr\index-option-original\option_indexname_fd.png'; File='option_indexname_fd_android.png'; MaxWidth=768; MaxHeight=576; Left=0; Top=0; PreservePatch=$false; ClearRows=6 },
    @{ Name='option-index-nonandroid'; Generated='option-index-nonandroid.png'; Original='work\graphic-ptbr\index-option-nonandroid-original\option_indexname_fd.png'; File='option_indexname_fd_nonandroid.png'; MaxWidth=768; MaxHeight=384; Left=0; Top=0; PreservePatch=$false; ClearRows=3 }
)
$report = @()
foreach ($item in $items) {
    $sourcePath = Join-Path $generated $item.Generated
    $originalPath = Join-Path $root $item.Original
    $targetPath = Join-Path $output $item.File
    foreach ($path in @($sourcePath, $originalPath)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing image: $path" }
    }

    $source = [System.Drawing.Bitmap]::FromFile($sourcePath)
    $original = [System.Drawing.Bitmap]::FromFile($originalPath)
    $target = $null
    try {
        $bounds = [System.Drawing.Rectangle]::Empty
        for ($y=0; $y -lt $source.Height; $y++) {
            for ($x=0; $x -lt $source.Width; $x++) {
                if ($source.GetPixel($x,$y).A -gt 8) {
                    if ($bounds.IsEmpty) { $bounds = [System.Drawing.Rectangle]::new($x,$y,1,1) }
                    else { $bounds = [System.Drawing.Rectangle]::FromLTRB([Math]::Min($bounds.Left,$x),[Math]::Min($bounds.Top,$y),[Math]::Max($bounds.Right,$x+1),[Math]::Max($bounds.Bottom,$y+1)) }
                }
            }
        }
        if ($bounds.IsEmpty) { throw "No visible pixels in $sourcePath" }
        $scale = [Math]::Min($item.MaxWidth / [double]$bounds.Width, $item.MaxHeight / [double]$bounds.Height)
        $width = [Math]::Max(1,[int][Math]::Round($bounds.Width*$scale))
        $height = [Math]::Max(1,[int][Math]::Round($bounds.Height*$scale))
        $canvasWidth, $canvasHeight = $original.Width, $original.Height
        if ($item.ClearRows) { $target = $original.Clone([System.Drawing.Rectangle]::new(0,0,$canvasWidth,$canvasHeight),[System.Drawing.Imaging.PixelFormat]::Format32bppArgb) }
        else { $target = [System.Drawing.Bitmap]::new($canvasWidth,$canvasHeight,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb) }
        $graphics = [System.Drawing.Graphics]::FromImage($target)
        try {
            if (-not $item.ClearRows) { $graphics.Clear([System.Drawing.Color]::Transparent) }
            if ($item.ClearRows) {
                $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
                $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::Transparent)
                try { for ($row=0; $row -lt $item.ClearRows; $row++) { $graphics.FillRectangle($brush,0,$row*96,$canvasWidth,96) } }
                finally { $brush.Dispose() }
            }
            $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceOver
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $left = [int](($canvasWidth-$width)/2)
            if ($item.PreservePatch) { $left = [int]((1536*0.7578125-$width)/2) }
            if ($item.Name -eq 'mode-select') { $left = $item.Left }
            $top = [int](($canvasHeight-$height)/2)
            if ($item.Left -gt 0 -or $item.Top -gt 0) { $left = $item.Left; $top = $item.Top }
            $dest = [System.Drawing.Rectangle]::new($left,$top,$width,$height)
            $graphics.DrawImage($source,$dest,$bounds,[System.Drawing.GraphicsUnit]::Pixel)
            if ($item.PreservePatch) {
                # The model's second UV set samples this color patch as a material constant.
                for ($y=728; $y -lt 736; $y++) { for ($x=1488; $x -lt 1496; $x++) {
                    $target.SetPixel($x,$y,$original.GetPixel($x,$y))
                } }
            }
        } finally { $graphics.Dispose() }
        $target.Save($targetPath,[System.Drawing.Imaging.ImageFormat]::Png)
        if ($target.Width -ne $original.Width -or $target.Height -ne $original.Height) { throw "Canvas dimensions changed: $($item.File)" }
        if ($item.PreservePatch) {
            for ($y=728; $y -lt 736; $y++) { for ($x=1488; $x -lt 1496; $x++) {
                if ($target.GetPixel($x,$y).ToArgb() -ne $original.GetPixel($x,$y).ToArgb()) { throw "UV patch changed: $($item.File)" }
            } }
        }
        $report += [pscustomobject]@{ name=$item.Name; source=$item.Generated; file=$item.File; canvas="$canvasWidth`x$canvasHeight"; visibleBox="$left,$top,$width,$height"; uvPatchPreserved=$item.PreservePatch }
    } finally {
        if ($null -ne $target) { $target.Dispose() }
        $source.Dispose(); $original.Dispose()
    }
}
$report | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding UTF8
$report | Format-Table -AutoSize
