@echo off
REM Tunnel relay launcher - silent, no popups
REM Requires: node, cloudflared.exe in same folder (auto-downloaded)
REM Set SLC_RELAY_SECRET env var before running for write auth.

set SCRIPT_DIR=%~dp0
set CF_EXE=%SCRIPT_DIR%cloudflared.exe

REM Download cloudflared binary if missing
if not exist "%CF_EXE%" (
    echo Downloading cloudflared binary...
    powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CF_EXE%'"
    timeout /t 6 /nobreak >nul
)

REM Kill any stale instances
taskkill /f /im cloudflared.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM Start watchdog (auto-restarts node on crash), hidden
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process cmd -ArgumentList '/c %SCRIPT_DIR%watchdog.bat' -WindowStyle Hidden"
timeout /t 2 /nobreak >nul

REM Start cloudflared tunnel, capture URL
del /q "%SCRIPT_DIR%tunnel_url.txt" >nul 2>&1
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process '%CF_EXE%' -ArgumentList 'tunnel --url http://127.0.0.1:8080' -WindowStyle Hidden -RedirectStandardOutput '%SCRIPT_DIR%tunnel_url.txt' -RedirectStandardError '%SCRIPT_DIR%tunnel_url.txt'"

echo Waiting for tunnel URL...
timeout /t 10 /nobreak >nul
type "%SCRIPT_DIR%tunnel_url.txt" | findstr trycloudflare
echo.
echo Full log: %SCRIPT_DIR%tunnel_url.txt
echo Set SLC_RELAY_SECRET env var to require auth on /write.
pause
