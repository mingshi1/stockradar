$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Exe = Join-Path $ProjectRoot "dist\StockEventRadar.exe"

if (-not (Test-Path $Exe)) {
    throw "Windows EXE does not exist: $Exe"
}

$Candidates = @()

$Command = Get-Command ISCC.exe -ErrorAction SilentlyContinue

if ($Command) {
    $Candidates += $Command.Source
}

$Candidates += @(
    "D:\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
)

$Iscc = $Candidates |
    Where-Object { $_ -and (Test-Path $_) } |
    Select-Object -First 1

if (-not $Iscc) {
    throw "Inno Setup 6 / ISCC.exe was not found."
}

Write-Host "Using Inno Setup:"
Write-Host "  $Iscc"

& $Iscc "installer\StockEventRadar.iss"

if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed with exit code $LASTEXITCODE"
}

$SetupExe = Join-Path $ProjectRoot "installer\output\StockEventRadar-Setup-1.0.0-rc4.27.exe"

if (-not (Test-Path $SetupExe)) {
    throw "Installer command completed but setup EXE was not found: $SetupExe"
}

Write-Host ""
Write-Host "Installer ready:"
Write-Host "  $SetupExe"
