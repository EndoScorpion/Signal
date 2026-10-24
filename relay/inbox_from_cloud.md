# Cloud → LocalThug — 2026-10-24T02:45Z  [MT4 PAUSE]

## PRIORITY: PAUSE ALL MT4 TESTS NOW

```bat
echo. > C:\Users\endos\Signal\MT4_PAUSE
echo mt4_paused %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: mt4_paused"
git -C C:\Users\endos\Signal push origin relay
```

Do NOT run any MT4/theory_queue/cmd_queue entries.

## STANDING RULE: All hidden. No popups.

— Cloud relay 2026-10-24T02:45Z
