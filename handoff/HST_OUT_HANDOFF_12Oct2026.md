# HANDOFF - hst_out MT4 test session (Claude, Sonnet 5.5 low) - 2026-10-12
Written for every other Claude agent/clone on this PC. Nasif's orders: free RAM + disk for the history download, keep phone control, never lose win logic.

## 1. PROTECT (never delete, never overwrite)
- CURRENT BEST (proven in MT4 backtests, NOT approved for live): b22_thu + Z-gate (ZMax 1.0, 20 M15 bars; 0.7*z(close)+0.3*z(volume)) + daily range filter (no new sells when today's range so far > 1.0 x D1 ATR5).
  Set: hst_out\winners\WIN_GEN1_ZGate_DailyRange_b31.set (EA Strong2010b_claude_b31). 8-period +75,254 vs b22 +48,429 at 8 pts/trade; holds at spread 5 and 8.
- Base b22_thu: UseSellBlock (ADX 28 / hour 2) + SessBlock 11-14 + DayBlock 4 (Thursday). Set: mt4_tester\tester\b22_thu.set.
- Pack of everything unique (EA sources b22-b38, make_b*.py, winner sets, scripts, TEST_LOG, WINNERS_REGISTRY, WIN_LOGIC_LOG, results): Signal\ea_backup_12Oct2026\hst_out_win_logic_pack.zip (copy also in hst_out\WIN_LOGIC_PACK_12Oct2026\).
- Keep: analysis/entry/filter/money-management logic, self-improvement instructions, history data (.hst in mt4_tester\history, 267 MB each copy), EA sources, .set files, reports (.htm).

## 2. METHOD (reuse it)
1. Every test .set lists ALL inputs on the b22_thu base (tester keeps stale inputs otherwise; g2_* runs were invalid for this reason).
2. Score = net*100 - 8 pts/trade (Nasif's rule). WIN rule: better than base in most of 8 periods (2011, 2012, 2017, 2019, 2020, 2021, 2022, 2025-26), positive where base is, neighbours stable, then spread 5 and 8.
3. One test at a time, via hst_out\run_tester.ps1 (lock, minimized no-activate launch, idle priority, honors hst_out\MT4_PAUSE and MT4_Backtest\PAUSE). Never start MT4 while a pause file exists.
4. Offline estimates over-rate gates (chop/chop+zH1 looked huge offline, failed 2022 in MT4). Trust only MT4 multi-period results.
5. Log every test in hst_out\winners\TEST_LOG.txt; winners in WINNERS_REGISTRY.txt.

## 3. REJECTED in MT4 (do not retest): EMA 9/21 gate, ATR trail/stealth trail, session windows, calculus vel/acc, volume gates, Williams %R, Alligator/AO/AC, entropy, fractal paradigms A/C, frac buy, ATR brackets x3 (2011 -103k), A/D divergence, chop / chop+zH1 / chop+ADX (negative 2022), b23 break-even, CCI gates (mixed), Z+range+chop (no gain), standalone EAs (EMA_ATR scalper, Gemini b25/b26).

## 4. SELF-IMPROVEMENT INSTRUCTIONS for autonomous agents
- Gen loop: clone the winner, mutate ONE input group, run 2017 sp2 first, promote to 8 periods + sp5 only if it beats parent; stop a generation that fails to beat parent in 6 of 8 periods.
- Save winners as WIN_GEN<n>_*.set (+ .txt copy) in hst_out\winners; never overwrite; freeze parent source before mutating.
- Tune on one year, confirm on the others; unseen-years check (2013-2016, 2018) is still pending: 8 runs via hst_out\run_guarded.ps1 once Nasif lifts the pause.
- Nothing goes live without Nasif's explicit yes.

## 5. HOUSEKEEPING RULES (Nasif, 2026-10-12)
- Auto-update the registry/logs; keep at most 3 recent duplicate backups of any file; always keep the unique win logic above.
- Archive = zip + verify + delete only raw originals (old journals, tester logs). Never delete reports, sources, sets, history.
- Free RAM: idle sessions are archived by Nasif; do not run background loops; coordinator = Phone Android Signal; phone link sessions stay.

## 6. STATE at handoff
- MT4_PAUSE present; no tester running; my watcher disarmed; sync loop stopped.
- Disk: hst_out\compress_old.py is zipping ~11 GB of old journals + ~2 GB tester logs to D:\hst_archive (log: hst_out\compress.log). Verified before deleting originals.
