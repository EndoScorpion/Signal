@echo off
REM Tunnel relay launcher - silent, no popups
REM Uses cloudflared binary directly (NOT npx)

set SCRIPT_DIR=%~dp0
set CF_EXE=%SCRIPT_DIR%cloudflared.exe

REM Download cloudflared binary if missing
if not exist "%CF_EXE%" (
    echo Downloading cloudflared...
    powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CF_EXE%'"
    timeout /t 5 /nobreak >nul
)

REM Kill any existing instances first
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM Start Node.js blackboard server hidden (watchdog: restarts on crash)
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "while($true){Start-Process node -ArgumentList '%SCRIPT_DIR%server.js' -Wait -WindowStyle Hidden; Start-Sleep 2}"
timeout /t 2 /nobreak >nul

REM Start cloudflared tunnel hidden, capture URL
del /q "%SCRIPT_DIR%tunnel_url.txt" >nul 2>&1
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process '%CF_EXE%' -ArgumentList 'tunnel --url http://127.0.0.1:8080' -WindowStyle Hidden -RedirectStandardOutput '%SCRIPT_DIR%tunnel_url.txt' -RedirectStandardError '%SCRIPT_DIR%tunnel_url.txt'"

echo Relay started. Waiting for URL...
timeout /t 10 /nobreak >nul
type "%SCRIPT_DIR%tunnel_url.txt" | findstr trycloudflare
echo.
echo Full log: %SCRIPT_DIR%tunnel_url.txt
pause
