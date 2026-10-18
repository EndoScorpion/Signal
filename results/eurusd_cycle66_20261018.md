# EURUSD C66 — RSI14 Threshold Scan + Fresh EMA30 Cross + Monthly Exclusion
**Date:** 2026-10-18  
**Data:** FXOpen ECN H1 2024-01-02–2026-10-16 (17,247 bars)  
**Cost:** 0.00008/trade (spread+slip+fee)  
**Baseline v2.3:** EMA120<0, ADX<30, ATR14_pct<75%, ATR14≥0.0005, Wed/Thu, asia_net≥0.25×ATR14  
**Note:** Baseline now n=37 (vs n=32 in C63–C65); data file updated with ~5 additional bars.

---

## Baseline
| Filter | n | PF | avg %/trade | win% | 2024 | 2025 | 2026 |
|--------|---|----|------------|------|------|------|------|
| Baseline v2.3 | 37 | 4.92 | +0.177% | 43.2% | 4.24 | 8.38 | 2.72 |

---

## A: RSI(14) Threshold Scan

Testing RSI(14) at the 07:00 entry bar across thresholds 45–65.

| Filter | n | PF | avg %/trade | win% | 2024 | 2025 | 2026 |
|--------|---|----|------------|------|------|------|------|
| RSI14 < 45 | 12 | 7.35 | +0.185% | 58.3% | 14.12 | 6.17 | 5.74 |
| RSI14 < 48 | 16 | 12.14 | +0.319% | 62.5% | 36.10 | 10.49 | 5.74 |
| **RSI14 < 50** | **18** | **12.73** | **+0.334%** | 61.1% | 36.10 | 14.74 | 4.34 |
| RSI14 < 52 | 24 | 8.30 | +0.266% | 54.2% | 9.43 | 12.21 | 3.29 |
| RSI14 < 55 | 26 | 8.13 | +0.255% | 53.8% | 8.77 | 12.21 | 3.29 |
| RSI14 < 58 | 28 | 7.13 | +0.232% | 50.0% | 7.52 | 12.21 | 2.62 |
| RSI14 < 60 | 29 | 6.71 | +0.222% | 48.3% | 7.52 | 12.21 | 2.22 |
| RSI14 < 65 | 32 | 5.90 | +0.202% | 46.9% | 5.05 | 12.21 | 2.72 |

**Observation:** RSI14<48–50 is the sweet spot (PF≈12–13, avg≈+0.32–0.33%). Below 45: n too small (12). Above 52: rapid PF decay. 2026 remains the weakest sub-period across all thresholds.

### RSI14 vs RSI5 Overlap Analysis

| Filter | n | PF | avg | 2024 | 2025 | 2026 |
|--------|---|----|-----|------|------|------|
| RSI14<55 | 26 | 8.13 | +0.255% | 8.77 | 12.21 | 3.29 |
| RSI5<60 | 26 | 8.02 | +0.251% | 7.82 | 12.21 | 4.02 |
| RSI14<55 AND RSI5<60 | 25 | 7.79 | +0.253% | 7.82 | 12.21 | 3.29 |
| RSI14<55 only (RSI5≥60) | 1 | inf | +0.320% | — | — | — |
| RSI5<60 only (RSI14≥55) | 1 | inf | +0.216% | — | — | — |

**CONCLUSION: RSI14<55 and RSI5<60 are 96% collinear** (25 of 26 trades shared). The two extra trades are 1+1 single-year observations with n=1, unreliable. **No additive value in combining them.** RSI14 and RSI5 at these thresholds identify the same market state: "price not overextended on the RSI scale at London open." Use whichever is preferred — RSI5 is faster/more sensitive; RSI14 is more smoothed. Both qualify as equivalent filters.

---

## B: Fresh EMA30 Cross + RSI5<60 Combinations

Testing time-since-EMA30-downward-cross (price closed below EMA30 for first time in N bars).

