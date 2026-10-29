# EURUSD Self-Improvement Cycles C44 — H4 EMA50 + Combo Tests
**Date:** 2026-10-18 | **Data:** FXOpen ECN H1 2024-01-02 to 2026-10-16 (17,247 bars)
**Baseline (v2.3):** n=32, PF=5.38, avg=+0.186%, win=78.1%

---

## C44a: H4 EMA50 Slope at 04:00 UTC

**Hypothesis:** H4 EMA50 slope at the last H4 bar before entry (04:00-07:59 UTC) provides additional trend confirmation.

**Method:** Resample H1 to H4 bars, compute EMA50, take the 04:00 UTC H4 bar slope for each trade date.

**Finding:** H4 EMA50 slope < 0 covers 87.5% of qualifying trades (n=28/32). The EMA120 slope<0 condition already pre-selects for bearish H4 momentum — the H4 EMA50 slope adds essentially no new information.

| Subset | n | PF | avg% |
|--------|---|-----|------|
| H4 EMA slope < 0 (bearish) | 28 | 5.14 | +0.177% |
| H4 EMA slope >= 0 (bullish) | 4 | inf | +0.254% |
| Missing (no H4 04:00 bar) | 0 | — | — |

**Verdict: REJECTED.** 87.5% overlap with EMA120 condition. The 4 trades with bullish H4 EMA actually performed better (no losses, n too small). Not a useful discriminator.

---

## C44b: Top Candidate Combo Tests

### Individual Candidates (reminder)

| Filter | n | PF | avg% | By Year |
|--------|---|-----|------|---------|
| D1 slope<0 (C25b) | 27 | 5.76 | +0.173% | 2024:3.78, 2025:8.11, 2026:5.46 |
| ATR expanding (C37) | 17 | 8.52 | +0.251% | 2024:4.05, 2025:inf, 2026:3.39 |
| 0-1 prior Asia up (C43) | 16 | 8.53 | +0.254% | 2024:8.82, 2025:10.37, 2026:4.54 |
| Skip Q2 (C42) | 24 | 7.22 | +0.214% | 2024:5.34, 2025:9.12, 2026:9.14 |
| Bear07 (C35) | 19 | 10.33 | +0.239% | 2024:5.15, 2025:inf, 2026:10.75 |

### Pairwise Combos

| Combo | n | PF | avg% | By Year |
|-------|---|-----|------|---------|
| D1+ATR_exp | 14 | 10.85 | +0.274% | 2024:5.23, 2025:inf, 2026:3.91 |
| D1+consec | 14 | 9.48 | +0.244% | 2024:8.82, 2025:9.77, 2026:4.32 |
| D1+skipQ2 | 20 | 7.11 | +0.192% | 2024:5.02, 2025:8.43, 2026:5.88 |
| ATR_exp+consec | 9 | inf | +0.329% | 2024:inf, 2025:inf, 2026:inf |
| ATR_exp+skipQ2 | 12 | 11.94 | +0.288% | 2024:4.87, 2025:inf, 2026:9.14 |
| consec+skipQ2 | 11 | 11.62 | +0.296% | 2024:8.67, 2025:9.23, 2026:9.08 |
| D1+bear07 | 17 | 12.16 | +0.291% | 2024:6.34, 2025:inf, 2026:11.23 |
| consec+bear07 | 10 | inf | +0.314% | 2024:inf, 2025:inf, 2026:inf |

### Triple Combos

| Combo | n | PF | avg% | By Year |
|-------|---|-----|------|---------|
| D1+consec+skipQ2 | 9 | inf | +0.321% | 2024:inf, 2025:inf, 2026:inf |
| D1+ATR_exp+consec | 7 | inf | +0.351% | 2024:inf, 2025:inf, 2026:inf |
| consec+skipQ2+ATR_exp | 6 | inf | +0.368% | 2024:inf, 2025:inf, 2026:inf |

---

## Summary

All pairwise and triple combos with `consec` or `bear07` hit n<30. The best realistic combo for the 2027 re-test pool:

- **D1+bear07** (n=17): PF=12.16, best all-year consistency among named pairs
- **consec+skipQ2** (n=11): PF=11.62, structurally sound (all years consistent)
- **ATR_exp+skipQ2** (n=12): PF=11.94, good year consistency

**All combos below n=30 threshold.** Rule adoption deferred until FXOpen 2027 data extends sample.

---

## Loop Status: PAUSED

All 20 cycles (C25-C44) exhausted on current 2024-2026 dataset. v2.3 baseline at performance ceiling with n=32.

**Priority queue for 2027 re-test:**
1. skip-Q2 alone (n=24 → ~27+ with 2027 data)
2. D1 slope<0 alone (n=27 → ~30+ with 2027 data)
3. consec (0-1 prior Asia up, n=16 → ~18+ with 2027 data)
4. bear07 (n=19 → ~21+ with 2027 data)
5. D1+skipQ2 combo (n=20 → ~23+ with 2027 data)

Resume: `python3 eurusd_c44.py` on updated FXOpen H1 CSV.
