@echo off
REM install_relay_auto_read.bat
REM Installs RelayAutoRead scheduled task (hidden, at logon)
REM Reads to_cli.json, executes commands, writes results to from_cli.json
REM Run as Administrator

set REPODIR=C:\Users\endos\Signal
set PSSCRIPT=%REPODIR%\relay\relay_auto_read.ps1
set VBSFILE=%REPODIR%\relay\run_relay_auto_read.vbs

echo [%TIME%] Pulling latest relay branch...
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "& git -C '%REPODIR%' fetch origin relay; & git -C '%REPODIR%' checkout relay -- relay/relay_auto_read.ps1"

echo [%TIME%] Creating VBS hidden launcher...
(
  echo Set wsh = CreateObject("WScript.Shell")
  echo wsh.Run "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File """ ^& "%PSSCRIPT%" ^& """", 0, False
) > "%VBSFILE%"

echo [%TIME%] Stopping any existing instance...
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Get-Process powershell | Where-Object { $_.MainWindowTitle -like '*relay_auto_read*' } | Stop-Process -Force" >nul 2>&1

echo [%TIME%] Registering RelayAutoRead task...
schtasks /Delete /TN "RelayAutoRead" /F >nul 2>&1
schtasks /Create /TN "RelayAutoRead" /TR "wscript.exe \"%VBSFILE%\"" /SC ONLOGON /RL HIGHEST /F
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: schtasks failed. Trying without /RL HIGHEST...
  schtasks /Create /TN "RelayAutoRead" /TR "wscript.exe \"%VBSFILE%\"" /SC ONLOGON /F
)

echo [%TIME%] Starting now...
wscript.exe "%VBSFILE%"

echo.
echo Done! RelayAutoRead installed and started.
echo PS1: %PSSCRIPT%
echo VBS: %VBSFILE%
echo Log: C:\Users\endos\Desktop\hst_out\relay_auto_read.log
echo.
pause
