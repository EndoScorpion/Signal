# Signal Handoff — 15 Oct 2026 session 2

## Status
Loop running. Silent mode. Sonnet 4.6 max.

## Work completed this session
- **D v2 CSV**: `data/D_trades_export.csv` — 457 trades, L1 exit (trail400/250 SL750 hold900min), all columns. Session session_01SeGDro1DcUkE6YSJ4yMRGY not found; coordinator notified.
- **Hash analysis** (`data/loss_hash.py`): Top loss buckets H09_Thu (-170 avg n=13), Thu_flat (-172 n=15), Nov (-93 n=32), h11 (-158 n=10).
- **Progressive filter stack**: BASE +26,244 → +skip_H09Thu +skip_Nov +skip_h11 = **+33,815 pts** (64.0% wr, 83% yrs+, +7,571 vs base).
- **MT4 queue** (`data/extra_candidates.json`): 4 new clones — skip_H09Thu_trail400_250, skip_Nov_trail400_250, skip_h11_trail400_250, skip_h04_trail400_250.
- **Liq/broker/bank** (`data/liq_broker_news.py`): Regulation events hurt (-99 avg). November structural loss NOT explained by macro catalog. Crypto crashes help (risk-off).
- **Improvement sim2** (`data/improvement_sim2.py`): FOMC genuinely 0 effect. G_best_combo (skip h11+h04) = +27,266 (+1,022 vs base).

## Pending
- Coordinator (session_01DyMXgM2RA1Uqvs7DWmeiy1) wants Task 1: cloud_G_newscross_v2.py — awaiting script paste.
- MT4 clones running one at a time per CLAUDE.md rule.
- Years 2011, 2014, 2023 still negative across all filters — unresolved.
- DSR/bootstrap on H09_Thu and November filters needed before MT4 promotion.

## Key files
- `data/D_trades_export.csv` — per-trade CSV for cloud D v2
- `data/loss_hash.txt` — full hash output
- `data/extra_candidates.json` — MT4 queue
- `data/improvement_sim2.txt` — improvement sim results
- `data/ANOMALY_RESEARCH_15Oct.md` — full anomaly log

## Rules in effect
- 6 pts FXOpen ECN (not 8pt default)
- First tests max 5 pts, 500 lev
- Report in pts ($/0.16)
- Win rate target 95%
- Never live trade
