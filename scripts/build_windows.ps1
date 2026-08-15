param(
    [switch]$SkipInstaller,
    [switch]$SkipDependencyInstall,
    [string]$BuildRoot = "D:\StockEventRadarBuild"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=========================================="
Write-Host " StockEventRadar v1.0.0-rc4 Windows Build"
Write-Host "=========================================="
Write-Host ""

$TempDir = Join-Path $BuildRoot "temp"
$NuitkaCacheDir = Join-Path $BuildRoot "nuitka-cache"
$PipCacheDir = Join-Path $BuildRoot "pip-cache"

New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
New-Item -ItemType Directory -Force -Path $NuitkaCacheDir | Out-Null
New-Item -ItemType Directory -Force -Path $PipCacheDir | Out-Null

$env:TEMP = $TempDir
$env:TMP = $TempDir
$env:TMPDIR = $TempDir
$env:NUITKA_CACHE_DIR = $NuitkaCacheDir
$env:PIP_CACHE_DIR = $PipCacheDir

Write-Host "Build workspace:"
Write-Host "  $BuildRoot"
Write-Host "TEMP / TMP:"
Write-Host "  $TempDir"
Write-Host "Nuitka cache:"
Write-Host "  $NuitkaCacheDir"
Write-Host "pip cache:"
Write-Host "  $PipCacheDir"
Write-Host ""

if (-not $SkipDependencyInstall) {
    Write-Host "[0/4] Installing deterministic build dependencies..."
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-build.txt
}

Write-Host "Python:"
python -c "import sys; print(sys.executable); print(sys.version)"
Write-Host "PySide6:"
python -c "import PySide6, PySide6.QtCore; print(PySide6.__version__); print(PySide6.__file__); print('Qt', PySide6.QtCore.__version__)"
Write-Host "Nuitka:"
python -m nuitka --version

$DistDir = Join-Path $ProjectRoot "dist"
$DeploymentDir = Join-Path $ProjectRoot "deployment"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null
New-Item -ItemType Directory -Force -Path $DeploymentDir | Out-Null

$Exe = Join-Path $DistDir "StockEventRadar.exe"

if (Test-Path $Exe) {
    Remove-Item $Exe -Force
}

if (Test-Path "pysidedeploy.spec") {
    Remove-Item "pysidedeploy.spec" -Force
}

Write-Host "[1/4] Creating deployment spec..."
pyside6-deploy main.py --init --name StockEventRadar -f

if ($LASTEXITCODE -ne 0) {
    throw "pyside6-deploy --init failed with exit code $LASTEXITCODE"
}

Write-Host "[2/4] Configuring deployment..."
python scripts/configure_deploy.py

if ($LASTEXITCODE -ne 0) {
    throw "configure_deploy.py failed with exit code $LASTEXITCODE"
}

Write-Host "[3/4] Building EXE with pyside6-deploy / Nuitka..."
pyside6-deploy -c pysidedeploy.spec -f

if ($LASTEXITCODE -ne 0) {
    Write-Error "pyside6-deploy failed with exit code $LASTEXITCODE. See the Nuitka output above and deployment\nuitka-report.xml when available."
}

if (-not (Test-Path $Exe)) {
    $FallbackExe = Join-Path $DeploymentDir "main.exe"

    if (Test-Path $FallbackExe) {
        Write-Warning "pyside6-deploy did not complete the final copy."
        Write-Host "Recovering compiled EXE from:"
        Write-Host "  $FallbackExe"

        Copy-Item $FallbackExe $Exe -Force
    }
}

if (-not (Test-Path $Exe)) {
    Write-Error "Build finished but $Exe was not found."
}

Write-Host ""
Write-Host "EXE ready:"
Write-Host "  $Exe"
Write-Host ""

if ($SkipInstaller) {
    exit 0
}

Write-Host "[4/4] Building installer..."
& "$PSScriptRoot\build_installer.ps1"
