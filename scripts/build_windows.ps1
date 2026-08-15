param(
    [switch]$SkipInstaller,
    [string]$BuildRoot = "D:\StockEventRadarBuild"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=========================================="
Write-Host " StockEventRadar v1.0.0-rc3 Windows Build"
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

python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt

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

Write-Host "[2/4] Configuring deployment..."
python scripts/configure_deploy.py

Write-Host "[3/4] Building EXE with pyside6-deploy / Nuitka..."
pyside6-deploy -c pysidedeploy.spec -f

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

Write-Host "[4/4] Looking for Inno Setup..."

$IsccCandidates = @(
    "D:\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
)

$Iscc = $null

foreach ($Candidate in $IsccCandidates) {
    if (Test-Path $Candidate) {
        $Iscc = $Candidate
        break
    }
}

if (-not $Iscc) {
    Write-Warning "Inno Setup 6 was not found."
    Write-Warning "The EXE was built successfully."
    Write-Warning "Install Inno Setup 6 and rerun to create Setup.exe."
    exit 0
}

& $Iscc "installer\StockEventRadar.iss"

Write-Host ""
Write-Host "Installer build complete."
