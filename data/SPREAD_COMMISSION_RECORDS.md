# FXOpen EURUSD 5-digit ECN - spread and commission records and cost logic (Nasif Hossain, backed up 2026-10-13)

## Commission (confirmed from Nasif's live account history; round trip, points per 0.01 lot ~ pts)
- 2023 to early 2024: -$0.05 per 0.01 lot = 5 pts
- 2025 to 2026 (current): -$0.08 per 0.01 lot = 8 pts
- For a long stretch before: 6 pts was the maximum. Commission varies with account balance tier and FXOpen rule changes.
- Nasif's rule (2026-10-13): at low volume assume the LOWEST confirmed rate, 5 pts (or lower if found in account history). Claude may read the commission history from the account, read-only.
- 5 pt commission max audit: realistic-cost pass re-tests candidates at 5 pts commission + that year's average real spread.

## Real spread from FXOpen M1 bid/ask (ask close - bid close, points; script data/spread_stats.py, table data/spread_stats.csv)
2009-2018: ask == bid in the downloaded files (spread reads 0): UNUSABLE. Real data from 2019.
| year | minutes | mean pts | median | p90 | <=2 pts | <=5 pts |
|---|---|---|---|---|---|---|
| 2009 | 364428 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2010 | 367194 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2011 | 369019 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2012 | 369878 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2013 | 368613 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2014 | 367334 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2015 | 370886 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2016 | 373151 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2017 | 370355 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2018 | 372438 | 0.0 | 1 | 1 | 100.0% | 100.0% |
| 2019 | 368338 | 4.81 | 4 | 5 | 1.4% | 71.1% |
| 2020 | 366642 | 3.72 | 2 | 5 | 31.9% | 85.8% |
| 2021 | 371039 | 3.97 | 2 | 4 | 17.3% | 90.0% |
| 2022 | 370249 | 3.5 | 2 | 5 | 36.8% | 83.4% |
| 2023 | 369058 | 1.67 | 1 | 2 | 78.5% | 95.8% |
| 2024 | 370904 | 1.4 | 1 | 2 | 82.9% | 96.5% |
| 2025 | 371171 | 2.36 | 1 | 2 | 81.5% | 94.9% |
| 2026 | 282731 | 2.87 | 1 | 2 | 80.0% | 94.3% |

Mean spread by UTC hour (CSV clock; NOT server hour), 2023-2026 (pts): 0:1.3 1:1.2 2:1.2 3:1.1 4:1.1 5:1.2 6:1.1 7:1.1 8:1.0 9:1.0 10:0.9 11:0.9 12:1.1 13:1.1 14:1.0 15:0.9 16:1.0 17:1.1 18:1.1 19:1.1 **20:2.5 21:17.1 22:7.7** 23:1.6 -> in MT4 server time (UTC+2, UTC+3 in US DST) the spike is about 22:00-01:00, peak 23:00-00:00: avoid new entries in server hours 23-01.
Tick sample with real bid/ask: D:\fxopen_eurusd_ticks (2020-08-10 to 2021-08-18, ask-bid gives tick-level spread).

## Cost logic used in tests
- MT4 tester takes ONE fixed Spread value (run_tester.ps1 -Spread). Convention in these records: Spread = total round-trip cost in points.
- Screen tests (data/auto_loop.py): flat sp5 (5 pt commission, floor assumption). Older numbers at sp6/sp8 on partial history are invalid.
- Realistic pass: real_sp(year) = 5 commission + round(that year's mean real spread, clipped 1..5); years before 2019 use the 2019-2026 average. Values: 2013/15/16/18 = 8, 2019 = 10, 2020 = 9, 2023 = 7, 2024 = 6, 2025 = 7, 2026 = 8.
- Honest total cost = commission + spread. Spread-alone sp2 is not realistic (commission alone is 5). MT4 cannot use variable spread; MT5 custom symbol / real ticks can (run_tester_mt5.ps1, csv_to_mt5.py).
- Offline lab costs: 5 pts + hourly mean spread (scalp_lab.py, shadow_audit.py). Scalp finding: 7-10 pt targets do not pay at a 5 pt commission (break-even hit rate 91-99% vs 70-83% achieved).
- MT4 offline spread issue: symbols.raw holds the symbol spread; when MT4 is offline the tester can fall back to a corrupt default. patch_mt4_spread.py sets EURUSD spread (record size 1936, spread at offset 284); EURUSD was already 6 pts. symbols.raw is backed up with the history.

## Files (all backed up under spread_commission\ on the stick)
spread_stats.py, spread_stats.csv, patch_mt4_spread.py, parse_results.py (commission tag/logging), auto_loop.py (real_sp, loop), scalp_lab.py, shadow_audit.py, run_tester.ps1, run_tester_mt5.ps1, csv_to_hst.py, csv_to_mt5.py, memory note feedback_commission_fxopen.md, symbols.raw.

## Swap (checked 2026-10-13)
- FXOpen pages state swap-free Islamic accounts exist; FXOpen support says for those the commission equals the swap (no saving). No low-swap ECN offer could be confirmed; Nasif previously had a low/no-swap account and is unsure it is still offered. FXOpen's public (INT) pricing page lists ECN FX commission per lot by balance (below 1k: 3.50, 1k-25k: 2.50, 25k-250k: 1.80, over 250k: 1.50), which differs from the FXOpen EU account's observed 5-8 pts round trip: confirm EU pricing with FXOpen support.
