# EURUSD Cycle 65 — WillR Exclusion, CCI(20), Bollinger Band Position, Prior Day High
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## Reference baselines

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| v2.3 baseline | 32 | 5.38 | +0.186% | 43.8% | 3.86 | 7.06 | 6.05 |
| RSI5(H1)<60 (C63b) | 21 | 11.44 | +0.298% | 61.9% | 8.62 | 13.40 | 12.85 |
| **EMA30 neg + RSI5<60 + no gap (C64b)** | **15** | **22.47** | **+0.404%** | **73.3%** | **16.88** | **26.89** | **25.71** |

---

## C65a: WillR ≤−30 as Exclusion Filter (Remove Overbought)

C64c found that WillR >−30 (overbought at entry, price near top of 14-bar range) produces PF=1.42 with 2025 PF=0.00 across 13/32 trades. Testing whether excluding those 13 trades improves remaining subsets.

Distribution: 19 trades with WillR≤−30, 13 trades with WillR>−30 (excluded).

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| Baseline excl. WillR ob (WillR≤−30) | 19 | 10.34 | +0.296% | 57.9% | 6.84 | 19.10 | 6.98 |
| EMA30 neg + WillR not ob | 16 | 14.30 | +0.344% | 62.5% | 13.38 | 17.30 | 11.15 |
| No gap + WillR not ob | 17 | 13.24 | +0.339% | 64.7% | 6.84 | 29.69 | 10.82 |
| RSI5<60 + WillR not ob | 18 | 11.82 | +0.317% | 61.1% | 6.84 | 19.10 | 11.15 |
| EMA30 neg + RSI5<60 + WillR not ob | 16 | 14.30 | +0.344% | 62.5% | 13.38 | 17.30 | 11.15 |
| **EMA30 neg + RSI5<60 + no gap + WillR not ob** | **14** | **21.00** | **+0.403%** | **71.4%** | **13.38** | **26.89** | **25.71** |
| No gap + RSI5<60 + WillR not ob | 16 | 15.77 | +0.365% | 68.8% | 6.84 | 29.69 | 25.71 |
| Prior bear + WillR not ob | 16 | 12.59 | +0.303% | 62.5% | 13.38 | 13.40 | 10.82 |

**Key findings:**

- **WillR≤−30 exclusion vs. prior:** Baseline rises from PF=5.38 (n=32) to 10.34 (n=19). The 13 excluded trades were indeed the worst of the baseline.

- **EMA30 neg + RSI5<60 + no gap (n=15, PF=22.47)** vs **+ WillR not ob (n=14, PF=21.00):** Adding WillR exclusion removes 1 trade from C64b's best three-filter and slightly weakens PF. The 1 removed trade is a loss, and removing it does not improve the three-filter — meaning the WillR exclusion is already partially captured by the EMA30+RSI5+no gap combination. **WillR exclusion adds nothing new to C64b.**

- **No gap + RSI5<60 + WillR not ob (n=16, PF=15.77, yrs 6.84/29.69/25.71):** 2024 weakens (6.84 vs 8.62 for no gap + RSI5<60 alone). WillR exclusion from C63b-a removes a 2024 winner and adds nothing to 2025/2026.

- **RSI5<60 captures WillR exclusion almost entirely:** RSI5<60 has n=21 (3 more trades than WillR≤−30 n=19), but RSI5<60 and WillR≤−30 are largely overlapping. RSI5 is a superior formulation of the same "not overbought" concept.

**Verdict: WillR≤−30 exclusion is COLLINEAR with RSI5<60. Adding WillR filter on top of RSI5<60 removes 1–3 marginal trades without improving year-consistent PF. REJECTED as independent filter.**

---

## C65b: CCI(20) at 07:00 Bar

CCI(20): (Typical Price − SMA20) / (0.015 × Mean Deviation). Positive = above typical price range. Distribution on 32 qualifying trades: mean=+32.6, median=+34.7.  
CCI≥0: 22 trades, CCI<0: 10 trades, CCI≥100: 7 trades.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| CCI ≥ 0 (above avg) | 22 | 5.07 | +0.198% | 36.4% | 3.86 | 10.44 | 1.01 |
| CCI < 0 (below avg) | 10 | 6.54 | +0.159% | 60.0% | 3.92 | 1.30 | 25.71 |
| **CCI ≥ 100 (overbought)** | **7** | **0.91** | **−0.006%** | **14.3%** | **1.63** | **0.00** | **0.00** |
| CCI < 100 (not overbought) | 25 | 7.86 | +0.240% | 52.0% | 5.56 | 10.07 | 8.42 |
| EMA30 neg + CCI ≥ 0 | 11 | 11.24 | +0.370% | 45.5% | 10.10 | 17.85 | 0.00 |
| RSI5<60 + CCI ≥ 0 | 12 | 13.30 | +0.385% | 58.3% | 7.58 | 41.85 | 3.01 |
| RSI5<60 + CCI < 0 | 9 | 8.33 | +0.183% | 66.7% | ~inf* | 1.30 | 25.71 |

