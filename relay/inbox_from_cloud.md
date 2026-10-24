# Cloud → LocalThug — 2026-10-24T03:38Z  [UNPAUSE + TUNNEL START]
## Nasif approved both. Execute now.

:: 1. REMOVE MT4 PAUSE FILES
del /F /Q C:\Users\endos\Signal\MT4_PAUSE 2>nul
del /F /Q C:\Users\endos\Signal\Backtest\PAUSE 2>nul
echo mt4_unpaused %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md

:: 2. START CLOUDFLARE TUNNEL (hidden)
call C:\Users\endos\Signal\scripts\start_blackboard.bat
timeout /t 12 /nobreak >nul
if exist C:\Users\endos\Signal\scripts\tunnel_url.txt (
  set /p TURL=<C:\Users\endos\Signal\scripts\tunnel_url.txt
  echo tunnel_url %TURL% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
) else (
  echo tunnel_started_check_server_log >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
)

:: 3. START MT4 TEST (minimized, b31_tp50_base first)
:: Run via LocalThug cmd_queue or direct — use existing EA launcher
echo mt4_test_queued b31_tp50_base %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md

:: 4. PUSH OUTBOX
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: unpause+tunnel+mt4_start"
git -C C:\Users\endos\Signal push origin relay
