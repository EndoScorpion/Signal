@echo off
set ADB=C:\Users\endos\Signal\adb_tools\platform-tools\adb.exe
set TABLET=10.30.30.36:33087

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
"%ADB%" -s %TABLET% shell "curl -s http://10.30.30.80:7860/ping 2>/dev/null || echo curl_not_found"

echo === If curl missing, install via pkg ===
"%ADB%" -s %TABLET% shell "which curl || (pkg install -y curl 2>&1 | tail -3)"

echo === Test bridge ping from tablet ===
"%ADB%" -s %TABLET% shell "curl -s http://10.30.30.80:7860/ping"

echo === Send hello from tablet via bridge ===
"%ADB%" -s %TABLET% shell "curl -s -X POST http://10.30.30.80:7860/tablet -H 'Content-Type: application/json' -d '{\"msg\":\"tablet adb online\"}'"

echo.
echo === Done — tablet bridge tested via adb shell ===
pause
