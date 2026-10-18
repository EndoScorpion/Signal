@echo off
:: cmd_poller_nssm_setup.bat — Install cmd_poller as a Windows SERVICE via NSSM
:: Run once as Administrator.
:: Advantage over Task Scheduler: runs as a true service, survives lock/reboot,
:: no desktop session required, restarts automatically on crash.
::
:: Requires nssm.exe in the same folder as this script, OR on PATH.
:: Download NSSM from https://nssm.cc/download (nssm-2.24.zip, grab win64\nssm.exe)
:: Drop nssm.exe into: C:\Users\endos\Desktop\hst_work\Signal\relay\

set REPO=C:\Users\endos\Desktop\hst_work\Signal
set SCRIPT=%REPO%\relay\cmd_poller.ps1
set SERVICENAME=CloudCmdPollerGH
set NSSM=%REPO%\relay\nssm.exe
set LOGDIR=C:\Users\endos\Desktop\hst_out

:: Create dirs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if not exist "C:\Users\endos\Desktop\hst_work" mkdir "C:\Users\endos\Desktop\hst_work"

:: Clone Signal if missing
if not exist "%REPO%\.git" (
    echo [INFO] Cloning Signal repo...
    git clone https://github.com/EndoScorpion/Signal.git "%REPO%"
    if %ERRORLEVEL% neq 0 ( echo [ERROR] git clone failed. & pause & exit /b 1 )
)

:: Switch to relay branch
cd /d "%REPO%"
git fetch origin relay
git checkout relay
git pull origin relay

:: Try to download nssm.exe if not present
if not exist "%NSSM%" (
    echo [INFO] nssm.exe not found. Attempting download...
    powershell -NonInteractive -Command "& { $z = '%LOGDIR%\nssm.zip'; Invoke-WebRequest 'https://nssm.cc/release/nssm-2.24.zip' -OutFile $z; Expand-Archive $z -DestinationPath '%LOGDIR%\nssm_tmp' -Force; Copy-Item '%LOGDIR%\nssm_tmp\nssm-2.24\win64\nssm.exe' '%NSSM%'; Remove-Item $z,'%LOGDIR%\nssm_tmp' -Recurse -Force }"
    if not exist "%NSSM%" (
        echo [ERROR] Could not download nssm.exe.
        echo        Download manually from https://nssm.cc/download
        echo        Place win64\nssm.exe at: %NSSM%
        pause
        exit /b 1
    )
    echo [OK] nssm.exe downloaded.
)

:: Remove existing service if present
"%NSSM%" stop "%SERVICENAME%" 2>nul
"%NSSM%" remove "%SERVICENAME%" confirm 2>nul

:: Install service: runs powershell.exe -File cmd_poller.ps1
"%NSSM%" install "%SERVICENAME%" powershell.exe
"%NSSM%" set "%SERVICENAME%" AppParameters "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File \"%SCRIPT%\""
"%NSSM%" set "%SERVICENAME%" AppDirectory "%REPO%"
"%NSSM%" set "%SERVICENAME%" DisplayName "Cloud Command Poller (GitHub relay)"
"%NSSM%" set "%SERVICENAME%" Description "Polls GitHub relay branch and executes queued commands."

:: Redirect stdout/stderr to log file
"%NSSM%" set "%SERVICENAME%" AppStdout "%LOGDIR%\cmd_poller_svc.log"
"%NSSM%" set "%SERVICENAME%" AppStderr "%LOGDIR%\cmd_poller_svc_err.log"

:: Auto-restart on crash, after 5s
"%NSSM%" set "%SERVICENAME%" AppRestartDelay 5000

:: Start automatically
"%NSSM%" set "%SERVICENAME%" Start SERVICE_AUTO_START

:: Start now
"%NSSM%" start "%SERVICENAME%"

if %ERRORLEVEL% == 0 (
    echo [OK] Service '%SERVICENAME%' installed and started.
    echo      Logs: %LOGDIR%\cmd_poller_svc.log
    echo      To stop:    sc stop %SERVICENAME%
    echo      To remove:  nssm remove %SERVICENAME% confirm
) else (
    echo [ERROR] Service start failed. Check logs.
)
pause