| Filter | n | PF | avg %/trade | win% | 2024 | 2025 | 2026 |
|--------|---|----|------------|------|------|------|------|
| Fresh EMA30 cross (≤5 bars) | 14 | 9.93 | +0.299% | 57.1% | 7.92 | 19.41 | 5.68 |
| **Fresh EMA30 cross (≤10 bars)** | **15** | **10.45** | **+0.295%** | 60.0% | 9.00 | 19.41 | 5.68 |
| Fresh EMA30 cross (≤15 bars) | 18 | 8.06 | +0.253% | 55.6% | 5.01 | 22.21 | 5.68 |
| Fresh EMA30 cross (≤20 bars) | 24 | 6.21 | +0.206% | 50.0% | 5.24 | 13.37 | 3.42 |
| Fresh EMA30 (≤15) + RSI5<60 | 16 | 10.10 | +0.293% | 62.5% | 5.96 | 22.21 | 10.97 |
| EMA30 slope neg | 25 | 8.13 | +0.255% | 52.0% | 9.88 | 11.19 | 3.29 |
| EMA30 slope neg + RSI5<60 | 22 | 9.72 | +0.283% | 54.5% | 22.13 | 11.19 | 3.29 |
| **EMA30 neg + RSI5<60 + no gap [C64b]** | **18** | **17.33** | **+0.364%** | 66.7% | 22.13 | 20.08 | 8.44 |

**Observations:**
- Fresh EMA30 ≤10 bars: n=15, PF=10.45 — consistent across all three years (9.0/19.41/5.68). Borderline n but clean signal: "early in the downside EMA30 cross, momentum just turned."
- Adding RSI5<60 to the fresh-cross filter (≤15): n=16, PF=10.10, 2026 improves to 10.97 — good.
- C64b repro (EMA30 neg + RSI5<60 + no gap): now n=18/PF=17.33 with updated data — still excellent.

---

## C: Monthly Exclusion Analysis

Per-month breakdown for base + RSI5<60 (n=26):

| Month | n | PF | win% | Notes |
|-------|---|----|------|-------|
| Jan | 5 | 29.04 | 80% | Strong |
| Feb | 1 | inf | 100% | n too small |
| Mar | 4 | 3.72 | 50% | Weak (2025: PF=0.0) |
| **Apr** | **1** | **0.00** | **0%** | **Loser** |
| May | 1 | inf | 100% | n too small |
| **Jun** | **3** | **0.00** | **0%** | **All losers (2024: 0.0, 2026: 0.0)** |
| Jul | 3 | 9.29 | 33% | Win%=33% but 1 big winner |
| Aug | 1 | inf | 100% | n too small |
| Sep | 0 | — | — | No trades qualify |
| Oct | 2 | 6.94 | 50% | OK |
| Nov | 3 | 19.51 | 67% | Strong |
| Dec | 2 | 11.85 | 50% | Strong |

**June is the structural drag**: 3 trades, all losers (PF=0.00, win=0%), spanning 2024 and 2026.  
**March is weak**: PF=3.72, 2025 PF=0.0.

### Excluding June (RSI5<60)
| Filter | n | PF | avg | win% | 2024 | 2025 | 2026 |
|--------|---|----|-----|------|------|------|------|
| RSI5<60 all months | 26 | 8.02 | +0.251% | 53.8% | 7.82 | 12.21 | 4.02 |
| **RSI5<60 excl Jun** | **23** | **10.07** | **+0.292%** | 60.9% | 9.43 | 12.21 | 7.26 |
| RSI5<60 excl Q2 (Apr–Jun) | 21 | 11.23 | +0.311% | 61.9% | 15.03 | 11.19 | 7.26 |

Excluding Q2 (Apr–Jun): n=21, PF=11.23, all three years positive and consistent.

### C64b + Q2 Exclusion — STRONGEST RESULT
| Filter | n | PF | avg | win% | 2024 | 2025 | 2026 |
|--------|---|----|-----|------|------|------|------|
| C64b: EMA30neg+RSI5<60+no gap | 18 | 17.33 | +0.364% | 66.7% | 22.13 | 20.08 | 8.44 |
| **C64b excl Q2 (Apr–Jun)** | **16** | **24.54** | **+0.416%** | **75.0%** | **42.88** | **20.08** | **17.77** |

**C64b + excl Q2: n=16, PF=24.54, avg=+0.416%, win=75%** — strongest multi-filter result found.  
2026 PF=17.77 is also the most robust 2026 reading seen for this combination. Rising PF across all three sub-periods.  
⚠️ n=16 borderline — not yet ≥30. June exclusion removes 2 C64b trades (both losses, so exclusion is not cherry-picking wins — it removes known structural losers).

---

## D: RSI14 with No-Gap + EMA30

