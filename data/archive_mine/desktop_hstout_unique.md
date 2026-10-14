# Unique trading-logic ideas from Desktop / hst-out / C--Users-endos transcripts (partial, keyword-window pass)

Method: streamed all jsonl files in the four named project folders (Pirates and system32 skipped), kept Nasif's user messages matching stoch/entry/trigger/gate/filter/regime/WIN/PF/profit/win rate/extern (1,130 windows, in `_scan_hits.tsv`). Skipped rules already in LINEAGE_DNA.md and RED_ZONES.md. Win rates below are from the in-browser SignalMonitor simulator (Desktop, Aug 2026), not MT4 tests, and have no profit factor or baseline value attached. Main-table rows need winning evidence; stochastic rows without it are listed separately below.

## Main table: evidence-backed winners only

No stochastic entry has been shown to win on an MT4 multi-period test. The Aug 2026 browser "winners" are small-sample (n=6 to 22) and not period-tested, so none qualify here.

| Rule idea | Exact parameters | Evidence | Status |
|---|---|---|---|
| (none qualifies) | - | Stochastic browser branches above are n<25 or lack a baseline; no MT4 PF or net profit recorded | - |

## Stochastic entries: no winning evidence (listed separately, as requested)

| Rule idea | Exact parameters | Evidence (session, date) | Status |
|---|---|---|---|
| Earliest first-gen stochastic trigger: stoch K 21-25 entry band | K 21-25 | 82364225, 2026-08-08, "first try stoch 21 - 25 entries, for at least one week" | unclear (no result recorded in the windows) |
| Stoch K 21-25 widened / plain | K 21-25 | 89fe2a43, 2026-08-09: 56.4% win n=110; 54.5% win n=121 | unclear (near coin-flip, no baseline gap) |
| Stoch K 13-17 "tight multi-sweep" | K 13-17, K-values 13-16 | 89fe2a43, 2026-08-09: 87.5% win, n=8 (7W/1L) | unclear (n=8, not tested on MT4) |
| Stoch K 18-22 tight (S20) | K 18-22 | 89fe2a43, 2026-08-09: 83.3% win, n=6 | unclear (n=6) |
| S20 guard (+/- SMA) | K 18-22 with SMA guard | 89fe2a43: 71.4% win, n=7 | unclear (n=7) |
| Stoch momentum | not specified | 89fe2a43: 59.1% win, n=22 | unclear |
| Stoch agreement | not specified | 89fe2a43: 55.1% win, n=89 | unclear (weak edge) |
| Slope-to-stoch ratio (SMA5 slope / stoch K5 etc.), ~0.3 ratio | ratio ~0.3 | 82364225, 2026-08-08 (idea only, no result) | untested |
| Stoch >=80 warning before buy, keep count | stoch >=80 | 3f5f51e0, 2026-10-11 (request, no result) | untested. Related to RED_ZONES K14>80 which lost in all 4 unseen years |
| Stoch K14 > 80 sells | K14 > 80 | RED_ZONES.md, lost in all 4 unseen years | tested-failed (sells only) |

## Other rules (non-stochastic)

| Rule idea | Exact parameters | Evidence (session, date) | Status |
|---|---|---|---|
| Quiet-market gate for sells (b13) | UseQuietGate=0, QuietRR=0.17 (H1 20-bar range / 20*ATR14), QuietADX=17.5 (M15 ADX14, closed bars) | 72b695a1, 2026-10-10 (code spec; no result found in windows) | untested |
| SellCCIMax | sells only when M15 CCI14 closed bar < value (999=off) | e8f21b79, 2026-10-11 (spec) | untested |
| SellBEStart / SellBELock | move "7" sell SL to entry-SellBELock once SellBEStart pts in profit (0=off) | e8f21b79, 2026-10-11 (spec) | untested |
| Dynamic threshold | 2.5 x ATR | e8f21b79, 2026-10-11 (code fragment) | unclear |
| Era filter: trailing 20-day ATR percent or monthly structure | trailing 20-day ATR% above X (X not set) | 72b695a1, 2026-10-11 (request) | untested |
| Chaos/Hurst regime (M5/M15 rescaled range) | rolling windows, not parameterised | 81414830, 2026-10-11 | untested (already noted in memory) |
| Volume-throttle: enter only if completed bar volume > prior bar | i=1 vs i=2 | e8f21b79, 2026-10-11 | unclear |

## Gaps

- The original first-generation M15 slope/momentum entry rule (LINEAGE_DNA inherited core) did not appear verbatim in the keyword windows. Its exact thresholds need a targeted read of the earliest Aug 2026 Desktop session (82364225) around the first ~10 user turns.
- No MT4 profit-factor numbers for the stochastic branches were found in these transcripts.
- Unique rule count (distinct ideas above): about 15 rows, most untested or unclear.
