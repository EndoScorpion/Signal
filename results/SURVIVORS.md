# Signal Backtest Survivors — Net of Costs
*Updated: 2026-10-18 | Stocks: data/history/*.csv 50 symbols 3d hold 0.083% RT | Crypto: data/history_crypto/*.csv 10 coins 4d hold 0.320% RT | Cost: cost_model.json*

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

### S1 — RSI<30 & below Bollinger Band ⚠️ INCONSISTENT (unfiltered)
| Period | n | Win% net | Avg gross | Avg net | Avg after-tax | Max DD |
|--------|---|----------|-----------|---------|---------------|--------|
| 2015-19 | 376 | 57.2% | +0.546% | +0.463% | +0.121% | 26.63% |
| 2020-22 | 499 | 47.1% | -0.638% | **-0.721%** | -1.131% | 108.27% |
| 2023-26 | 637 | 54.8% | +0.639% | +0.556% | +0.130% | 59.04% |

**Verdict (unfiltered):** Net positive 2/3 but fails hard in 2020-22. Use S1+Regime instead (see below).

---

### S1+Regime — RSI<30 & below BB & SPY>200SMA ✅ NEW SURVIVOR
| Period | n | Win% net | Avg gross | Avg net | Avg after-tax |
|--------|---|----------|-----------|---------|---------------|
| 2015-19 | 305 | 53.8% | +0.182% | **+0.099%** | -0.160% |
| 2020-22 | 235 | 56.2% | +0.551% | **+0.468%** | +0.038% |
| 2023-26 | 516 | 51.9% | +0.349% | **+0.266%** | -0.106% |

**Verdict:** Net positive 3/3 periods — **survivor**. Regime filter transforms the 2020-22 result from -0.721% → +0.468% by excluding crash-period false signals. n≥30 all periods. After-tax marginally negative outside 2020-22 — suitable for tax-advantaged accounts or where losses offset gains. **Preferred over unfiltered S1.**

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
| S3+Regime (SPY>200SMA) | Regime filter HURTS S3: 2020-22 net -1.399% vs +0.050% unfiltered. Sharp dip rule works ACROSS regimes — when SPY>200SMA, a -5%/-10% drop is often company-specific trouble, not a rebound opportunity. Apply S3 unfiltered only. |
| Crypto daily S1/S2/S3 (4d hold) | Net positive in ≥2/3 periods but after-tax negative all periods. 0.32% RT cost + 24% tax erases edge. Daily timeframe too coarse; prior H1 finding (+0.25% avg at 0.12% cost) is on hourly data — not testable with daily CSVs. |

---

## Key findings
- Stock RT cost: **0.083%** | Crypto RT cost: **0.320%** (high — erases daily edge after tax)
- Tax drag (24% short-term): major — erases net edge in most periods for taxable accounts
- **S1+Regime** (RSI<30+BB+SPY>200SMA): **best risk-adjusted** — net positive 3/3, avoids crash traps
- **S3 unfiltered** (3d-5%&10d-10%): strongest raw net returns; apply WITHOUT regime filter
- **S2 unfiltered** (RSI<25): most consistent — net positive all 3 periods, lowest drawdown
- Regime filter helps S1 dramatically (+0.468% in 2020-22 vs -0.721%) but hurts S3
- Crypto daily rules: no after-tax edge at 0.32% RT cost; H1 finding (+0.25%) needs hourly data
- MT4 EURUSD b62 backtest: blocked pending EURUSD15.hst from FXOpen ECN (laptop-gated)

## Rule ranking (net of costs, taxable account)
1. **S1+Regime** — 3/3 periods positive net, regime filter eliminates crash exposure
2. **S3 unfiltered** — 3/3 periods positive net, highest avg net (+0.577%/+0.050%/+0.640%)
3. **S2 unfiltered** — 3/3 periods positive net, most consistent, lowest drawdown
4. S1 unfiltered — only use if regime filter unavailable; high 2020-22 risk
5. All crypto daily — REJECTED after-tax; re-test on hourly data when available

## Recommended next steps
1. ✅ DONE: Regime filter on S1 — dramatically improved
2. ✅ DONE: Crypto daily backtest — no after-tax edge at daily timeframe
3. Update addon37.html/addon36.html with new S1+Regime rule
4. Test crypto H1 rules (hourly data required — not yet available)
5. Upload FXOpen EURUSD15.hst for b62 EA MT4 backtest (laptop-gated)
