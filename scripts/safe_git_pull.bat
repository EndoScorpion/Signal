@echo off
REM safe_git_pull.bat
REM (Admin cmd required) - right-click cmd.exe, Run as Administrator
REM Stops poller, kills git.exe, removes index.lock, resets to relay, restarts poller.
REM Also used by RelayAutoSync scheduled task (silent background run).

schtasks /End /TN "CloudCmdPollerGH" 2>nul
taskkill /F /IM git.exe 2>nul
timeout /t 2 /nobreak >nul
del /F "C:\Users\endos\Signal\.git\index.lock" 2>nul

cd /d C:\Users\endos\Signal
git fetch origin relay
git reset --hard origin/relay

schtasks /Run /TN "CloudCmdPollerGH" 2>nul

REM When run manually, pause to show output.
REM When run by scheduler (no interactive window), this is a no-op.
if "%1"=="/manual" (
    echo.
    echo Done. Relay synced, poller restarted.
    pause
)
