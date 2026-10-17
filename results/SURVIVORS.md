# Signal Backtest Survivors — Net of Costs
*Run: 2026-10-17 | Data: data/history/*.csv (Oct 2026) | Universe: 50 symbols (expanded) | Hold: 3d | Cost: cost_model.json (0.083% round trip)*

> ⚠️ Data source: Yahoo Finance fallback via fetch_history.py — NOT FXOpen ECN. Per standing rule, these results are **reference tier only** for any EURUSD EA work. For stocks/ETFs/metals this is the primary source.

---

## SURVIVORS (positive net ≥2/3 periods, n≥30 all periods)

### BASE — Buy-and-hold 3d baseline
| Period | n | Win% net | Avg gross | Avg net | Avg after-tax | Max DD |
|--------|---|----------|-----------|---------|---------------|--------|
| 2015-19 | 29052 | 53.3% | +0.190% | +0.107% | -0.134% | 730.16% |
| 2020-22 | 29429 | 50.5% | +0.142% | +0.059% | -0.335% | 890.46% |
| 2023-26 | 47053 | 52.3% | +0.281% | +0.198% | -0.132% | 1169.11% |

**Verdict:** Marginal — net positive 3/3, but after-tax negative all periods. Baseline only; no edge.

---

### S1 — RSI<30 & below Bollinger Band ⚠️ INCONSISTENT
| Period | n | Win% net | Avg gross | Avg net | Avg after-tax | Max DD |
|--------|---|----------|-----------|---------|---------------|--------|
| 2015-19 | 376 | 57.2% | +0.546% | +0.463% | +0.121% | 26.63% |
| 2020-22 | 499 | 47.1% | -0.638% | **-0.721%** | -1.131% | 108.27% |
| 2023-26 | 637 | 54.8% | +0.639% | +0.556% | +0.130% | 59.04% |

**Verdict:** Net positive 2/3 periods — **technically survives filter** but fails hard in 2020-22 (-0.721% net). High variance. The 2020-22 crash environment triggered many false oversold signals. Use with extreme caution; consider regime filter before live use.

---

### S2 — RSI<25
| Period | n | Win% net | Avg gross | Avg net | Avg after-tax | Max DD |
|--------|---|----------|-----------|---------|---------------|--------|
| 2015-19 | 468 | 56.8% | +0.456% | +0.373% | +0.029% | 31.99% |
| 2020-22 | 555 | 52.4% | +0.103% | +0.020% | -0.455% | 57.07% |
| 2023-26 | 822 | 50.6% | +0.341% | +0.258% | -0.130% | 66.98% |

**Verdict:** Net positive 3/3 periods — survivor. Marginal in 2020-22 (+0.020%). After-tax turns negative in 2020-22 and 2023-26. Net edge exists but tax drag erases it for taxable accounts. Best suited for tax-advantaged accounts or tax-loss harvesting.

---

### S3 — 3d-5% & 10d-10% (sharp dip)
| Period | n | Win% net | Avg gross | Avg net | Avg after-tax | Max DD |
|--------|---|----------|-----------|---------|---------------|--------|
| 2015-19 | 150 | 56.0% | +0.660% | +0.577% | +0.069% | 37.90% |
| 2020-22 | 527 | 48.4% | +0.133% | +0.050% | -0.742% | 201.12% |
| 2023-26 | 439 | 52.2% | +0.723% | +0.640% | -0.063% | 76.99% |

**Verdict:** Net positive 3/3 periods — survivor. Strongest net returns (+0.577%, +0.050%, +0.640%). However after-tax heavily negative in 2020-22 (-0.742%) — crash environment causes large losses that aren't offset (conservative tax model). Pre-tax this is the best rule; after-tax requires regime awareness.

---

## REJECTED

| Rule | Reason |
|------|--------|
| S4 below BB & Stoch<10 in uptrend | Net positive 1/3 periods only (2015-19 only; 2020-22: -0.295%, 2023-26: -0.084%) |

---

## Key findings
- Cost per round trip: **0.083%** (spread 0.04% + slippage 0.04% + reg fees 0.003%)
- Tax drag (short-term 24%): major cost — erases edge in most scenarios for taxable accounts
- **S3 (sharp dip)** is the strongest net rule: +0.577%/+0.050%/+0.640% across periods
- **S2 (RSI<25)** is most consistent: net positive all 3 periods, low drawdown
- **S1 (RSI<30+BB)** survives filter but is dangerously inconsistent — 2020 crash produced -0.721% net
- S4 rejected — does not hold across regimes
- All rules fail after-tax in taxable accounts during 2020-22 crash period

## Recommended next steps
1. Add regime filter to S1/S3 (e.g., SPY > 200-day SMA = uptrend only) — expected to improve 2020-22 results
2. Run crypto universe backtest (`crypto_universe.txt`) — prior H1 dip-rebound signals showed promise
3. Test S3 on individual sectors (XLK, XLF, XLE) to find highest-signal subsectors
4. Consider tax-advantaged implementation (IRA/401k) to recapture after-tax edge
5. Upload FXOpen EUR/USD QuotesDownloader data for EURUSD EA work (laptop-gated)
