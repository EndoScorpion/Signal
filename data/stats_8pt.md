# 8-pt rescore + multiple-testing bar - 2019 IN-SAMPLE (signal-a2)

Method: tools\stats_8pt.py. Raw prices only: sell pts = (open - close)/0.00001 from report fill/exit prices (exit already includes spread 3), commission 8 pts charged once, 0.01 lot = $0.01/pt, never the report's profit column. DD = closed-trade peak-to-trough, % of $10,000. Day-block bootstrap (5000 resamples of close-day nets). Cross-check: net @6 reproduces +146.82 (g2a) and +121.80 (g1a) exactly.

| report | trades | open at end | win % @8 | PF @8 | net @8 $ | max DD @8 $ (% of 10k) | day-block p(net<=0) @8 | days | net @6 $ (check) |
|---|---|---|---|---|---|---|---|---|---|
| g2a 2019 M1 sp3 | 403 | 0 | 57.1 | 1.26 | 138.76 | 105.96 (1.1%) | 0.183 | 93 | 146.82 |
| b20legs_g1a 2019 M1 sp3 | 670 | 0 | 54.0 | 1.11 | 108.40 | 192.52 (1.9%) | 0.347 | 103 | 121.80 |

Both pass PF >= 1.10 and DD < 5% at 8 pts, but IN-SAMPLE only, and neither is distinguishable from luck at day level (p 0.18 and 0.35).

## How many things we have looked at (documented, approximate)

| family | count |
|---|---|
| strategy variants scored on 2019 M1: b12_ladder12 / b20legs / b12_bracketreg x g1a, g1b (6) + g2a (1) | 7 |
| variants specified/queued or screened: g2b, g2c, g2d, g2e, g3a | 5 |
| TP/SL grid on g1a 2019: 4 TP x 3 SL (12), plus SL500 (4) | 16 |
| hour-block cuts: six 4-hour blocks x ~3 branch types (pending sell, hedge, ladder), approximate | ~18 |
| **total looks, IS (upper bound)** | **~46** |
| **candidates actually carried to the 2021 OOS test: g1a, g2a, g2b, g2c, g2d (5) + 16 TP/SL combos** | **21** |

Because the candidate list is fixed BEFORE the OOS run, the OOS p-values are clean and only need correction over the OOS candidates (m = 21). The ~46 IS looks explain why an IS winner is probably selection luck, and why IS p-values are not usable.

## Bar for the 2021 out-of-sample winner (one line)
A winner needs day-block p(net<=0) at 8 pts <= 0.05/21 = 0.0024 (Bonferroni, m=21; Holm: smallest p <= 0.0024, next <= 0.0025, ...), PLUS PF >= 1.10 and DD < 5% at 8 pts and win % above baseline; use 0.05/46 = 0.0011 if you count all IS looks. A single 2021 window (~190 days) may be too short to reach this, so pool 2021 + 2012 + 2011 OOS days before concluding.
