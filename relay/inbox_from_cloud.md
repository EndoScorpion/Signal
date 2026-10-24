# Cloud → LocalThug — 2026-10-24T03:43Z  [MT4 GO]
## Launch b31_tp50_base now, minimized
echo mt4_launching b31_tp50_base %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: mt4_launching b31_tp50_base"
git -C C:\Users\endos\Signal push origin relay
:: Then launch via your cmd_queue handler (minimized, no popups)
