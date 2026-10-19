@echo off
:: 07_poller_status.bat - Quick check of poller service + recent log lines

set SERVICENAME=CloudCmdPollerGH
set LOGDIR=C:\Users\endos\Desktop\hst_out

echo === Service Status ===
sc query "%SERVICENAME%"
echo.
echo === Last 20 log lines ===
powershell -NonInteractive -Command "Get-Content '%LOGDIR%\cmd_poller_svc.log' -Tail 20 -ErrorAction SilentlyContinue"
echo.
echo === Errors (last 10) ===
powershell -NonInteractive -Command "Get-Content '%LOGDIR%\cmd_poller_svc_err.log' -Tail 10 -ErrorAction SilentlyContinue"
pause
