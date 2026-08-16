@echo off
setlocal

cd /d "%~dp0\.."

echo ==========================================
echo StockEventRadar v1.0.0-rc4.7.1 Windows Build
echo ==========================================
echo.
echo Large TEMP, Nuitka and pip build caches will use:
echo   D:\StockEventRadarBuild
echo.
echo This wrapper does NOT permanently change PowerShell execution policy.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_windows.ps1" %*

set EXITCODE=%ERRORLEVEL%

echo.
if not "%EXITCODE%"=="0" (
    echo Build exited with code %EXITCODE%.
) else (
    echo Build command finished successfully.
)

exit /b %EXITCODE%
