param(
    [string]$BuildRoot = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not $BuildRoot) {
    if ($env:RUNNER_TEMP) {
        $BuildRoot = Join-Path $env:RUNNER_TEMP "StockEventRadarBuild"
    } else {
        $BuildRoot = "D:\StockEventRadarBuild"
    }
}

Write-Host "=== GitHub/CI Windows preflight ==="
Write-Host "Project: $ProjectRoot"
Write-Host "BuildRoot: $BuildRoot"

$VsWhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {
    throw "vswhere.exe was not found. Visual Studio Build Tools/MSVC are required."
}

$VsPath = & $VsWhere `
    -latest `
    -products * `
    -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
    -property installationPath

if (-not $VsPath) {
    throw "Visual Studio installation with VC x64 tools was not found."
}

$DevCmd = Join-Path $VsPath "Common7\Tools\VsDevCmd.bat"

if (-not (Test-Path $DevCmd)) {
    throw "VsDevCmd.bat was not found at: $DevCmd"
}

Write-Host "Visual Studio:"
Write-Host "  $VsPath"
Write-Host "Loading MSVC environment from:"
Write-Host "  $DevCmd"

# Capture the environment produced by VsDevCmd.bat into this PowerShell process.
$EnvLines = & cmd.exe /d /s /c "`"$DevCmd`" -no_logo -arch=x64 -host_arch=x64 && set"

if ($LASTEXITCODE -ne 0) {
    throw "VsDevCmd.bat failed with exit code $LASTEXITCODE"
}

foreach ($Line in $EnvLines) {
    if ($Line -match '^([^=]+)=(.*)$') {
        $Name = $matches[1]
        $Value = $matches[2]

        [Environment]::SetEnvironmentVariable(
            $Name,
            $Value,
            "Process"
        )
    }
}

Write-Host ""
Write-Host "Compiler diagnostics:"
$Cl = Get-Command cl.exe -ErrorAction SilentlyContinue
$Dumpbin = Get-Command dumpbin.exe -ErrorAction SilentlyContinue

if (-not $Cl) {
    throw "cl.exe is still not on PATH after loading VsDevCmd.bat"
}

if (-not $Dumpbin) {
    throw "dumpbin.exe is still not on PATH after loading VsDevCmd.bat"
}

Write-Host "cl.exe:"
Write-Host "  $($Cl.Source)"
Write-Host "dumpbin.exe:"
Write-Host "  $($Dumpbin.Source)"

Write-Host ""
Write-Host "Python/PySide/Nuitka diagnostics:"
python -c "import sys; print('Python executable:', sys.executable); print(sys.version)"
python -c "import PySide6, PySide6.QtCore; print('PySide6:', PySide6.__version__); print('Qt:', PySide6.QtCore.__version__); print('PySide6 path:', PySide6.__file__)"
python -m nuitka --version

Write-Host ""
Write-Host "Starting actual Windows build..."

& "$PSScriptRoot\build_windows.ps1" `
    -SkipInstaller `
    -SkipDependencyInstall `
    -BuildRoot $BuildRoot

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
