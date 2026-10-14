# Handoff - Pirates/Signal session ("Remote control"), 2026-10-12
Model: Sonnet 5.5, low effort. Nothing running from this session after the stop files below are honored. No MT4/tests started by this session today except g7a/g7b (09:xx-10:xx, completed). MT4_PAUSE untouched.

## Win-logic findings that only this session produced (in-sample, EURUSD M1, 2021.03.19-2022.01.01, spread 3, commission 6, deposit 10000)
Base = Strong2010b_claude_g5a (EntrySlopeMin=1.5, UseS2Entry=0, BlockADX=28).
- EntrySlopeMin 1 vs 1.5 (g5b vs g5a): IDENTICAL results -> slope filter not binding in 1..1.5.
- EntrySlopeMin 1.5 vs 2 with UseS2Entry=1 (g5d vs g5c): IDENTICAL -> not binding in 1.5..2 either.
- UseS2Entry=1: +10 trades, PF 1.462 -> 1.430, net 98.56 -> 98.20 (slightly worse).
- BlockADX 28 -> 35 (g5e): PF 1.357, DD 43.94 (worse). Looser trend block hurts.
- BlockADX 28 -> 24 (g7a): 134 trades, WR 73.9%, net 120.09, PF 1.953, DD 21.84 (best so far).
- BlockADX 28 -> 20 (g7b): 80 trades, WR 70.0%, net 51.76, PF 1.586, DD 29.29 (too restrictive).
- BlockADX 22 (g7c) and 26 (g7d): files created, NOT TESTED.
CAVEAT: direction was chosen from g5e on the same window -> g7a is tuned, not validated. Multi-year sweep (g4b/g6b/g7n, 2015-2026): g4b loses 2015, 2016, 2018; wins 2017, 2019, 2020, 2021; ~flat 2022 (PF 1.09); 2023-2025 have NO history (0 trades). g7n has more trades but lower PF than g4b in nearly every year. g7a was never run multi-year or at 8pt cost.
Weekday/hour pattern (g4b, 1114 trades, all years): Mon/Fri strong (~69% WR), Tue/Wed weaker (57-59%); weak entry hours 4,6,13,14,19-22; strong 3,7,17,18. Not validated out of sample.

## Files (nothing deleted; all left in place)
- EAs: Signal_copy\Strong2010b_claude_g7a..g7d.mq4 and the same four in the MT4 Experts folder (g7a=ADX24, g7b=ADX20, g7c=ADX22, g7d=ADX26; copies of g5a with BlockADX only; comment encoding of (c) differs in g7a/g7b).
- Results: Signal\data\g5_summary_v2_12Oct2026.txt, g7_summary_12Oct2026.txt, g5_results_history.csv (built by scripts\Log-G5Results.ps1, now reads g?_summary*.txt). A stray "g8a 5k 500lev 6pt" block in g8_summary_12Oct2026.txt is from another session, unverified.
- Notes: HUB_STATE.md (my results section appended). Analysis CSV of g4b trades was in my scratchpad only (not needed).

## My helpers (all STOPPED via stop files; scripts kept in Signal\scripts, safe to ignore or delete later)
Keep-MT4Visible.ps1, Guard-System.ps1, Keep-ClaudeEfficient.ps1, MT4Ctl.ps1, Watch-Processes.ps1 (log-only duplicate of ram_guard_v1), run_g7_12Oct2026.ps1, run_g8_12Oct2026.ps1. Silent flag mt4_silent.flag left in place.

## UPDATE (reported by the coordinator session "Phone Android Signal"; NOT verified by this session) - the "pending" items below were later run
- g7c (ADX22) PF 1.665 and g7d (ADX26) PF 1.747: both pass the gate.
- g7a at spread 6: PF 2.04 (unexplained: higher than the spread-3 result of 1.953, so treat with suspicion).
- g7a on 2022 H1: PF 1.885. g7a on 2015 / 2016 / 2018: FAILED all three (PF 0.70 / 0.59 / 0.70).
- ADX sweep 20-26: rejected under the pre-fixed rule. => g7a is NOT validated; it fails the choppy years. Full results are in HUB_STATE.md (committed in 7eed730).
- Still true: 2023-2025 history is missing; any further MT4 work needs Nasif's go and about 1.0 GB free RAM.

## Pending / not done (as of my last check - see UPDATE above)
- g7c, g7d, g7a at spread 6/8pt, g7a on unseen years: need MT4 (paused; hst_out watcher disarmed; needs free RAM >= 1.0 GB and Nasif's go).
- Missing history 2023-2025: tick download to D:\ticks (one 3-month chunk first, RAM >= 1.5 GB). QuotesDownloader not running.
- Rule from Nasif: no MT4/test starts without his yes; MT4 runs minimized+silent; routines all disabled (19 cloud routines show enabled=false; no local scheduled tasks).
