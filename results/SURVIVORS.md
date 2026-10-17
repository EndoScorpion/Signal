# SURVIVORS — net-of-cost backtest (2026-10-17)

Universe: SPY QQQ ULTY AAPL MSFT JPM KO XOM GLD SLV (10 symbols)
Hold: 3 days | Cost/round-trip: 0.083% | Tax (short-term gains): 24%
Periods: 2015-19, 2020-22, 2023-26 (15y Yahoo data)
Pass criteria: n≥30 AND after-tax avg >0 in ≥2 of 3 periods

---

## SURVIVORS

### S2 — RSI<25  ✓ PASS
| Period  |   n | Win% | Avg net% | Avg after-tax% |
|---------|-----|------|----------|----------------|
| 2015-19 | 156 | 48.7 | +0.330   | **+0.065**     |
| 2020-22 | 108 | 53.7 | +0.193   | -0.178         |
| 2023-26 | 147 | 56.5 | +0.624   | **+0.238**     |

Positive after-tax in 2 of 3 periods, n≥30 in all. Negative 2020-22 (COVID volatility era — large drops that didn't recover in 3 days). Edge is thin; consistent direction.

---

## REJECTED

| Rule | Reason |
|------|--------|
| S1 RSI<30 & below BB | After-tax negative in 2/3 periods (2015-19: -0.027%, 2020-22: -0.199%) |
| S3 3d-5% & 10d-10% dip | After-tax -1.259% in 2020-22 (large dips kept falling); n=24 in 2015-19 |
| S4 below BB & Stoch<10 uptrend | n<30 in all 3 periods (max n=20) — insufficient data |

---

## BASE (buy-and-hold 3d, all days)
| Period  |    n | Win% | Avg net% | Avg after-tax% |
|---------|------|------|----------|----------------|
| 2015-19 | 11322| 53.0 | +0.060   | -0.119         |
| 2020-22 | 6804 | 52.8 | +0.069   | -0.219         |
| 2023-26 | 9190 | 54.0 | +0.114   | -0.128         |

Base is after-tax negative in all periods — tax drag kills random 3-day holds. S2 edges above base in 2015-19 and 2023-26.

---

## NEXT STEPS
1. Patch app_addons rules to add S2 (RSI<25 signal, 3-day hold).
2. Walk-forward validation: tune on oldest 60% (2015-20), validate 2021-23, final test 2024-26 untouched.
3. Expand universe (more symbols) to increase S2 signal count and reduce per-symbol concentration.
4. Consider longer hold (5-7d) for dip rules — 2020-22 failures may be a 3d-too-short issue.

---
*All results are estimates net of costs + tax. NOT approved for live trading. Past results are not advice.*
