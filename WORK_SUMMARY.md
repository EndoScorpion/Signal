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

*Last updated: 2026-10-19*
