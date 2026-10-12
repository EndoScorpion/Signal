# endos-29 Master Hub — State File
Last updated: 2026-10-12 (OOS-gate cloud thread)

## BLOCKING GATE
**2021 M1 OOS backtest must exit 0 before ANY EA code changes.**
Pass bar: PF ≥ 1.10 AND max DD < 5% ($500 on $10k) after 8pt commission.

---

## GATE STATUS (2026-10-12): RAN LOCALLY — g4b PASS (PF 1.460); see ## RESULTS and the g6/g7 notes below. (Earlier text said "NOT RUN"; MT4 runs on the local PC only.)
- **Cannot run in cloud.** MT4 Strategy Tester + FXOpen 2021 M1 tick history exist only on the PC.
- **EA mismatch fixed in this file.** Old Job 1 said "b20legs_g1a (Strong2010b_claude.mq4 current branch)".
  Those are different EAs: the branch `Strong2010b_claude.mq4` (662 lines) is a BUY-only PatRec rewrite;
  b20legs_g1a is the SELL-leg EA whose 2019 IS numbers are in the leaderboard. Testing the branch file
  would gate an EA that has no in-sample baseline. Job 1 now targets the compiled
  `MQL4\Experts\Strong2010b_claude_b20legs_g1a.ex4` (present on the PC, built 2026-10-08).
- **Scorer verified.** `oos_check.py` on the 2019 g2a report: 403 trades, PF 1.249, DD 1.05%, exit 0.
  Price-based 8pt recompute gives PF 1.26 / net $138.76, matching data/stats_8pt.md. Note: the report's
  profit column already carries ~8.6pt/trade broker cost, so `--commission 8` adds only $0.008/trade on top.
- **One-command runner:** `scripts/run_oos_gate.ps1` (RAM gate, writes tester ini, runs MT4 headless,
  copies report to data/, runs oos_check, exits 0/1). Set deposit $10,000 in the tester GUI once first.

### Next steps
1. Close MT4, then from the Signal folder: `powershell -ExecutionPolicy Bypass -File scripts\run_oos_gate.ps1`
2. Push the .htm from data/, fill in ## RESULTS below.
3. For the full OOS candidate set (stats_8pt.md, m=21): compile g2a–g2d .mq4 in MetaEditor (no .ex4 yet),
   rerun with `-Expert Strong2010b_claude_g2a` etc. A winner also needs day-block p ≤ 0.0024.
4. Only after exit 0: unblock Jobs 2–4.

---

## Overnight Queue (process in order)

### JOB 1 — BLOCKING OOS GATE
```
EA:        Strong2010b_claude_b20legs_g1a.ex4  (MQL4\Experts on the PC — NOT the branch Strong2010b_claude.mq4)
Pair:      EURUSD
TF:        M1
Period:    2021-03-19 to 2022-01-01
SpreadPt:  3  (sp3)
Deposit:   $10,000
Leverage:  1:100
Commission: 8pt per RT (InpCommissionPts=8)
```
**Steps:**
1. RAM check: `Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory`
   - Must be ≥ 1,000,000 KB (1.0 GB) before launching MT4
2. Launch MT4 Strategy Tester → load Strong2010b_claude.mq4
3. Set dates: 2021.03.19 – 2022.01.01, M1, EURUSD, Every Tick, $10k, 1:100
4. Run → wait for completion
5. Right-click Report tab → Save as HTML → save to:
   `Signal\data\Strong2010b_claude_b20legs_g1a_M1_20210319-20220101_sp3.htm`
6. Push to git:
   ```
   cd Signal
   git add data/Strong2010b_claude_b20legs_g1a_M1_20210319-20220101_sp3.htm
   git commit -m "data: 2021 M1 OOS backtest result (b20legs_g1a)"
   git push -u origin claude/mql4-analysis-comments-bd4kz3
   ```
7. Score:
   ```
   python analysis/oos_check.py data/Strong2010b_claude_b20legs_g1a_M1_20210319-20220101_sp3.htm --commission 8 --deposit 10000
   ```
8. Record result in this file under ## RESULTS

---

### JOB 2 — HOLD (post OOS gate)
CostGateOK formula fix + TP raise to ≥ 458pt  
File: Strong2010b_claude.mq4  
See analysis/rvc_patch_draft.txt for details

### JOB 3 — HOLD (post OOS gate)
Restore g2a features missing from patched EA:
- H1 SMA(1200) directional gate
- M15 ADX<28 block  
- 3-level sell ladder

