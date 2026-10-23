@echo off
REM Tunnel relay launcher - silent, no popups
REM Run from C:\Signal\ or C:\Users\endos\Signal\

set SCRIPT_DIR=%~dp0

REM Start Node.js blackboard server hidden
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process node -ArgumentList '%SCRIPT_DIR%server.js' -WindowStyle Hidden"
timeout /t 2 /nobreak >nul

REM Start Cloudflare tunnel, capture URL to tunnel_url.txt
start "" /b cmd /c "npx @cloudflare/cloudflared tunnel --url http://127.0.0.1:8080 > %SCRIPT_DIR%tunnel_url.txt 2>&1"

echo.
echo Blackboard relay started.
echo URL (wait 5s then check): %SCRIPT_DIR%tunnel_url.txt
echo Use: type "%SCRIPT_DIR%tunnel_url.txt" ^| findstr trycloudflare
echo.
echo READ:  curl https://<url>/board
echo WRITE: curl -s -X POST https://<url>/write -H "Content-Type: application/json" -d "{\"sender\":\"Cloud\",\"message\":\"WR67 PF2.9 n=36\"}"
echo.
echo VAGUE CODES ONLY in message field. Public URL - no strategy details.
echo.
pause
