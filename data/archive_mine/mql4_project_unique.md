# MQL4 project transcripts: unique trading-logic ideas (Oct 9-12 2026)

Source: 13 transcripts in C:\Users\endos\.claude\projects\C--Users-endos-AppData-Roaming-MetaQuotes-Terminal-6278E353D77D4E501C6775ACEC85F415-MQL4 (streamed, read-only).
Scan: 908 keyword hits, narrowed to 455 unique rule/verdict snippets, then read. Skip-list (LINEAGE_DNA.md, RED_ZONES.md) applied: their families (ZGate, MMR, ER, SMA regime, stochastic K14, NFP, ATR tercile, daily range) are NOT the subject of these transcripts (MMR 0 hits, ZGate 4 hits, no b31 lineage content), so no overlap was removed.
Commission: per CLAUDE.md, 8 pts/trade. Several Strong2010b/g-series results were scored at 6 pts (FXOpen rule in memory); noted per row.
Session ids are the first 8 chars of the transcript file name.

| # | Rule idea | Exact parameters | Evidence (numbers, session, date) | Status |
|---|---|---|---|---|
| 1 | H4 trend + H1 pullback entry (Signal 1) | buy/sell; target 400 or 200; trail 100; no-trail variant | 2011-12 buy tp400 trail100 +$105 PF 1.34; 2019 buy -$27 PF 0.78. Sell tp400 trail100 +$63 (2011-12), +$18 (2019), +$16 (2017), -$11 PF 0.84 (2020). Session 177cdfa1, 2026-10-09 | tested-failed (buys fail 2019; sell fails 2020) |
| 2 | Sweep-and-reclaim of recent low (buy) | 40 tp / 120 stop, control points, spread 2 | 1969 trades, -$169, -8.6 pts/trade, PF 0.73; random baseline -9.8 pts PF 0.70. 177cdfa1, 2026-10-09 | tested-failed (no edge over random) |
| 3 | Bollinger lower-band touch in ranging market (buy) | same as #2 | 1018 trades, -$104, -10.2 pts, PF 0.69. 177cdfa1, 2026-10-09 | tested-failed |
| 4 | RSI leaving extreme (sell) | sell, target 200, trail 0 | 153 trades, +$51, +34 pts, PF 1.35 (2011-12 window only). 177cdfa1, 2026-10-09 | unclear (single window, low n, no OOS) |
| 5 | 20-bar breakout (sell) | sell, tp400 trail100 | 550 trades, +$90, +16 pts, PF 1.24 (2011-12). Buy side -$150 to -$159. 177cdfa1, 2026-10-09 | unclear (no OOS run) |
| 6 | London-open breakout | target 80/120/160, trail 0/60, stop 150, 48-bar time exit | 245 trades; best PF 0.94 (-$7). 177cdfa1, 2026-10-09 | tested-failed |
| 7 | Dip-rebound (3-day -5% drop, hold 3 days) | daily crypto/stock file | 57-71% wins, +0.8 to +1.4%/trade on file's own sample; best-of-6 at 160/60 PF 0.80 (-$480). 177cdfa1, 2026-10-09 | tested-failed (no rule with enough trades) |
| 8 | Server-hours 0-4 entry gate | HourStart=0, HourEnd=4, target 30, stop 600 | 2011-12 +$16.22, +5.6 pts, PF 1.38 (292 trades); 2019 +$6; 2021 -$61.36, PF 0.41 (217 trades). 177cdfa1, 2026-10-09 | tested-failed OOS (overfit in-sample) |
| 9 | Exit grid (target/stop) on fixed entries | 20/60, 40/60, 30/90, 40/120, 60/150; control points, spread 2 | All 5 pairs negative after cost: -14 to -18 pts/trade, PF 0.30-0.65. 177cdfa1, 2026-10-09 | tested-failed (exit alone does not rescue entries) |
| 10 | Trailing stop on profitable signals | trail 50 or 100 points | Trail 100 helped all three signals in 2011-12 (no-trail sell tp400 -$53 vs trail +$63). 177cdfa1, 2026-10-09 | unclear (in-sample only) |
| 11 | Random-entry control baseline (method) | random buys with same exit; 0.5 target/stop control | Random baseline -9.8 pts PF 0.70 vs rules -8.6 to -13.0 pts. Any entry must beat random. 177cdfa1, 2026-10-09 | proven as a test method |
| 12 | Ladder12 stacked-ladder EA (b12_ladder12) | ladder + HEDGE + SELLSTOP + RLOG branches | Full period 2001 trades, -17,879 pts, 61.8% win; LADDER branch -12,628 pts. 2026-only (seg3) +12,383 pts. 41dd9048, 2026-10-11 | tested-failed (full period); unclear on 2026 alone |
| 13 | RLOG buy branch (tight TP) | TP 15 pts vs SL 290 pts, spread 2 + 6-pt cap | 95% wins but -6,639 pts; 8-pt commission eats each win. Break-even needs ~99.3% wins at 11/290. 41dd9048 and 177cdfa1, 2026-10-09/11 | tested-failed |
| 14 | HEDGE sell branch | hedge sell order in ladder EA | 52.9% win, +1,296 pts (b12 run). 41dd9048, 2026-10-11 | unclear (branch-level only, not run standalone) |
| 15 | g2e risk guard (g2a + caps) | UseRiskGuard=1, MaxOpenOrders=4, DailyLossPct=2 | Proposal from hub; caps ladder stacking and daily loss. efc7e6f7, 2026-10-12 | untested |
| 16 | Offline TP/SL replay on g1a 2021 fills | TP250/SL400: PF 1.28, +$204.56, p=0.176; TP250/SL500 PF 1.28 p=0.173; TP300/SL400 PF 1.18. 2019 IS best TP250/SL400 PF 1.22 | Passes PF >= 1.10, DD < 5%, but not the Bonferroni bar p <= 0.0024 (21 candidates). d18a4f8d, 2026-10-12 | unclear (passes PF gate, fails stat bar) |
| 17 | g2a generation (in-sample winner) | g2a on 2019 M1: 403 trades, 57.1% win, PF 1.28 | Out of sample 2021: PF 0.87. Overfit warning from same agent. d18a4f8d and 86c3b185, 2026-10-12 | tested-failed (OOS) |
| 18 | g1a baseline gate | 2019 PF 1.11 @8 (IS); 2021 OOS 568 trades, win 52.5%, PF 1.05 @8, net +$38.56, DD 1.7% | Gate needs PF >= 1.10: FAIL. d18a4f8d, 2026-10-12 | tested-failed (OOS gate) |
| 19 | g4a OOS gate (Strong2010b_claude_g4a) | EURUSD 2021-03-19 to 2022-01-01, spread 3 | PF 1.085 (needs 1.10): FAIL; 328 trades, 61.9% win, +$39.85; max DD 0.90% (OK). b3dcceb2, 2026-10-12 | tested-failed |
| 20 | Weak-hour and Thursday exclusion (g4a) | block server hours 6, 8, 19 and Thursdays | Observed as weak in g4a 2021 OOS run; no separate test. b3dcceb2, 2026-10-12 | untested |
| 21 | ADX gate: reopen 12-16 when H1 ADX > 25 (g3a) | reopen window 12-16, H1 ADX > 25 | 55 trades, 49.1% win, net6 -$6.30. g3a dropped. d18a4f8d, 2026-10-12 | tested-failed |
| 22 | BlockADX=24 (g7a) | BlockADX=24 | In-sample PF 1.953, not validated; g7c/g7d not tested. efc7e6f7, 2026-10-12 | untested (in-sample only) |
| 23 | Sell-only clone of g1a | buys turned off | Ran 6 clones x 3 years (18 backtests); g1b worse than g1a in 2020, DD 33-64% higher. 3836883c, 2026-10-12 | tested-failed (g1b); g1a sell-only result unclear |
| 24 | Strong2010b_claude family (2018 M15 and 2019 M1) | 6 variants 2019 M1 spread 3; 5 variants 2018 M15 spread 2; no commission in raw reports | PF 1.02-1.11 (2019 M1), PF 0.86-1.04 (2018 M15). Commission re-pricing at 8 and 6 pts was requested; final pass list not seen. 86c3b185, 2026-10-12 | unclear |
| 25 | Pass gate for candidates | OOS PF >= 1.10, max DD < 5%, win % above baseline, Bonferroni p <= 0.0024 (21 candidates) | Gate used in d18a4f8d and b3dcceb2. Method rule. | proven as a method |

