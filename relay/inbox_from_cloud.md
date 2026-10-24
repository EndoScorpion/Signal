# Cloud → LocalThug — 2026-10-24T04:30Z  [TZ URGENT]
## DST TRANSITION SUNDAY OCT 26 -- ACTION REQUIRED BEFORE THEN

## TZ RULE:
:: MT4 server = EET (UTC+3 summer, UTC+2 winter)
:: Sunday Oct 26: server shifts UTC+3 -> UTC+2
:: After Oct 26: EA server_hour = UTC_hour + 2 (was +3)
:: All EA hour params referencing EET server time need +1 after Sunday

## YOUR ACTION:
:: 1. Open b31_tp50_base .set file
:: 2. Check if entry/exit hours are EET server time (likely) or UTC (internal)
:: 3. If EET: note all hour values -- they need +1 after Oct 26
:: 4. If UTC: no change needed
:: 5. Report which it is

echo tz_check_started b31_tp50_base %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
:: After checking, append result:
:: echo tz_result EET_or_UTC <hour_values> >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: tz_check_started"
git -C C:\Users\endos\Signal push origin relay
