# EA EUR/USD — consolidated hub state (owner: hub endos-29, CLI PID 15388)

## Gate rule (user)
Only proceed with work that raises EUR/USD win rate AND keeps PF >= 1.10 and max DD < 5%,
measured OUT of sample (not 2019 alone). Anything else: pause.
COMMISSION (user, confirmed in hub 2026-10-12): live FXOpen charged up to 8 pts per trade max.
Score every result at BOTH 6 pt and 8 pt, charged once from raw prices. The pass bar must hold at 8 pt.

## Data
- FXOpen EU MT4, server FXOpenEU-ECN, 5-digit (1 pip = 10 pts). Commission cap 6 pts/round turn ($0.06 per 0.01 lot).
- Tester profit already includes ~$0.08/trade -> always score from RAW prices + 6 pts, once.
- History coverage: 2019 M1 96% (Jan 3-11 gap), 2021 M1 90% (Feb 16-Mar 18 gap -> test from 2021-03-19),
  2011 M15 93% (Aug 8-24 gap), 2012 M15 96%, 2018 only 35% (excluded). No data Sep 28 2022 - Aug 28 2025.
- IS = 2019. OOS = 2021-03-19..2022-01-01, 2012, 2011.

## Infrastructure
- Backtest copy (portable, no login): C:\Users\endos\MT4_Backtest
- Queue: queue.txt (EA|Period|From|To|Spread[|Deposit]); runner run_queue.ps1 (one job/call, lock, >=1 GB RAM, dedupe via done.csv)
- Guard hook: ~/.claude/hooks/mt4-guard.ps1 (blocks overlapping MT4 launches from any local session)
- Reports: MT4_Backtest\reports\ ; old ones in %APPDATA%\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\reports\
- Live-terminal EA sources: %APPDATA%\...\6278E353...\MQL4\Experts (g2a-g2e, g3a .mq4/.txt)
- Git channel to cloud: C:\Users\endos\Signal, branch claude/mql4-analysis-comments-bd4kz3 (data/ out, results/ in)
- Scoring scripts: hub scratchpad rb\an.py (monthly/raw-price), br.py (branch/time-block); scorer's run6.py (see handoff below)

## Variants
| Name | Change vs b20legs_g1a | Status |
|---|---|---|
| g2a | no sell-stop/ladder 12-16, 20-24 server time | 2019 IS: 403 tr, 57.1%, PF 1.28, +$147, DD $104 (1.0%) |
| g2b | g2a filter on g1b (360 TP/SL) | queued |
| g2c | g2a + no hedge sell 20-24 | queued |
| g2d | g2a + no pending sells 00-04 | queued |
| g2e | g2a + hard MaxOpenOrders=4 risk guard | HELD until 2021 result |
| g3a | g2a but 12-16 reopened when H1 ADX(14) > 25 | DROPPED: g1a 2019 12-16 trades with ADX>25 = 55 tr, 49.1% win, net6 -$6.30 (system32-df, g3a_adx.js) |
| Signal repo EA (baf8d86) | separate long-only scalper | needs 5-digit fix (sl/tp x10) before test |
Baseline b20legs_g1a 2019 IS at 6 pt: 670 tr, 54.0%, PF 1.13, +$122, DD $187.

## Queue order (decisive first)
1-2 g1a vs g2a 2021 OOS · 3-4 g2d 2019/2021 · 5-6 g1a vs g2a 2012 · 7-10 g2b/g2c · 11-12 g1a vs g2a 2011 · $5k run PAUSED

