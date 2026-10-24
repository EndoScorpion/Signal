@echo off
REM Watchdog: keeps Node blackboard server alive, restarts on crash
REM Run hidden via start_blackboard.bat — do not run directly
set SCRIPT_DIR=%~dp0
:loop
node "%SCRIPT_DIR%server.js"
echo [watchdog] server exited, restarting in 3s...
timeout /t 3 /nobreak >nul
goto loop
