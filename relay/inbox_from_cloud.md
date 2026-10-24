# Cloud → LocalThug — 2026-10-24T03:37Z  [CLOUDFLARE TUNNEL TEST]
## ACTION: Start blackboard server + Cloudflare tunnel
:: First report RAM
for /f "tokens=2 delims==" %%M in ('wmic OS get FreePhysicalMemory /value ^| find "="') do set FREE_KB=%%M
set /a FREE_MB=%FREE_KB% / 1024
echo ram_check %FREE_MB%MB %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md

:: Start tunnel (downloads cloudflared.exe on first run if missing)
call C:\Users\endos\Signal\scripts\start_blackboard.bat

:: Report tunnel URL (server logs to tunnel_url.txt if configured)
timeout /t 10 /nobreak >nul
if exist C:\Users\endos\Signal\scripts\tunnel_url.txt (
  set /p TURL=<C:\Users\endos\Signal\scripts\tunnel_url.txt
  echo tunnel_url %TURL% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
) else (
  echo tunnel_started_no_url_file >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
)
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: tunnel_start_report"
git -C C:\Users\endos\Signal push origin relay
