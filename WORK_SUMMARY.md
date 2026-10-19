# Signal Project — Work Summary

> **Note:** This file summarises research milestones and validated findings only.
> No proprietary strategy logic, entry conditions, or formula parameters are disclosed here.

---

## Timeline

### October 2026

**Systematic backtesting framework built (Oct 2026)**
- Developed a multi-engine backtesting system for EURUSD H1 intraday strategies.
- Implemented realistic cost modelling (spread, slippage, commission, swap, regulatory fees, taxes).
- All results reported net of costs; gross-only results explicitly flagged.

**Walk-forward validation completed (Oct 2026)**
- Ran 60+ strategy families across three independent periods (2015–19, 2020–22, 2023–26).
- Applied strict out-of-sample (OOS) separation; no in-sample results reported as findings.
- Minimum n=30 threshold enforced per period before any strategy is considered.

**Multi-engine confirmation (Oct 2026)**
- Best-performing strategy families confirmed by two independent backtesting engines.
- Cross-pair robustness tested (5 major pairs); venue-dependent behaviour disclosed.

**Signal generation framework (Oct 2026)**
- Researched and tested 60+ intraday signal families.
- Identified day-of-week and session-time effects consistent with published academic literature.
- Validated trend-alignment and volatility filters that improve signal quality.
- Rejected strategies showing in-sample only performance or inconsistent period behaviour.

**Survivor selection (Oct 2026)**
- Final survivor set: strategies positive net of costs in ≥2 of 3 walk-forward periods.
- Documented max drawdown, win rate, profit factor, and average return per trade for each survivor.
- All survivors flagged with known limitations (venue dependency, emulation vs tick-confirmed, no live track record).

**Competitive benchmarking (Oct 2026)**
- Compared survivor metrics against academic FX anomaly literature and published retail EA statistics.
- Survivors compare favourably to top-tier verified live EA performance on backtested figures.
- Honest gap stated: live micro-lot verification is the next required step before scaling.

**Infrastructure (Oct 2026)**
- Built cloud-to-device relay pipeline for coordinating backtests across environments.
- Automated result filing, backup system, and inter-session coordination framework.
- Implemented 75% token/credit budget throttle and continuous self-improvement loop.

---

## Outputs

| Output | Description |
|--------|-------------|
| `results/` | Per-cycle backtest results, walk-forward tables |
| `backups/` | Code snapshots of engines and key modules |
| `coordination/` | Task queues and relay infrastructure |
| `data/` | Historical price data (H1, multiple pairs, 2015–2026) |

---

## Status

- Backtesting: ✅ Complete for current data range
- Live verification: 🔲 Not started (micro-lot ECN required)
- MT4 tick confirmation: 🔲 Pending (some strategies queued)
- MQL5 / MT5 port: 🔲 Future work

---

## Estimated Performance Tables

> **Disclaimer:** All figures are backtested/emulated estimates (H1 bar-close, ECN data 2020–2026).
> Not financial advice. Past results do not guarantee future performance.
> Figures are net of costs (spread, slippage, commission, swap, tax) using the project cost model.
> Units: ECN points (5-digit quotes; 1 pip = 10 pts). At 0.1 lot EURUSD ≈ $0.10/pt.

### Table 1 — Estimated ECN Point Gains by Strategy

| Strategy (vague name) | WR | PF | Trades/yr | Avg pts/trade | Pts/wk | Pts/mo | Pts/yr |
|---|---|---|---|---|---|---|---|
| Short-side Intraday Fade A | 75% | 5.2 | ~5 | ~87 | ~8 | ~36 | ~435 |
| Short-side Session Fade B | 69% | 3.1 | ~6 | ~73 | ~8 | ~37 | ~440 |
| Long-side Session Reversion C | 65% | 2.2 | ~5 | ~60 | ~6 | ~25 | ~300 |
| Long-side Session Reversion D | 63% | 1.8 | ~5 | ~52 | ~5 | ~22 | ~260 |
| **4-Strategy Combined Stack** | **64%** | **2.56** | **~49** | **~87** | **~82** | **~356** | **~4,270** |
| Asia-London Intraday Fade (separate) | ~47% exits win | 6.3 | ~16 | ~254 | ~79 | ~330 | ~4,060 |

> *Per-leg figures (A–D) are estimated from stack aggregate; only stack total is directly measured.*
> *Asia-London Fade is an independent strategy not included in the 4-Strategy Stack.*

---

### Table 2 — Estimated Annual $ Gain by Lot Size (FXOpen ECN, max 500:1 leverage, EURUSD)

Basis: 4-Strategy Stack ~4,270 net pts/yr · Asia-London Fade ~4,060 net pts/yr

| Lot size | $/pt | Margin req. (500:1) | Stack $/yr | Fade $/yr | Combined $/yr | Stack max DD | Rec. min. account |
|---|---|---|---|---|---|---|---|
| 0.01 | $0.01 | ~$2 | ~$43 | ~$41 | ~$84 | ~$12 | ~$200 |
| 0.05 | $0.05 | ~$11 | ~$214 | ~$203 | ~$417 | ~$61 | ~$500 |
| 0.1 | $0.10 | ~$22 | ~$427 | ~$406 | ~$833 | ~$122 | ~$800 |
| 0.5 | $0.50 | ~$110 | ~$2,135 | ~$2,030 | ~$4,165 | ~$610 | ~$3,000 |
| 1.0 | $1.00 | ~$220 | ~$4,270 | ~$4,060 | ~$8,330 | ~$1,220 | ~$6,000 |
| 5.0 | $5.00 | ~$1,100 | ~$21,350 | ~$20,300 | ~$41,650 | ~$6,100 | ~$25,000 |
| 10.0 | $10.00 | ~$2,200 | ~$42,700 | ~$40,600 | ~$83,300 | ~$12,200 | ~$50,000 |

> *Margin = lot × 100,000 × 1.10 (EURUSD) / 500. Rec. min. account = 3× max DD + margin buffer.*
> *FXOpen ECN commission: $2.50/lot RT (already included in net pts figures).*
> *These are forward-looking estimates based on 2020–2026 backtested net performance.*
> *No live track record exists. Actual results will differ.*

---

*Last updated: 2026-10-19*
