# RED ZONES - conditions where base b31 (WIN_GEN1 ZGate+DailyRange) sell entries lose
Started 2026-10-13. EURUSD M15, sp5, years 2015/2018/2023/2024 (avg pnl per trade in $ at 0.01-lot-scaled sim, n in brackets where known).
Status: REPLAY LEADS ONLY. Not a gate until confirmed in the MT4 tester on the 8 training periods and other markets/brokers. Backtest never = live approval.

| Zone | 2015 | 2018 | 2023 | 2024 | Same sign 4/4 | Closest EA input | Status |
|---|---|---|---|---|---|---|---|
| Stochastic K14 > 80 | -25.9 | -25.3 | -23.6 | -49.3 | yes | UseWprGate=1 (w_wpr1_20) | queued in auto_loop |
| Price in upper 38% of 5-day range (fib > 0.618) | -12.6 | -18.3 | -26.2 | -14.6 | yes | none (needs EA edit) | untested |
| NFP day (first Friday) vs other days | -18.4 vs -2.1 | -6.7 vs -6.0 | -29.1 vs -11.2 | -6.5 vs -4.8 | yes | UseNewsDayBlock (n_newsday) | queued |
| High ATR14 tercile | -7.6 | -17.1 | -29.4 | -19.7 | yes | MaxRangeAtrMultiplier (d_range_tight) | queued |
| Fast/slow slope: aligned or diverged/converging | mixed | negative | negative | negative | mostly | none (needs EA edit) | only diverged/diverging ~breakeven |
| Sell regime OFF (control) | - | - | -7416 vs base -3998 | - | n/a | UseSellRegime | regime rule is protective |

Cost red zone (computed from real M1 bid/ask, data/spread_stats.csv): UTC hours 20-22 (the CSV clock). In MT4 server time (UTC+2, UTC+3 in US DST) the rollover spread spike is about 22:00-01:00 with the peak 23:00-00:00 (spike (avg spread hour 21 = 17 pts, hour 22 = 7.7, hour 20 = 2.5 vs ~1 pt otherwise, 2023-26). Avoid new entries in SERVER hours 23-01 (UTC 21-22). Pre-2019 spread data is zero in the files (unusable).

Not stable / no conclusion: volume, 20-bar range, psychological 0.0050 levels, S/R distance (too few near-level entries).
Still to track: real news/events calendar, CFTC COT positioning (weekly), slope std-dev bands, convergence timeline (data/convergence_timeline.csv).
Update rule: after each loop pass or new replay, edit this table; mark a zone CONFIRMED only after training-period MT4 tests and multi-market/broker checks (MMR proof gate).
Scripts: data/level_replay.py, state_filter_replay.py, convergence_map.py, slope_map.py, auto_loop.py.
