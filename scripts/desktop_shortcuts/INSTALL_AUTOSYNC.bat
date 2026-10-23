@echo off
REM INSTALL_AUTOSYNC.bat - double-click to run (auto-elevates to Admin)
REM Registers RelayAutoSync scheduled task - runs SAFE_GIT_PULL every 5 min silently.

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Requesting Admin...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Registering RelayAutoSync scheduled task...
schtasks /Delete /TN "RelayAutoSync" /F 2>nul

schtasks /Create /TN "RelayAutoSync" ^
  /TR "cmd.exe /c C:\Users\endos\Signal\scripts\safe_git_pull.bat" ^
  /SC MINUTE /MO 5 ^
  /RL HIGHEST ^
  /F

if %ERRORLEVEL%==0 (
    echo.
    echo RelayAutoSync registered. Runs every 5 minutes silently.
) else (
    echo.
    echo ERROR: Task registration failed.
)

echo.
pause
