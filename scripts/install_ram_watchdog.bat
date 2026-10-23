@echo off
:: Installs RAMWatchdog scheduled task — run once as admin

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  powershell -Command "Start-Process '%~f0' -Verb RunAs"
  exit /b
)

set SCRIPT=C:\Users\endos\Signal\scripts\ram_watchdog.bat
set TASK=RAMWatchdog
set VBS=C:\Users\endos\Signal\scripts\run_hidden.vbs

schtasks /Delete /TN "%TASK%" /F >nul 2>&1

schtasks /Create /TN "%TASK%" /TR "wscript.exe \"%VBS%\" \"%SCRIPT%\"" /SC MINUTE /MO 5 /RL HIGHEST /RU SYSTEM /F

echo RAMWatchdog installed (every 5 min, hidden).
pause
