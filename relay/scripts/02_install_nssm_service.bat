@echo off
:: 02_install_nssm_service.bat - Install cmd_poller.ps1 as Windows service via NSSM
:: Idempotent: removes and recreates service each run.
:: Requires: Signal repo cloned at REPO path (run 01_clone_signal.bat first).

set REPO=C:\Users\endos\Desktop\hst_work\Signal
set SCRIPT=%REPO%\relay\cmd_poller.ps1
set NSSM=%REPO%\relay\nssm.exe
set SERVICENAME=CloudCmdPollerGH
set LOGDIR=C:\Users\endos\Desktop\hst_out

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

:: Download NSSM if missing
if not exist "%NSSM%" (
    echo [INFO] Downloading nssm.exe...
    powershell -NonInteractive -Command "& { $z='%LOGDIR%\nssm.zip'; Invoke-WebRequest 'https://nssm.cc/release/nssm-2.24.zip' -OutFile $z; Expand-Archive $z -DestinationPath '%LOGDIR%\nssm_tmp' -Force; Copy-Item '%LOGDIR%\nssm_tmp\nssm-2.24\win64\nssm.exe' '%NSSM%'; Remove-Item $z,'%LOGDIR%\nssm_tmp' -Recurse -Force }"
    if not exist "%NSSM%" (
        echo [ERROR] nssm.exe download failed.
        echo         Download manually: https://nssm.cc/download
        echo         Place win64\nssm.exe at: %NSSM%
        exit /b 1
    )
)

:: Remove existing service
"%NSSM%" stop "%SERVICENAME%" 2>nul
"%NSSM%" remove "%SERVICENAME%" confirm 2>nul

:: Install service
"%NSSM%" install "%SERVICENAME%" powershell.exe
"%NSSM%" set "%SERVICENAME%" AppParameters "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File \"%SCRIPT%\""
"%NSSM%" set "%SERVICENAME%" AppDirectory "%REPO%"
"%NSSM%" set "%SERVICENAME%" DisplayName "Cloud Command Poller (GitHub relay)"
"%NSSM%" set "%SERVICENAME%" Description "Polls GitHub relay branch for queued commands. Executes and pushes results."
"%NSSM%" set "%SERVICENAME%" AppStdout "%LOGDIR%\cmd_poller_svc.log"
"%NSSM%" set "%SERVICENAME%" AppStderr "%LOGDIR%\cmd_poller_svc_err.log"
"%NSSM%" set "%SERVICENAME%" AppRestartDelay 5000
"%NSSM%" set "%SERVICENAME%" Start SERVICE_AUTO_START
"%NSSM%" start "%SERVICENAME%"

sc query "%SERVICENAME%" | findstr /i RUNNING >nul
if %ERRORLEVEL% == 0 (
    echo [OK] Service running. Log: %LOGDIR%\cmd_poller_svc.log
) else (
    echo [WARN] Service installed but may not be running. Check: sc query %SERVICENAME%
)
exit /b 0
