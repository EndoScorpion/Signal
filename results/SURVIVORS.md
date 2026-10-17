# Signal Backtest Survivors — Net of Costs
*Run: 2026-10-17 | Data: data/history/*.csv (Oct 2026) | Hold: 3d | Cost: cost_model.json (0.083% round trip)*

> ⚠️ Data source: existing CSVs (Webull/Yahoo fallback — NOT FXOpen ECN). Per standing rule, these results are **reference tier only** for any EURUSD EA work. For stocks/ETFs/metals this is the primary source.

---

## SURVIVORS (positive net ≥2/3 periods, n≥30)

### BASE — Buy-and-hold 3d baseline
| Period | n | Win% net | Avg gross | Avg net | Avg after-tax | Max DD |
|--------|---|----------|-----------|---------|---------------|--------|
| 2020-22 | 495 | 56.0% | +0.448% | +0.365% | +0.051% | 68.88% |
| 2023-26 | 9133 | 55.2% | +0.279% | +0.196% | -0.053% | 249.43% |

**Verdict:** Marginal — net positive in 2/2 periods measured, but after-tax turns negative in 2023-26. Baseline only; no edge over index hold.

---

## REJECTED (n<30 or inconsistent periods)

| Rule | Reason | Best period result |
|------|--------|--------------------|
| S1 RSI<30 & below BB | n<30 in 2020-22 (n=2) | 2023-26: win 57.7%, avg net +0.765% (n=123) |
| S2 RSI<25 | n<30 in 2020-22 (n=4) | 2023-26: win 56.8%, avg net +0.803% (n=132) |
| S3 3d-5% & 10d-10% | n<30 across periods (n=30 only in 2023-26) | 2023-26: win 63.3%, avg net +1.093% (n=30) |
| S4 below BB & Stoch<10 in uptrend | n<30 across periods (n=14 in 2023-26) | 2023-26: win 71.4%, avg net +1.382% (n=14) |

**Note:** S1-S4 show promising signals in 2023-26 but lack sufficient trade counts in earlier periods to confirm consistency. S4 has the highest win rate (71.4%) and net return (+1.382%) but only n=14 — needs more history or a broader universe to confirm.

---

## Key findings
- Cost per round trip: **0.083%** (spread 0.04% + slippage 0.04% + reg fees 0.003%)
- Tax drag (short-term 24%): largest cost — reduces +0.365% net to +0.051% after-tax in 2020-22
- No rule clears the n≥30 + positive-net-in-≥2-periods bar except BASE
- S4 (BB+Stoch uptrend) is the most promising candidate — needs wider universe to reach n≥30

## Recommended next steps
1. Expand universe (add 20-50 stocks) to increase n for S1-S4
2. Re-run with crypto_universe.txt — crypto rules had prior positive signals (H1 dip-rebound)
3. S4 specifically: backtest on full S&P500 universe to get n≥100
