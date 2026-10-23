@echo off
REM SAFE_GIT_PULL.bat - double-click to run (auto-elevates to Admin)

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Requesting Admin...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/5] Stopping CloudCmdPollerGH...
schtasks /End /TN "CloudCmdPollerGH" 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Killing git.exe...
taskkill /F /IM git.exe 2>nul
timeout /t 1 /nobreak >nul

echo [3/5] Removing index.lock...
del /F "C:\Users\endos\Signal\.git\index.lock" 2>nul

echo [4/5] Syncing relay branch...
cd /d C:\Users\endos\Signal
set GIT_TERMINAL_PROMPT=0
git fetch origin relay
git reset --hard origin/relay

echo [5/5] Restarting CloudCmdPollerGH...
schtasks /Run /TN "CloudCmdPollerGH" 2>nul

echo.
echo Done. Relay synced, poller restarted.
pause
