$ErrorActionPreference = "Continue"

Write-Host "=========================================="
Write-Host " StockEventRadar C-drive Build Cache Cleanup"
Write-Host "=========================================="
Write-Host ""
Write-Host "This cleans build/download caches only."
Write-Host "It does NOT delete:"
Write-Host "  %APPDATA%\StockEventRadar\stockradar.db"
Write-Host "  your source code"
Write-Host "  your API keys"
Write-Host ""

Write-Host "[1/3] Current pip cache:"
python -m pip cache info

Write-Host ""
Write-Host "[2/3] Cleaning the CURRENT/default Nuitka caches..."
python -m nuitka --clean-cache=all

Write-Host ""
Write-Host "[3/3] Purging pip download/wheel cache..."
python -m pip cache purge

Write-Host ""
Write-Host "Known build caches have been cleaned."
Write-Host ""
Write-Host "For safety this script does NOT wipe the whole Windows TEMP directory."
Write-Host "Current TEMP:"
Write-Host "  $env:TEMP"