### JOB 4 — HOLD (post OOS gate)
Thursday filter: DayOfWeek() != 4 guard
Cross-check 2019 AND 2021 Thursday data first

---

## Security Constraints (HARD — do not override)
- No EA code commits without Job 1 exit 0
- RAM gate: ≥ 1.0 GB free for MT4 backtests
- RAM gate: ≥ 1.5 GB free for new local CLI clones
- Pass bar for ALL changes: PF ≥ 1.10 AND DD < 5% on 2021 M1 OOS
- Lucky bar (13 variants tested): 2021 OOS PF ≥ 1.306 (5%) or ≥ 1.275 (10%)

---

## RESULTS
*(fill in after Job 1 completes)*

12 Oct 2026 | Strong2010b_claude_g4b @ exp/g4b-hour-thu-filter | EURUSD M1 19 Mar 2021 -> 1 Jan 2022, spread 3
- Trades: 182 (123W/59L)
- Win rate: 67.6%
- PF: 1.460
- Net PnL: $98.19
- Max DD: $33.79 closed (0.34%)
- Verdict: PASS (OOS gate, exit 0). WARN hours: 12, 14, 15, 20, 22. WARN day: Monday (-2.66)
- Report: data\Strong2010b_claude_g4b_M1_20210319-20220101_sp3.htm

### Other variants, 2021 OOS (from data\g6_summary / g7_summary, cross-checked against the .htm reports)
Gate numbers (PF, closed DD) differ slightly from the MT4 report numbers (PF, equity DD); both shown.
| Variant | Gate | Gate PF / DD | MT4 report PF / DD | Trades |
|---|---|---|---|---|
| g6a | PASS | 1.462 / $33.77 | 1.47 / 0.47% | 182 |
| g6b | PASS | 1.476 / $33.77 | 1.48 / 0.47% | 183 |
| g6c | PASS | 1.462 / $33.77 | not checked | 182 |
| g6d, g6e | PASS | 1.311 / 1.292 | not checked | - |
| g7a | PASS | 1.953 / $21.84 | 2.03 / 0.29% | 134 |
| g7b | PASS | 1.586 / $29.29 | 1.65 / 0.41% | 80 |
- g5 a-e: failed RAM gate, no results. g7c/g7d: incomplete (RAM gate OK only).
- g8a: PASS but different settings (5k, 500 lev, 6pt spread); not comparable.
- g7a is best on paper; unverified beyond 2021 (check per-year OOS before trusting).

---

## Session Map
| Role | Session ID | Status | Notes |
|------|-----------|--------|-------|
| master | endos-29 (new session) | ACTIVE | runs queue |
| analyst | system32-df (cloud) | ACTIVE | multi-factor win model |
| scorer | signal-ba (cloud) | ACTIVE | 8pt rescore done |

## EA Branch
`claude/mql4-analysis-comments-bd4kz3`  
Last commit: `1ac0ba2`