Count: 25 unique rule ideas (rows 11, 18-19, 25 are method or verdict items rather than entry rules).

Top 5 by evidence (most promising):
1. Row 16: TP250/SL400 exit on g1a fills. PF 1.22 IS, 1.28 OOS, passes PF and DD gates, but p=0.176 (needs <= 0.0024). Needs more data before any claim. Session d18a4f8d, 2026-10-12.
2. Row 22: BlockADX=24 (g7a). PF 1.953 in-sample. Highest number but unvalidated. Session efc7e6f7, 2026-10-12.
3. Row 14: HEDGE sell branch. 52.9% win, +1,296 pts inside a losing EA. Standalone test not run. Session 41dd9048, 2026-10-11.
4. Row 4: RSI leaving extreme (sell tp200, no trail). PF 1.35 on 153 trades, single window. Session 177cdfa1, 2026-10-09.
5. Row 5: 20-bar breakout sell (tp400, trail 100). PF 1.24 on 550 trades, 2011-12 only. Session 177cdfa1, 2026-10-09.

Caveats: rows 4, 5, 10, 14, 16, 22, 24 are unclear or untested. Most entry-rule families (H4/H1 pullback, sweep, Bollinger, breakout, dip-rebound) failed vs random or OOS. Commission basis differs across rows (6 vs 8 pts) as noted above.
