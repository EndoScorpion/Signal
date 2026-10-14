# Phone bridge: desktop status for the $ Trade project (updated 2026-10-14 ~16:00 local)
Add this file to the project docs. The phone chat is not a terminal, so it reads this and Nasif pastes replies to the desktop session.

## Rules (read first)
- Backtest only. No orders or trades from any agent. Nothing is live-approved.
- One MT4 test at a time, single loop only (driver evolve.ps1 + auto_loop.py already running). No pause files exist now.
- Never kill others' processes; add files, never overwrite. Costs must be labelled on every number.

## Current state
- Loop running on clean history (mt4_tester2). First results landing: rc_th_g2 clean re-tests (2013, 2014, 2024 reports done). Then wr_* win-rate candidates.
- Old leader numbers (+10k/+18k) are INVALID (rollover window, base-set collision bugs fixed; DSR 0.595).
- Cost scoring now: max 5 pts RT + spread/2 ("5pt"). 6pt and tiered runs are separate labelled scenarios.

## Waiting on Nasif (answer in the desktop chat, not here)
1. 6pt test: which candidate?
2. Tiered test grid (published USD basis): tier7@500, tier5@1000, tier5@1100, tier3.6@25000, tier3.6@27500, tier3.0@250000, tier3.0@275000. Confirm to queue.
3. Commission currency basis: USD (published 7/5/3.6/3.0) or EUR (8.05/5.75/4.14/3.45)? Confirm from a real statement.
4. Tester leverage should be 500; I have not verified the tester setting.

## Where things live (PC)
- C:\Users\endos\Signal\AGENT_RULES_READ_FIRST.md, data\agent_board.json (jobs 8-19), data\fxopen_cost_model.json, data\LINEAGE_DNA.md
- agent_readonly\ : read-only BTC alert + Telegram /status scripts (not started)
