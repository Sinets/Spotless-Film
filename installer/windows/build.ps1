# Build Spotless Film Windows executable (PyInstaller) and optional Inno Setup installer.
# Run in PowerShell on Windows from repo root:  .\installer\windows\build.ps1
# Prerequisites: Python 3.9+ on PATH, (optional) Inno Setup 6 for .exe setup.

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Src = Join-Path $RepoRoot "src"

Set-Location $Src
try {
    Write-Host "Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
    python -m pip install -r requirements_spotless_film.txt
    # CPU wheel keeps CI and default dev builds smaller; replace with CUDA index if needed.
    python -m pip install torch torchvision --index-url "https://download.pytorch.org/whl/cpu"

    if (-not (Test-Path "weights")) {
        Write-Warning "No src\weights folder: add .pth files before build for a working U-Net."
    }

    Write-Host "Running PyInstaller..."
    pyinstaller --clean --noconfirm spotless_film.spec
} finally {
    Set-Location $RepoRoot
}

$exePath = Join-Path $Src "dist\SpotlessFilm.exe"
if (-not (Test-Path $exePath)) {
    throw "Expected executable missing: $exePath"
}
Write-Host "Built: $exePath"

$isccCandidates = @(
    Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
    Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"
)
$iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
$iss = Join-Path $RepoRoot "installer\windows\SpotlessFilm.iss"

if ($iscc) {
    Write-Host "Compiling installer with Inno Setup..."
    & $iscc $iss
    $outDir = Join-Path $RepoRoot "installer\windows\Output"
    Get-ChildItem $outDir -Filter "Spotless-Film-*-Setup*.exe" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "Installer: $($_.FullName)"
    }
} else {
    Write-Warning "Inno Setup 6 (ISCC.exe) not found. Install from https://jrsoftware.org/isdl.php to produce a setup .exe, or ship dist\SpotlessFilm.exe as a portable build."
}