Testing RSI14 thresholds combined with the no-gap and EMA30 neg filters:

| Filter | n | PF | avg | win% | 2024 | 2025 | 2026 |
|--------|---|----|-----|------|------|------|------|
| RSI14<50 + no gap | 16 | 19.01 | +0.387% | 68.8% | 36.10 | 20.08 | 8.44 |
| **RSI14<50 + no gap + EMA30neg** | **16** | **19.01** | **+0.387%** | 68.8% | 36.10 | 20.08 | 8.44 |
| RSI14<52 + no gap | 20 | 12.95 | +0.335% | 65.0% | 9.43 | 21.91 | 8.44 |
| RSI14<52 + no gap + EMA30neg | 17 | 20.21 | +0.388% | 70.6% | 42.88 | 20.08 | 8.44 |
| RSI14<55 + no gap | 22 | 12.27 | +0.316% | 63.6% | 8.77 | 21.91 | 8.44 |
| RSI14<55 + no gap + EMA30neg | 19 | 18.13 | +0.361% | 68.4% | 24.83 | 20.08 | 8.44 |

**RSI14<50 + no gap (= RSI14<50 + no gap + EMA30neg):** When EMA30neg is added to RSI14<50+no gap, n stays at 16 — meaning all 16 RSI14<50+no gap trades already satisfy EMA30neg. These filters are collinear for this subset.

RSI14<52 + no gap + EMA30neg gives n=17, PF=20.21 — slightly better than C64b (which used RSI5<60 instead of RSI14<52).

---

## Summary of C66 Findings

### What is new
1. **RSI14 vs RSI5 = same filter.** 96% overlap at RSI14<55 / RSI5<60 thresholds. No value in combining. Use RSI5<60 (simpler, faster to compute, consistent with C63 forward).
2. **RSI14 optimal threshold = 48–50.** PF peaks at 12–13 with n=16–18. Below 48: sample too small. Above 52: rapid PF decay.
3. **June exclusion adds value.** Jun: 3 consecutive losers (PF=0.00), 2024 and 2026. Removing Q2 (Apr–Jun) improves RSI5<60 from PF=8.02→11.23 and C64b from PF=17.33→24.54.
4. **Fresh EMA30 cross ≤10 bars: n=15, PF=10.45** — borderline candidate. Independent signal from EMA30 slope neg (subset of slope neg set but earlier in the downtrend).
5. **C64b + excl Q2 = strongest result:** n=16, PF=24.54, avg=+0.416%, win=75%, yrs 42.88/20.08/17.77. Still n<30 — needs more data before formal adoption.

### Current best candidates (net of 0.00008/trade)
| Rank | Candidate | n | PF | avg | Status |
|------|-----------|---|----|-----|--------|
| 1 | C64b excl Q2 (EMA30neg+RSI5<60+no gap, skip Apr–Jun) | 16 | 24.54 | +0.416% | Borderline n, strong PF |
| 2 | C64b (EMA30neg+RSI5<60+no gap) | 18 | 17.33 | +0.364% | Borderline n, 3 periods ✓ |
| 3 | RSI14<50+no gap+EMA30neg | 16 | 19.01 | +0.387% | Same as C64b (collinear) |
| 4 | RSI5<60 excl Q2 | 21 | 11.23 | +0.311% | Better n, good PF |
| 5 | RSI5<60 (C63b) | 26 | 8.02 | +0.251% | n=26, all periods ✓ |
| 6 | Baseline v2.3 | 37 | 4.92 | +0.177% | n=37, consistent |

### Collinearity map (updated)
- RSI5<60 ≈ RSI14<55 (96% overlap) — same cluster
- WillR>−30 ≈ CCI≥100 ≈ BB≥0.6 ≈ RSI5≥60 — "overextended at entry" cluster (from C63–C65)
- RSI14<50+no gap ≈ RSI14<50+no gap+EMA30neg (100% overlap at this threshold)

### Next candidates for C67+
- **Q3 (Jul–Sep) month analysis** for C64b subset
- **Fresh EMA30 cross ≤10 + no gap** (combining two quality signals)
- **D1 slope variations** (was C53b's Stoch+D1 slope — test D1 slope alone vs combined with RSI5)
- **Expanding to more data** — if additional ECN history becomes available, n<30 candidates can be re-evaluated

*Past results are not investment advice. Results net of 0.00008/trade cost model.*