**Key findings:**

- **CCI≥100 overbought (n=7): PF=0.91, avg=−0.006%, 2025 and 2026 both PF=0.00.** The 7 most extended trades (price far above its typical range) are dead losses across 2025 and 2026. Another strong negative filter consistent with WillR>−30 — both identify the same "overextended" trades.

- **CCI<100 exclusion (n=25): PF=7.86, yrs 5.56/10.07/8.42** — an improvement over baseline (5.38). But n=25 is large and PF=7.86 doesn't reach the strong candidate threshold.

- **EMA30 neg + CCI≥0 (n=11, yrs 10.10/17.85/0.00):** 2026 collapses to 0.00 — catastrophic. Inconsistent.

- **RSI5<60 + CCI≥0 (n=12, yrs 7.58/41.85/3.01):** 2026 = 3.01 (very weak). 2025 near-inf is likely small-n artifact. Year inconsistency.

- CCI<0 (n=10) has 2024 PF=3.92 and 2025 PF=1.30 — weak first two years despite strong 2026.

**Economic interpretation:** The CCI≥100 overbought bucket contains the same trades as WillR>−30 — both identify when the Asia-to-London entry point is at the top of its recent price range. These are the worst SHORT setups because price has already moved far and is likely to consolidate rather than reverse cleanly.

**Verdict: CCI≥100 = strong NEGATIVE filter (n=7, 2025/2026 dead). Consistent with WillR>−30 discovery. But CCI<100 exclusion improves baseline (PF 5.38→7.86) — weaker than RSI5<60 (PF=11.44). COLLINEAR with existing WillR / RSI5 filters. REJECTED as independent addition.**

---

## C65c: Bollinger Band %B Position at 07:00 Bar

BB %B at entry: 0=at lower band, 0.5=at midline, 1=at upper band, >1=above upper band.  
Distribution: mean=0.547, median=0.571.  
Upper half (≥0.5): 19. Lower half (<0.5): 13. Extended (≥0.8): 5.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| BB high (≥0.6) | 14 | 2.70 | +0.092% | 28.6% | 2.17 | 4.45 | 1.52 |
| **BB low (<0.6)** | **18** | **8.72** | **+0.259%** | **55.6%** | **6.71** | **9.40** | **11.15** |
| BB extended (≥0.8) | 5 | 1.26 | +0.018% | 20.0% | 2.06 | 0.00 | — |
| No gap + BB high | 10 | 3.66 | +0.133% | 30.0% | 3.10 | 12.11 | 0.00 |
| No gap + BB low | 15 | 13.18 | +0.324% | 66.7% | 6.71 | 20.83 | 25.71 |
| EMA30 neg + BB high | 5 | 7.17 | +0.238% | 40.0% | 3.67 | 12.11 | — |
| RSI5<60 + BB high | 4 | 27.92 | +0.385% | 75.0% | 7.23 | ~inf* | ~inf* |
| RSI5<60 + BB low | 17 | 9.71 | +0.278% | 58.8% | 9.08 | 9.40 | 11.15 |

**Key findings:**

- **BB high (≥0.6) = weak: PF=2.70, 2026 PF=1.52.** Price near the upper Bollinger band at entry means the Asia rally has pushed price toward its statistical extreme — bad SHORT setup. Extended (≥0.8) is even worse: PF=1.26, 2025 PF=0.00.

- **BB low (<0.6) = BORDERLINE CANDIDATE: n=18, PF=8.72, yrs 6.71/9.40/11.15.** Clean year consistency, rising trajectory. When price is in the lower half of its Bollinger bands at entry despite the Asia rally being net-up, it means the rally has been "soft" — not overextended. The SHORT has more downside room.

- **No gap + BB low (n=15, PF=13.18, yrs 6.71/20.83/25.71):** Strong candidate! 2025/2026 both 20+. 2024 is 6.71 — lower but still positive. n=15 at the adoption boundary.

- RSI5<60 + BB low (n=17, PF=9.71, yrs 9.08/9.40/11.15): Very clean consistency but PF same as RSI5<60 alone — BB low adds nothing within RSI5<60 universe.

**Economic interpretation:** BB %B captures the same "overextension" concept as WillR and CCI, but from a volatility-normalized perspective. Price at the upper Bollinger band has moved 2 standard deviations from its recent mean — a statistical extreme likely to mean-revert. The SHORT strategy benefits from fading this extreme from below, not from above.

