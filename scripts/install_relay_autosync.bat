@echo off
REM install_relay_autosync.bat
REM (Admin cmd required) - right-click cmd.exe, Run as Administrator
REM Registers RelayAutoSync scheduled task: runs safe_git_pull.bat every 5 minutes, silent.

echo Registering RelayAutoSync scheduled task...

schtasks /Delete /TN "RelayAutoSync" /F 2>nul

schtasks /Create /TN "RelayAutoSync" ^
  /TR "cmd.exe /c C:\Users\endos\Signal\scripts\safe_git_pull.bat" ^
  /SC MINUTE /MO 5 ^
  /RL HIGHEST ^
  /F

if %ERRORLEVEL%==0 (
    echo RelayAutoSync registered. Runs every 5 minutes.
) else (
    echo ERROR: Failed to register. Make sure you ran as Admin.
)

echo.
pause
