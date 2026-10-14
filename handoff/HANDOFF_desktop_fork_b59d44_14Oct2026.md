# Handoff: desktop session "Phone Android2 Shared session (fork)" [b59d44], 2026-10-14

## State
- Single loop running on clean history (mt4_tester2): driver evolve.ps1 (PID 16948) + auto_loop.py (PID 4844). No MT4_PAUSE files. Do not start a second driver or tester. Not archived: the loop is still running and only Nasif archives sessions.
- Corrected engine (rollover 23-01 fix, base-set collision fix, b52 clamp fix). Old +10k/+18k leader numbers are invalid (DSR 0.595). Waiting on rc_th_g2 then wr_* results for the real leader and win rate.
- RAM is tight (~1.2 GB after trim). Run scripts\ram_trim.ps1 when blocked; never kill processes.

## Done this session
- AGENT_RULES_READ_FIRST.md, PHONE_BRIDGE_STATUS.md (bridge doc for the $ Trade project), agent_readonly\ (read-only BTC alert + Telegram /status, not started).
- data\fxopen_cost_model.json (scenarios published USD, published_eur, 5pt, 6pt; leverage 500; leverage rule switch unverified/low priority). Agent board jobs 8-19.
- Reviewed phone-chat "Agent Trading System" page: its order-placing parts were NOT adopted.

## Waiting on Nasif (confirm in the desktop chat)
1. 6pt test: which candidate. 2. Tiered grid (published USD basis, 7 runs): tier7@500, tier5@1000, tier5@1100, tier3.6@25000, tier3.6@27500, tier3.0@250000, tier3.0@275000. 3. Commission currency basis USD vs EUR (statement). 4. Tester leverage setting should be 500 (unverified). 5. Shadow ledger script (post-processing only) after cost model fields are filled.

## Peers
- Cloud forks [7e95d6], [7d82b9], [a4rtsd] (cloud, one-way, cannot reply to the desktop): ER study read-only, gap audit done (repo .hst copy is stale, not authoritative).
- Repo is now on branch claude/project-thread-j8fma9 with 3 stashes from the old branch; restore only via the RC thread that stashed them.
- Remote Control session local_93e7f36b received the rules.

## Update 16:20
- The loop had silently stopped ~16:00 (RAM fell to ~400 MB, no PAUSE file). Trimmed RAM (545 -> 1346 MB) and restarted with scripts\resume_tests.ps1: single driver (powershell 20984) + auto_loop (python 19272) + terminal.exe 17592. Watch for repeats: RAM is the weak point.
- Queued at the front of extra_candidates.json (backup bak8): 7 sim_* runs on MR_RegimeSwitch_b63 (UseLotSim, SimDeposit, SimLeverage<=500). A lot-aware re-pricing script is still TO BUILD before analysing them (cost_scenarios.py assumes 0.16 lot). Run param_audit after the first sim_* report.
- cost_scenarios.py re-prices finished tests at 3.45pt, 5pt, 6pt, 8pt and tier/eur families (post-processing, new csv per run). Best so far rc_th_g2_AtrCapPts_90_hours_00-03: +18.2k pts, 177 trades over 8 yrs at sp5 (few trades, unproven).
- Remote Control session local_93e7f36b: gap audit shows mt4_tester2 M1 history clean (data\gap_audit_EURUSD1_tester2_14Oct2026.txt).
- Nasif (relayed): shadow stays local, no cloud clone, no daemon. AFTER EACH FINISHED TEST BATCH run once, idle priority, post-processing only: back up data\ALT_WIN_LOGIC.md first (the script rewrites it), then `python -E -P data\shadow_audit.py` (skips itself if RAM < 0.9 GB free), then add one line to agent_board.json. Not run yet: the current batch (sim_* runs) is unfinished.
- EUR/USD rate wording: always "1 EUR / USD $ 1.15000".
- 2025-01..08 leader run (Nasif via MQL cloud relay, clean hist mt4_tester2): guarded one-shot scripts\run_2025_leader.ps1 launched hidden (single-instance mutex, waits for tester idle, RAM >= 1 GB, honors PAUSE, gives up after 6 h). Report will be hst_out\clean\LOOP_rc_th_g2_AtrCapPts_90_hours_00-03_2025_sp5.htm; check evolve_log.txt lines prefixed run_2025_leader. Re-price at 3.45/5/6/8pt with data\cost_scenarios_lots.py --all (lot-aware) or cost_scenarios.py.
- Sim queue order cheapest-first (backup bak9); sim_tier7_at_500 was already in progress. Lot-aware analysis: data\cost_scenarios_lots.py (no args = sim_* only). First results sim_tier7_at_500 2016/2018 look sane (0.01 min lot at $500).
- Shadow audit after the batch (see above). Loop weak point: RAM (stopped once at ~400 MB free).

## Update 18:50 (handoff to the MQL cloud session, Nasif continues there)
- Standing rule: first result of any candidate at cheapest commission (3.0pt published >250k tier; 3.45pt EUR-base separate label), 500 max leverage, then 5pt, 6pt, 8pt, never mixed. USD basis. EUR/USD rate always "1 EUR / USD $ 1.15000".
- Loop still running (single driver). Now on sim_tier3p0_at_250000 (2023 year 3/8), then 3.0 -> 3.6 -> 5 -> 7 tiers. Lot-aware analysis: data\cost_scenarios_lots.py. Re-pricing: data\cost_scenarios.py (latest cost_scenarios_20261014_1845.csv).
- OPEN: 2025-01..08 rerun (first attempt INVALID: 0 trades, 0.7 min, wrong folder, quarantined in hst_out\clean\_suspect_2025_leader_0trades_14Oct2026); check if leader ATR cap 90 blocks all 2025 entries; rerun only via the loop's clean path. 6pt candidate still unnamed by Nasif (working: rc_th_g2_AtrCapPts_90_hours_00-03, 177 trades, unproven).
- Shadow audit once after the batch (backup ALT_WIN_LOGIC.md first). Progress page: data\progress.html via data\progress_page.py.
- Cloud sessions cannot message the laptop session back; the laptop session can receive messages by name. Nothing is paused; nothing is live-approved.

- Balance tiers: only below $60k are tested (Nasif). Queue: 3.6@25000, 27500, 50000; 5@1000, 1100, 5000, 10000; 7@500; 3.0@250000 already ran, 275000 finishing. Backup bak10.
