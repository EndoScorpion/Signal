@echo off
REM Tunnel relay launcher - silent, no popups
REM Uses cloudflared binary directly (NOT npx)

set SCRIPT_DIR=%~dp0
set CF_EXE=%SCRIPT_DIR%cloudflared.exe

REM Step 1: Download cloudflared binary if missing
if not exist "%CF_EXE%" (
    echo Downloading cloudflared...
    powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CF_EXE%'"
    timeout /t 5 /nobreak >nul
)

REM Step 2: Start Node.js blackboard server hidden
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process node -ArgumentList '%SCRIPT_DIR%server.js' -WindowStyle Hidden"
timeout /t 2 /nobreak >nul

REM Step 3: Start cloudflared tunnel hidden, capture URL
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process '%CF_EXE%' -ArgumentList 'tunnel --url http://127.0.0.1:8080' -WindowStyle Hidden -RedirectStandardOutput '%SCRIPT_DIR%tunnel_url.txt' -RedirectStandardError '%SCRIPT_DIR%tunnel_url.txt'"

echo Relay started. Waiting for URL...
timeout /t 8 /nobreak >nul
type "%SCRIPT_DIR%tunnel_url.txt" | findstr trycloudflare
echo.
echo Full log: %SCRIPT_DIR%tunnel_url.txt
pause
