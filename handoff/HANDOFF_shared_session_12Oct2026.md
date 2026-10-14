# Handoff: Shared session (Phone Android2), Signal repo, 12 Oct 2026
Written by the Shared session (Sonnet 5.5 low). Nothing deleted. Read HUB_STATE.md for full results.

## Where the win logic and tests live (do not lose)
- EA sources: C:\Users\endos\Signal_copy\*.mq4 (33 files) and a copy in Signal\ea_backup_12Oct2026\ (git commit 7eed730, local, NOT pushed).
- Families: Strong2010b_claude_g4b (baseline, gate PASS PF 1.460), g6a-e, g7a-d/g7n (BlockADX), g5, g8-g10, ChopBracket_h1a-d (+_brk) tests.
- Gate: analysis\oos_check.py (PASS = PF>=1.10, DD<=5%); scripts\run_oos_gate_v3/v4, compile_and_gate_v2/v3 (carry MT4 pause guards).
- Results: HUB_STATE.md, data\*_summary_12Oct2026.txt, data\*.htm reports.

## Findings (all in-sample unless stated)
- g4b PASS 2021 (PF 1.460, 182 trades). g7a BlockADX=24 PF 1.953 (tuned, NOT validated): passes 2022 H1 (PF 1.885) but FAILS choppy 2015/2016/2018 (PF 0.70/0.59/0.70).
- ADX sweep 20/22/24/26 rejected by a rule fixed in advance. ChopBracket h1a-h1d (Bollinger/ADX/CCI/ATR/volume bracket) all FAIL PF 1.10 on 2016; best fade h1c wins 67% but payoff ratio keeps PF<1.
- History coverage gaps: 2013-2015, 2017-2018, 2020 partial; 2023-2024 missing; 2025 28%.

## Rules everyone follows
- MT4 stays paused (MT4_PAUSE / MT4_Backtest\PAUSE) until Nasif says resume; needs >=1.0 GB free RAM (1.5 GB for tick download or new CLI).
- Keep at most 3 recent backup duplicates of anything; archive older duplicates, never delete without Nasif's yes.
- ALWAYS keep unique win logic, entry/filter logic, money management, analysis methods and self-improvement instructions for clone agents and EAs. Backups of these are never "duplicates" to drop.
- Tune only on tuning years; run the holdout once; no live trading; no logins/passwords in chats.
- Phone link: keep the Shared session and remote-control process (PID 4200) active, both ways.

## Pending (needs Nasif's go + RAM)
- Tick/history download to D:\ticks, one 3-month chunk first. Cost rule decision (6 vs 8 pts). Possible 2021 OOS for g2/g3 line (separate project).
