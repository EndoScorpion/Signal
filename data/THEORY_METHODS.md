# One theory method per Claude clone (Nasif 2026-10-15: each clone uses a different method, no overlap)

Claim a method on the job board before working: `python -E -P data\agent_board.py claim <ID> <your_name>`. One clone per method.
Rules: new versioned EA files only (b64 and up, next free number), old EA files never edited, compile only, never start MT4 or a second loop,
queue candidates at the FRONT of data\extra_candidates.json (backup first, append/reorder only), no live orders.
Name candidates with your method prefix so results can be traced. Log each theory as one line in data\theory_log.csv:
`time,method,owner,candidate,theory,status` (status: queued / tested / passed / failed). Results for every run: data\results_summary.csv (auto, every 30 min).

| Method | Prefix | Owner | What it uses to find theories |
|---|---|---|---|
| A. Loss-cluster analysis | th64_, lc_ | Backtest status check thread (claimed) | Where losses bunch (weekday, hour, ATR bucket, slope stack), then gates/exits that remove those buckets |
| B. Regime and volatility gates | rg_ | open | Hurst, variance ratio, ATR/BB percentiles, H1/H4/D1 regime, vol-of-vol |
| C. Entry-trigger variants | en_ | open | z period/trigger, Kalman z, turn confirm, multi-timeframe z agreement |
| D. Exit and trailing logic | ex_ | open | z-revert exit, ATR trail, partial TP, time exit length, breakeven |
| E. Position sizing and balance tiers | sz_ | open | confidence sizing, lot cap, FXOpen tier balances at 500:1, drawdown-scaled lots |
| F. Session and time filters | ss_ | open | hour masks, rollover, London/NY overlap, news-day skip, month/quarter seasonality |
| G. Phone subagents | ph_ | open | Read results_summary.txt only and propose theories as board notes (no files changed on the PC) |
