@echo off
:: cmd_poller_setup.bat — GitHub relay poller setup
:: Run once as Administrator from anywhere on the machine

set REPO=C:\Users\endos\Desktop\hst_work\Signal
set SCRIPT=%REPO%\relay\cmd_poller.ps1
set TASKNAME=CloudCmdPollerGH

:: Create hst_out dir if needed
if not exist "C:\Users\endos\Desktop\hst_out" mkdir "C:\Users\endos\Desktop\hst_out"

:: Create parent dir if needed
if not exist "C:\Users\endos\Desktop\hst_work" mkdir "C:\Users\endos\Desktop\hst_work"

:: Clone Signal repo if not present
if not exist "%REPO%\.git" (
    echo [INFO] Cloning Signal repo...
    git clone https://github.com/EndoScorpion/Signal.git "%REPO%"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] git clone failed. Check network and GitHub access.
        pause
        exit /b 1
    )
)

:: Switch to relay branch
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
    echo [OK] Poller running. Log: C:\Users\endos\Desktop\hst_out\cmd_poller.log
) else (
    echo [ERROR] Run as Administrator.
)
pause
