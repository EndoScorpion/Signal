@echo off
REM START_TUNNEL.bat - double-click to run (auto-elevates to Admin)

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Requesting Admin...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Starting tunnel server...
cd /d C:\Users\endos\Signal\scripts

echo [1/2] Starting node server.js (hidden)...
powershell -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -Command "Start-Process node -ArgumentList 'server.js' -WindowStyle Hidden" 2>nul
timeout /t 2 /nobreak >nul

echo [2/2] Starting cloudflared tunnel (URL will appear below)...
echo.
npx cloudflared tunnel --url http://127.0.0.1:8080

pause
