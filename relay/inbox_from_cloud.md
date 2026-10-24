# Cloud → LocalThug — 2026-10-24T04:32Z  [CLAUDE STARTUP TASK]
## ACTION: Register Claude Desktop minimized on login

:: Step 1: Find real .lnk path
dir /s /b "%APPDATA%\Claude.lnk" 2>nul >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
dir /s /b "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Claude*" 2>nul >> C:\Users\endos\Signal\relay\outbox_to_cloud.md

:: Step 2: Register scheduled task
schtasks /create /tn "ClaudeDesktopStartup" /tr "cmd /c start /min \"\" \"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Claude.lnk\"" /sc onlogon /ru "%USERNAME%" /f
if %ERRORLEVEL%==0 (
  echo claude_startup_task_created %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
) else (
  echo claude_startup_task_FAILED %ERRORLEVEL% %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
)

:: Step 3: Push
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: claude_startup_task"
git -C C:\Users\endos\Signal push origin relay
