@echo off
setlocal

cd /d "%~dp0\.."

echo Running safe build-cache cleanup...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0cleanup_c_build_cache.ps1"

exit /b %ERRORLEVEL%