**Verdict: BB low (<0.6) is a BORDERLINE CANDIDATE: n=18, PF=8.72, yrs 6.71/9.40/11.15. No gap + BB low (n=15, PF=13.18) is stronger. However, BB low is structurally collinear with WillR/CCI non-overbought and RSI5<60. Re-test BB low with 2027+ data; low standalone incremental value given RSI5<60 already available.**

---

## C65d: Price vs Prior Day High at Entry

Testing whether the Asia close being above the prior session's daily high predicts a stronger SHORT setup (fresh breakout to be faded).

Distribution: **2 trades above prior day high, 30 trades at/below.** The "breakout" scenario is structurally rare — almost never (2/32) does the Asia session close push above the prior day's high in the qualifying universe.

| Configuration | n | PF | avg% |
|--------------|---|----|------|
| Above prior day high | 2 | inf | +0.592% |
| At/below prior day high | 30 | 4.51 | +0.159% |
| RSI5<60 + at/below | 19 | 9.47 | +0.267% |

**Verdict: PERMANENTLY REJECTED.** Only 2 of 32 qualifying trades breach the prior day high. This is not a usable filter in the current data window. The "below prior high" group (n=30) has PF=4.51 — below baseline (5.38) because the 2 above-prior-high trades (which are winners) are now excluded. Adding them back is the baseline. STRUCTURALLY COLLINEAR with the baseline entry universe.

---

## C65 Summary: The Overextension Pattern

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C65a: WillR≤−30 exclusion | Collinear with RSI5<60; adds nothing new | REJECTED |
| C65b: CCI≥100 overbought | n=7, 2025/2026 dead — negative filter | NEGATIVE FILTER (collinear) |
| **C65b: CCI<100 exclusion** | **n=25, PF=7.86, yrs 5.56/10.07/8.42** | **Weak standalone; absorbed by RSI5<60** |
| C65c: BB high (≥0.6) | n=14, PF=2.70, 2026 dead — negative filter | NEGATIVE FILTER |
| **C65c: No gap + BB low** | **n=15, PF=13.18, yrs 6.71/20.83/25.71** | **BORDERLINE CANDIDATE** |
| C65d: Above prior day high | n=2 structurally near-zero | REJECTED |

**C65 major conclusion:** WillR, CCI, and Bollinger Band all converge on the same insight: trades where price is near/above its recent statistical extreme at 07:00 entry are bad SHORTs. RSI5<60 already captures this pattern as the most statistically clean single filter. No new independent information discovered in C65.

**The "overextension cluster" of rejected/negative filters:** WillR>−30, CCI≥100, BB≥0.6 — all three identify the same 10–13 worst trades in the baseline. They are collinear with RSI5<60 and with each other.

---

## Updated Pending Candidates Table (all cycles through C65)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| **C53b** | **SK<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | |
| **C59c** | **EMA30(H1) slope<0** | **21** | **9.28** | **+0.269%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C63b** | **RSI5(H1)<60 at entry** | **21** | **11.44** | **+0.298%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C63b-a** | **No gap up + RSI5(H1)<60** | **17** | **16.81** | **+0.368%** | **FXOpen 2028** | |
| **C64a** | **No gap + RSI5<60 + prior bear** | **15** | **20.12** | **+0.360%** | **FXOpen 2028** | **All 3 yrs 16+** |
| **C64b** | **EMA30 neg + RSI5<60 + no gap** | **15** | **22.47** | **+0.404%** | **FXOpen 2028** | **Strongest 3-filter** |
| **C65c** | **No gap + BB low (<0.6)** | **15** | **13.18** | **+0.324%** | **FXOpen 2028** | **NEW — collinear w/RSI5** |
| C57a | Baseline + no gap up | 25 | 7.90 | +0.248% | FXOpen 2027 | |
| C59c-b | C53b + EMA30(H1)<0 | 11 | 26.87 | +0.415% | FXOpen 2028 | All 3 yrs 25+ |
| C60a | SK<60 + EMA30(H1)<0 + no gap | 12 | 22.04 | +0.394% | FXOpen 2028 | 3-filter |
| C60c | EMA30(H1)<0 + H6 bullish | 13 | 11.82 | +0.349% | FXOpen 2028 | |
| C63c | No gap + prior bear + mom≥2 | 10 | 16.84 | +0.464% | FXOpen 2028 | Year-consistent |

---

## Permanently Rejected (C65 scope)

- **C65a (WillR≤−30 exclusion):** Collinear with RSI5<60. Removes 1 trade from C64b three-filter, marginally weakens PF.
- **C65b (CCI as positive filter):** CCI≥100 = dead negative filter (same trades as WillR/RSI5 overbought). CCI<0 = inconsistent years.
- **C65c (BB extended ≥0.8):** 2025 PF=0.00. Same overextension cluster as WillR/CCI.
- **C65d (above prior day high):** n=2 — structurally unusable.

---

*Past results are not investment advice.*
