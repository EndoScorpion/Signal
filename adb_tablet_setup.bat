@echo off
set ADB=C:\Users\endos\Signal\adb_tools\platform-tools\adb.exe
rem LAN addresses live in private\lan.bat (gitignored). It sets TABLET and BRIDGE.
if not exist "%~dp0private\lan.bat" (echo ERROR: private\lan.bat missing & exit /b 1)
call "%~dp0private\lan.bat"

echo === Connecting to tablet ===
"%ADB%" connect %TABLET%
timeout /t 3 /nobreak >nul

echo === Checking device ===
"%ADB%" -s %TABLET% get-state 2>nul
if errorlevel 1 (
  echo ERROR: Tablet not connected. Check wireless debugging is still enabled.
  pause
  exit /b 1
)

echo === Test curl on tablet ===
"%ADB%" -s %TABLET% shell "curl -s %BRIDGE%/ping 2>/dev/null || echo curl_not_found"

echo === If curl missing, install via pkg ===
"%ADB%" -s %TABLET% shell "which curl || (pkg install -y curl 2>&1 | tail -3)"

echo === Test bridge ping from tablet ===
"%ADB%" -s %TABLET% shell "curl -s %BRIDGE%/ping"

echo === Send hello from tablet via bridge ===
"%ADB%" -s %TABLET% shell "curl -s -X POST %BRIDGE%/tablet -H 'Content-Type: application/json' -d '{\"msg\":\"tablet adb online\"}'"

echo.
echo === Done — tablet bridge tested via adb shell ===
pause