## Handoffs received
(appended below as sessions close)
- signal-a2 (git bridge): repo C:\Users\endos\Signal, branch claude/mql4-analysis-comments-bd4kz3, last push e97cd0a (data/: g2a 2019 report, leaderboard.md, commission_repricing.md). Local is 3 commits behind origin -> `git pull` before use. No git identity on PC: commit with `git -c user.name=EndoScorpion -c user.email=<addr> commit ...`.
- signal-a5: ended (was teleport PID 9420); no local files.
- system32-df: reports\g2_diff_notes.txt, reports\g2e_proposal.mq4; its watcher stopped (watch_queue.stop).
- Win rates (scorer): rescore one report -> `python -I C:\Users\endos\Desktop\hst_out\commission6\rescore\score1.py "<report.htm>" <deposit>` (trades, win%, PF, net, commission, max DD $/%). Same folder: reprice_pf.py, leaderboard.py (doesn't parse new *_M1_YYYYMMDD-YYYYMMDD_spN names; add rows by hand), stopfill.py (leak). Board: reports\leaderboard.md; 40-run table hst_out\commission6\summary_6pt.csv. hst_out\seg_reprice2.json is 8 pt (discard).
- mql4-79 (builder): sources+.txt in live Experts (Strong2010b_claude_{g2a..g2e,g3a}, UTF-8 BOM); g2a-g2d compiled in MT4_Backtest\MQL4\Experts; g2e/g3a NOT compiled (held). Status: ...\MQL4\claude_coord.txt.
  Scripts (node <script> <report.htm>) in MT4_Backtest\reports\mql4-79_scripts\: branches.js (per-branch net6), spill.js (leak; 2nd arg blocked hours e.g. 0-4,12-16,20-24), blockedq.js (12-16/20-24 by quarter).
  Scoring: sells (open-close)*lots*100000, buys reverse, minus 6*lots once; never use report profit.
  TODO: (a) score 2021 g1a vs g2a vs gate; (b) g3a check = count g1a 2019 12-16 trades with H1 Wilder ADX(14)>25 from EURUSD60.hst; queue g3a only if meaningful AND 2021 passes; (c) g2e compile+queue after 2021.

## After a report lands (hub checklist)
1. from C:\Users\endos\Desktop\hst_out\commission6\rescore: `python -I score1.py "<report>" 10000` (must run in that folder)  2. `node ...\spill.js "<report>" <blocks>`  3. add IS/OOS row to leaderboard.md  4. gate verdict (OOS only)  5. copy to Signal\data\, git pull + commit + push

## Offline TP/SL replay (signal-a2, no MT4) — reports\tpsl_grid_2019.md — IN-SAMPLE
Self-check TP300/SL300 = real g1a exactly (670, 54.0%, PF 1.13, +$121.80). Top by PF that raise win%:
TP200/SL400 72.8% PF 1.28 +$208 DD $161 · TP250/SL400 67.3% PF 1.24 +$211 DD $176 · TP300/SL400 61.9% PF 1.18 +$185 DD $242 · TP250/SL300 59.3% PF 1.16 +$133 DD $130.
Caution: win% rises because SL widens (200/400 needs >67.6% to break even); SL400 is grid edge. NEXT: replay same grid (+SL500) on 2021 OOS g1a trades once that report exists; entries held fixed (approximation) -> confirm best in MT4.

## Statistical check (signal-a2, 2019 IN-SAMPLE)
Runs z ~ -21 for every TP/SL combo: wins/losses cluster (ladder legs share outcomes) -> trades are NOT independent.
Trade-level bootstrap p=0.001-0.07 is MISLEADING. Day-block bootstrap: p(net<=0)=0.17-0.33 for all candidates
(TP200/SL400 PF 1.26@8pt p=0.17; TP300/SL300 PF 1.11@8pt p=0.33). => 2019 edge not distinguishable from luck. OOS decides.
RULE: use day-block resampling for any significance claim; never trade-level p-values.
Script: tpsl_oos.py (grid 200-360 x 200-500, 6/8pt, runs, day-block bootstrap+permutation, monthly PF).
- signal-a2 closed (handoff): scripts in MT4_Backtest\tools\. Run OOS grid on a report:
  python -I C:\Users\endos\MT4_Backtest\tools\tpsl_oos.py "<report.htm>" OUT-OF-SAMPLE C:\Users\endos\MT4_Backtest\reports\tpsl_oos_2021.md 2021.03.19

## Process inventory + gate status (signal session, 2026-10-12 ~03:56, read-only; nothing killed or spawned)
Free RAM 0.39 GB (queue needs 1.0; a new local CLI needs >= 1.5 per clone-guard; cloud master asks 2.0 for clones).
| PID | process | MB | purpose |
|---|---|---|---|
| 15288 | Claude CLI, resumed session (parent powershell 9348) | 326 | MASTER hub (keep) |
| 16480 | powershell watch_queue.ps1 (hidden) | small | queue watcher, polls 3 min, runs jobs only when >= 1.0 GB free (keep) |
| 19936 | Claude Code 2.1.295 embedded in the Claude desktop app | 289 | a Claude Desktop (non-CLI) session, role not verified |
| 16136, 9836, 11100, 22060, 20560, 12136, 5272, 11224, 14848, 1096 | Claude desktop app shell (Electron renderer/gpu/utility/crashpad, parent 17696) | ~1000 total | desktop app; renderer 16136 alone is 664 MB, the biggest quick RAM win if the app is closed |
| 18200, 4144, 22116, 17952, 6948, 21788 (+ 22400, 2388, 20440, 20184, 21384, 13976 npx launchers) | node.exe under cmd.exe, npx MCP servers (@mod..., @won... packages, command lines truncated) | ~700 total | MCP server helpers for desktop/CLI sessions; purpose inferred from package names, not verified |
Ask the user before killing any of these.

## OOS gate status (Strong2010b)
BLOCKING: no 2021 OOS report exists. Queue jobs 1-2 (b20legs_g1a and g2a, M1, 2021.03.19-2022.01.01, sp3) wait only on RAM (>= 1.0 GB free).
SMALLEST CLEARING TEST: those two jobs (~1 min each when RAM allows). Score at 8 pts raw prices. Pass = win % above g1a baseline AND PF >= 1.10 AND DD < 5% AND day-block p <= 0.05/21 = 0.0024 (pool 2012/2011 days if 2021 is too short).

## Proposal (NOT run): g2a with TP 250 instead of 300, SL 300 unchanged
Why: 2019 replay at 8 pts: win 59.3% (baseline 54.0%), PF 1.14, DD $135.52 (lowest of the profitable set), and unlike TP200/SL400 it does not widen the stop. IN-SAMPLE only.
Validate OOS only: MT4 tester, g2a with InpTPRange=250 (needs a g2f variant or .set; no logic change), M1, 2021.03.19-2022.01.01, spread 3, 0.01 lot; then 2012 M15 sp2. Do not run before the g1a/g2a 2021 jobs.
File changed: this one. Backup: HUB_STATE.backup_20261012.txt
