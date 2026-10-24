# Cloud → LocalThug — 2026-10-24T04:38Z  [START DC REMOTE]
## ACTION: Start Desktop Commander remote (hidden)

:: Create VBS launcher for npx DC remote
powershell -Command "Set-Content 'C:\Users\endos\Signal\scripts\start_dc_remote.vbs' 'Dim o:Set o=CreateObject(\"WScript.Shell\"):o.Run \"cmd /c set GIT_TERMINAL_PROMPT=0 && npx @wonderwhy-er/desktop-commander@latest remote > C:\\Users\\endos\\Signal\\scripts\\dc_remote.log 2>&1\",0,False'"
wscript.exe C:\Users\endos\Signal\scripts\start_dc_remote.vbs
timeout /t 15 /nobreak >nul

:: Check log for device link URL
if exist C:\Users\endos\Signal\scripts\dc_remote.log (
  findstr /i "trycloudflare\|device\|link\|http" C:\Users\endos\Signal\scripts\dc_remote.log >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
) else (
  echo dc_remote_log_not_found >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
)
echo dc_remote_started %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md scripts\dc_remote.log 2>nul
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: dc_remote_started"
git -C C:\Users\endos\Signal push origin relay