### Pirates-folder session (Sonnet 5.5) - g5/g7 BlockADX results, 2026-10-12
Source files: Signal\data\g5_summary_v2_12Oct2026.txt, g7_summary_12Oct2026.txt; CSV via scripts\Log-G5Results.ps1.
Setup: EURUSD M1, 2021.03.19-2022.01.01, spread 3, commission 6, deposit 10000.
| Variant | Change vs g5a | Trades | Win% | Net | PF | MaxDD |
|---|---|---|---|---|---|---|
| g5a | baseline (BlockADX=28, S2Entry=0, Slope=1.5) | 182 | 67.6 | 98.56 | 1.462 | 33.77 |
| g5b | Slope=1 | 182 | 67.6 | 98.56 | 1.462 | 33.77 (identical: slope not binding) |
| g5c/g5d | S2Entry=1 | 192 | 67.2 | 98.20 | 1.430 | 38.32 |
| g5e | BlockADX=35, Slope=2 | 197 | 66.0 | 86.67 | 1.357 | 43.94 |
| g7a | BlockADX=24 | 134 | 73.9 | 120.09 | 1.953 | 21.84 |
| g7b | BlockADX=20 | 80 | 70.0 | 51.76 | 1.586 | 29.29 |
CAVEATS: all in-sample on the same window; BlockADX direction was chosen from g5e on this data, so g7a is tuned, not validated.
| g7c | BlockADX=22 | 113 | 70.8 | 79.60 | 1.665 | 21.84 |
| g7d | BlockADX=26 | 156 | 71.8 | 119.01 | 1.747 | 34.26 |
(g7c/g7d run 12 Oct 2026, same setup, both OOS gate PASS; source data\g7cd_summary_12Oct2026.txt. Still in-sample tuning on one window.)
g7a extras (12 Oct 2026, data\g7a_extra_summary_12Oct2026.txt): spread 6 on 2021 window: 138 trades, WR 74.6%, PF 2.040, DD $18.70, PASS (higher PF than spread 3 is odd - 4 more trades; treat as unexplained). 2022.01-2022.07 spread 3: 126 trades, WR 75.4%, PF 1.885, DD $33.76, PASS (first true out-of-window check for g7a).
g7a on choppy years (12 Oct 2026, data\g7a_years_summary_12Oct2026.txt), all FAIL: 2015 WR 52.1% PF 0.702 (73 tr); 2016 WR 48.4% PF 0.594 (155 tr); 2018 WR 52.4% PF 0.696 (126 tr). ADX 24 does NOT fix choppy years; g7a's 2021/2022H1 PF 1.9-2.0 does not generalise.
Improvement loop round 1 (master proposals; tune 2015-2018 ONLY, hold out 2019-2022): (1) BlockADX sweep 20/22/24/26, (2) ATR volatility cap, (3) loss-streak pause (last, high overfit risk).
DECISION RULE for the ADX sweep (written 12 Oct 2026 BEFORE sweep results were seen; do not change after):
- Winner = highest pooled PF over 2015-2018 (summed gross profit / gross loss). Each year >= 40 trades, pooled max DD < 5%. If within 0.03 PF, take the one with more trades.
- Real improvement over g4b/g7n baselines: in EACH choppy year (2015, 2016, 2018) PF >= +0.10 and win rate >= +3 pts; total wins >= 60% of baseline; pooled PF beats baseline; PF moves monotonically across ADX values (no lone spike).
- Reject all if (b) is not met, or gains appear in only 1 of the 3 choppy years; then stop.
- Holdout 2019-2022 is run exactly ONCE on the single chosen variant; no re-tuning afterwards.
Sweep results: data\adx_sweep_tuning_12Oct2026.txt.
NEW CHOPPY LOGIC TEST: ChopBracket_h1a (C:\Users\endos\Signal_copy\ChopBracket_h1a.mq4), a standalone test EA (does not touch the Strong2010b family). Moving bracket on the last 20 M15 bars' high/low, re-placed every bar: Mode 0 = limit orders just outside the edges (fade, only when ADX<=22), Mode 1 = stop orders outside the edges (breakout). One trade at a time, SL 150 pts, time exit 16 bars. Backtest only.
Pre-set plan (before results): tune ONLY on 2016 (best-covered choppy year); judge on 2015 and 2018 (partial data); holdout 2019, 2021, 2022 run once on the single chosen setting. Keep if PF >= 1.10 and WR/PF clearly better than g4b on 2016 AND it does not lose on holdout; max 3 parameter rounds, then stop.
HISTORY COVERAGE CHECK (12 Oct 2026, read-only sample of MT4_Backtest\history\...\EURUSD1.hst, ~3.5M bars; a full year is ~372k M1 bars; approximate, sampled every 5000th bar):
2011 ~350k, 2012 ~360k, 2019 ~360k, 2021 ~335k = full. 2016 ~285k (76%), 2022 ~255k (68%), 2026 ~280k (YTD).
PATCHY: 2013 ~200k, 2014 ~135k, 2015 ~115k (31%), 2017 ~180k (48%), 2018 ~130k (35%), 2020 ~220k (59%). MISSING: 2023, 2024 (0 bars); 2025 ~105k (28%).
Consequence: 2023-2025 "0 trades" = no history, not a filter bug. 2015/2017/2018/2020 per-year results come from partial data, so they are weak evidence either way; holdout 2019-2022 is only trustworthy for 2019, 2021, 2022(part). 2016 is the best choppy tuning year.
PENDING: g5 a-e rerun. Per-year (from .htm): g4b/g6b lose in 2015, 2016, 2018 (PF 0.59-0.86), win 2017/2019/2020/2022/2026; 2023-2025 have 0 trades (history missing or filter blocks all).
Note: a stray "g8a 5k 500lev 6pt" block sits in Signal\data\g8_summary_12Oct2026.txt, written by another session (unverified).
