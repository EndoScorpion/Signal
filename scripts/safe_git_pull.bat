@echo off
REM safe_git_pull.bat
REM (Admin cmd required) - right-click cmd.exe, Run as Administrator
REM Stops poller, kills git.exe, removes index.lock, resets to relay, restarts poller.

echo [1/5] Stopping CloudCmdPollerGH...
schtasks /End /TN "CloudCmdPollerGH" 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Killing any running git.exe...
taskkill /F /IM git.exe 2>nul
timeout /t 1 /nobreak >nul

echo [3/5] Removing index.lock if present...
del /F "C:\Users\endos\Signal\.git\index.lock" 2>nul

echo [4/5] Fetching + resetting to origin/relay...
cd /d C:\Users\endos\Signal
git fetch origin relay
git reset --hard origin/relay

echo [5/5] Restarting CloudCmdPollerGH...
schtasks /Run /TN "CloudCmdPollerGH" 2>nul

echo.
echo Done. Relay branch synced, poller restarted.
pause
