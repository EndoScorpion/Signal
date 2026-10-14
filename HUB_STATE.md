# HUB_STATE (coordinator: "Phone Android Signal" [33e18c])

Rules (set by Nasif): single coordinator; sessions send short text reports here. Do NOT start MT4 or tests. `C:\Users\endos\Desktop\hst_out\MT4_PAUSE` stays until Nasif lifts it.

## Global status (2026-10-12)
- MT4: PAUSED (MT4_PAUSE flag present). No MT4 tests started from this session.
- RAM: very tight (free ~420-710 MB, memory 86-89%). clone-guard hook blocks PowerShell under 1.5 GB free.
- Phone link: two-way confirmed. Remote-control host = claude.exe PID 4200 (`--remote-control Signal`). Never end it.

## Sessions
| Session | Ref | Role | State |
|---|---|---|---|
| Phone Android Signal | 33e18c | Coordinator (this) | idle |
| Remote control | 0056ec | Archives sessions / RAM advice | idle; archived "Recover closed master CLI" |
| Remote Control session (from a project) | 094e32 | hst_out MT4 test queue owner | idle; MT4_PAUSE enforced in run_tester.ps1 |
| Shared session | 8fb6e6 | clone/master test, large transcript | idle; candidate to archive |

## Done
- MT4_PAUSE guard added to Signal scripts: run_oos_gate.ps1, _v2, run_g5_all_v2, run_g7, run_g8 (compile_and_gate_v2 and run_oos_gate_v3 already guarded).
- scripts/ram_guard_v1_12Oct2026.ps1: tiered RAM relief (Eco / pause / graceful end), dry-run default, protected list. Tested on a fake process only. NOT running.

## Pending (needs Nasif)
- Silent-mode edits for gate scripts (TestVisualEnable=false, minimized terminal launch).
- Commission 6 -> 8 in run_oos_gate_v3, g5, g7, g8 runners (g5 results must be rescored at 8 before comparing with hst_out).
- Whether to run ram_guard live (Eco-only first).
- Archive "Shared session" when idle to free RAM.

## Findings
- tick_log.csv built (88 reports, read-only, no MT4 started). History gaps seen in tester reports: 2023 and 2024 show 1970 dates (no data); 2022 data ends 2022.09.28; 2025 starts 2025.08.28. Any tick/history download for those periods needs MT4 -> blocked by MT4_PAUSE.

## Active (as seen on Nasif's screen)
- History download: NOT running in any session. "Shared session" [8fb6e6] says it is not part of it; it will only check file size/date coverage read-only if asked once a chunk lands. Nasif's note "attempting safe history download - the others are working" was a status note, not an assignment. If the download uses MT4/terminal.exe it conflicts with MT4_PAUSE; only Nasif lifts the pause.

