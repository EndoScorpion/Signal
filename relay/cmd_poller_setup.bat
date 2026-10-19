@echo off
:: cmd_poller_setup.bat — GitHub relay poller setup
:: Run once as Administrator from C:\Users\endos\Desktop\hst_work\Signal\relay\

set REPO=C:\Users\endos\Desktop\hst_work\Signal
set SCRIPT=%REPO%\relay\cmd_poller.ps1
set TASKNAME=CloudCmdPollerGH

if not exist "C:\Users\endos\Desktop\hst_out" mkdir "C:\Users\endos\Desktop\hst_out"

:: One-time: ensure relay branch is checked out
cd /d "%REPO%"
git fetch origin relay
git checkout relay
git pull origin relay

:: Delete old task if exists
schtasks /Delete /F /TN "%TASKNAME%" 2>nul

:: Register ONLOGON task
schtasks /Create /F /TN "%TASKNAME%" ^
  /TR "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File \"%SCRIPT%\"" ^
  /SC ONLOGON /RL HIGHEST /DELAY 0001:00

if %ERRORLEVEL% == 0 (
    echo [OK] Registered. Starting now...
    schtasks /Run /TN "%TASKNAME%"
    echo [OK] Poller running. Log: hst_out\cmd_poller.log
) else (
    echo [ERROR] Run as Administrator.
)
pause
