# Adaptive Zero-Trade Logic — Audit & Cloud Emulation Test
**Date:** 2026-10-19  |  All figures in ECN points ($0.10/pt at 0.1 lot)

---

## 1. Was adaptive zero-trade logic ever implemented?

**Answer: No.**

- **EA set files** (`adapt_*_001` entries in `coordination/theory_queue.json`, relay commit e402687): these are parameter-variant EAs (adaptive WPR tightening after losses, ATR trail, zgate/wpr60/chop/atrbrk regime gates). None contain logic to detect zero-trade windows and relax filters. All 8 entries are marked `needs_local_mt4` — LocalThug still needs to run them.
- **Cloud clone engine** (`backups/clone_engine_20261019.txt`): "Clone 2a T11_adaptive" uses a rolling-percentile threshold for mom3 (adaptive threshold, not adaptive zero-trade detection). No zero-trade window detection anywhere in the file.

**Conclusion: the adaptive zero-trade feature was never built.** This result is for the MKT-14-NY-T31s family (the main survivor). The Win Logic v2 / nomem6 scanner hard-reject month problem (2021-11, 2022-04 etc.) is a separate issue for multi-filter families.

---

## 2. Zero-trade months in T31s baseline

| Dataset | Period | Months | Trades | Zero-trade months |
|---------|--------|--------|--------|-------------------|
| TwelveData IS | 2020–2023 | 48 | 88 | 3 (6.3%) — 2021-06, 2021-07, 2023-02 |
| FXOpen OOS | 2024–2026 | ~32 | 72 | 2 (6.3%) — 2024-06, 2026-03 |

Zero-trade months are **rare** for T31s (Friday-only entry, single filter `day_up > 0.5×ATR14`). The hard-reject problem seen in nomem6 (90%+ bars blocked in some months) is driven by the multi-filter scanner conditions, not T31s.

---

## 3. Baseline T31s stats

### IS: TwelveData 2020–2023
| Year | n | WR% | PF | avg pts |
|------|---|-----|----|---------|
| 2020 | 21 | 61.9 | 1.07 | +10.8 |
| 2021 | 19 | 57.9 | 1.42 | +41.2 |
| 2022 | 24 | 62.5 | 2.34 | +99.5 |
| 2023 | 24 | 62.5 | 2.25 | +57.3 |
| **Total** | **88** | **61.4** | **1.60** | **+54.2** |
**Total pts: +4,770**

### OOS: FXOpen 2024–2026
| Year | n | WR% | PF | avg pts |
|------|---|-----|----|---------|
| 2024 | 29 | 65.5 | 1.33 | +23.2 |
| 2025 | 28 | 53.6 | 1.18 | +16.6 |
| 2026 | 15 | 73.3 | 6.55 | +134.7 |
| **Total** | **72** | **62.5** | **1.63** | **+43.9** |
**Total pts: +3,161**

> Note: IS 2011–2019 data unavailable — H1 EURUSD data only exists from 2020-02 (yfinance H1 limited to 730 days; no pre-2020 H1 in project files). TD 2020-2023 used as IS, FXOpen 2024-2026 as OOS.

---

## 4. Adaptive emulation test

**Logic implemented:** rolling 4-week window; if 0 trades → relax `day_up` threshold from 0.5×ATR14 to 0.35×ATR14 for next opportunity. Coordinator relay also suggested ATR-scaling of hard rejects (e.g. -210 pts → -1.5×ATR14); applied here as proportional threshold relaxation.

### Delta: Adaptive vs Baseline
| | IS n | IS WR | IS PF | IS avg | OOS n | OOS WR | OOS PF | OOS avg |
|--|------|-------|-------|--------|-------|--------|--------|---------|
| Baseline | 88 | 61.4% | 1.60 | +54.2 | 72 | 62.5% | 1.63 | +43.9 |
| Adaptive | 88 | 61.4% | 1.60 | +54.2 | 73 | 61.6% | 1.62 | +42.6 |
| Delta | **+0** | 0 | 0 | 0 | **+1** | **−0.9%** | **−0.01** | **−1.3** |

### Relaxed-threshold trades (mult < 0.5):
- IS: n=12 trades (window-triggered at start of dataset; not true zero-trade recovery), WR=41.7%, avg=**−85.9 pts** ❌
- OOS: n=7, WR=42.9%, avg=**−10.3 pts** ❌

**Relaxed trades are losers** — days with small day_up (0.35–0.50×ATR14) tend to lack directional follow-through, reversing the Friday fade.

---

## 5. Verdict

| | |
|--|--|
| Implementation status | **Never built** in EA or clone engine |
| Zero-trade problem severity | **Low** for T31s — only 3 months in 4 years |
| Adaptive relaxation effect | **Slightly negative** — relaxed threshold adds losing trades |
| **Recommendation** | **Do not implement** adaptive zero-trade for T31s |

The zero-trade problem reported by the coordinator (months with 90%+ bars rejected) is specific to the multi-filter Win Logic v2 scanner (minslp, maxh, minSSR, Filters 4/1 conditions). Those are NOT present in T31s. If/when a multi-filter survivor emerges from the scanner, revisit ATR-scaled threshold relaxation for those specific conditions.

---

## 6. What the EA adapt_* entries actually test

From `coordination/theory_queue.json` (8 entries, needs_local_mt4):

| ID | Description |
|----|-------------|
| adapt_atrtrail_001 | b31 + ATR trailing stop after entry |
| adapt_adaptwpr_001 | b31 + WPR tightens after 3 consecutive losses |
| adapt_wpr_trail_001 | both adaptive WPR + ATR trail |
| adapt_s2s4_001 | b31 S2-S4 parameter variants |
| adapt_lowrev_001 | low reversal entry variant |
| adapt_atrbracket_001 | ATR bracket stop variant |
| adapt_emacross_001 | EMA cross gate |
| adapt_fracbuy_001 | fractal buy variant |
| + 8× adapt_gate_*_001 | regime gate variants (zgate07, wpr60, chop, atrbrk, reg200, reg500) |

None implement zero-trade window detection. LocalThug still needs to run these via MT4.

---

*Engine: cloud emulation of clone_engine_20261019 with adaptive extensions. Cost: 8 ECN pts/trade. Data: TD 2020-2023 (H1), FXOpen 2024-2026 (H1 ECN). Past results are not advice.*