## Report log (newest first)
- Web/claude.ai build chat (12 Oct 2026, 16:40): MT4 not touched, nothing deleted, nothing started. Backed up my own build files (copies only) to Signal\backups_web_build041_12Oct2026. Handoff: Signal\handoff\HANDOFF_web_companion_build041_12Oct2026_1640.md. Now idle.
- Remote control [0056ec] (Pirates/Signal) HANDOFF READY (per Nasif): win-logic findings (g5/g7 BlockADX: ADX 28->24 = PF 1.953 / WR 73.9% in-sample, untested multi-year or at 8pt; slope and S2Entry filters not binding), multi-year sweep read, file list and pending work are in Signal\HANDOFF_pirates_session_12Oct2026.md. Nothing deleted. Its helper watchers are STOPPED (stop files in Signal\scripts). All 19 cloud routines show enabled=false; no local scheduled tasks. NOTE: 3 sessions appeared in the agent list in the last 15 min ("MT4 terminal agent" [9c50a6] busy, "Win rates at 8pt commission" [d2f6eb], two "Remote Control session (from a project)" [3342e6] [33698c]) and hst_out [094e32] is no longer listed - RAM cost; owner unknown.
- hst_out [094e32]: watcher DISARMED. It can no longer lift MT4_PAUSE or start tests. MT4_PAUSE stays, no tester running; nothing starts until Nasif explicitly says "resume" to it. Re-arm = one command (run_guarded.ps1, 8 unseen-year jobs, RAM >= 1.0 GB, idle priority, minimized).
- Coordinator: asked all 3 peers to stay idle / minimal activity to save RAM. Applying ram_guard (Eco-only) live was DENIED by the auto-mode classifier; not retried or worked around. ram_guard remains dry-run only.
- hst_out [094e32]: citing Nasif's "safe ram test - coordinate with others". Its watcher is ARMED: when free RAM >= 1.0 GB for 2 checks it will LIFT MT4_PAUSE itself and run 8 unseen-year tests (serial, minimized, silent, 8 pts); re-pauses if RAM < 400 MB; stops if anyone recreates MT4_PAUSE. Free RAM 613 MB, nothing started. Asks: no downloads (QuotesDownloader / D:\ticks) or other MT4 work until its run reports GUARDED DONE (hst_out\guarded.log); don't recreate MT4_PAUSE unless Nasif asks. Will report when the run finishes/stops. FLAG FOR NASIF: auto-lift of MT4_PAUSE rests on a loose instruction; confirm or tell it to disarm.
- Remote control [0056ec]: read-only RAM check: free 646 MB of 5,965 MB, CPU 27%. No terminal/metatester/QuotesDownloader running. MT4_PAUSE exists. Its window-watcher silent flag is on. Below 1.0 GB test gate and 1.5 GB download gate, so nothing should start.
- Shared session [8fb6e6]: free RAM 0.6 GB (read via clone-guard hook; its own RAM command was blocked below 1.5 GB, not worked around). Below the 1.0 GB MT4 gate and the 1.5 GB download gate, so no tests or tick download should start. Nothing running from it; MT4 and history download not started.
- Remote control [0056ec] (Pirates/Signal session): QuotesDownloader NOT running; D:\ticks empty; no tick download started. Free RAM ~758 MB. Per the session (attributing it to Nasif, unverified by me): tick download waits until the hst_out MT4 tests finish and free RAM >= 1.5 GB, then ONE 3-month chunk to D:\ticks. It also says Nasif just approved the hst_out tests to resume - NOT confirmed by me; MT4_PAUSE flag still needs to be removed by Nasif.
- hst_out session [094e32]: received Nasif's "hst proceed" but NOT starting. Free RAM 387 MB < 1.0 GB start rule (and under 400 MB stop line). Top users: Claude app processes (844/333/275/259 MB). MT4_PAUSE stays. Guarded runner ready: hst_out\run_guarded.ps1 (serial, minimized, silent, 8 pts; waits for >=1.0 GB free before each test, kills tester and re-pauses if RAM <400 MB, stops if MT4_PAUSE reappears). Remaining: 8 unseen-year runs (2014-2016, 2018 for b22 and current best). Starts once RAM >=1.0 GB: needs idle Claude sessions closed or QuotesDownloader stopped.
- hst_out session [094e32] (2026-10-12): STOPPED. Queue paused, no tester/MetaEditor running, MT4_PAUSE honored (run_tester.ps1 exits 6), status-sync loop stopped. run_tester.ps1 now launches MT4 minimized/no-activate (ShowWindow 7; MT4 had focus in 1 of 638 samples).
  - PROVEN best (backtest only, NOT approved for live): b22_thu + Z-gate (ZMax 1.0) + daily range 1.0xD1 ATR5 = winners\WIN_GEN1_ZGate_DailyRange_b31.set; 8-period +75,254 vs b22 +48,429 at 8 pts/trade; holds at spread 5 and 8.
  - Rejected: all 17 PC_TEST_QUEUE candidates on 2017; chop, chop+zH1, chop+ADX (negative 2022); BE200/BE250; Z+range+chop no gain.
  - Pending when pause lifts: unseen-years check 2013-2016 + 2018 (2013 done for both; 8 runs left).
  - Blockers: none besides the pause.
