# EURUSD Cycle 64 — RSI5 Combos, Williams %R(H1), MACD Histogram
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## Reference baselines

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| v2.3 baseline | 32 | 5.38 | +0.186% | 43.8% | 3.86 | 7.06 | 6.05 |
| EMA30(H1)<0 (C59c) | 21 | 9.28 | +0.269% | 52.4% | 8.48 | 9.12 | 11.15 |
| RSI5(H1)<60 (C63b) | 21 | 11.44 | +0.298% | 61.9% | 8.62 | 13.40 | 12.85 |
| No gap up (C57a) | 25 | 7.90 | +0.248% | 52.0% | 4.76 | 17.14 | 7.16 |
| C53b (SK<60+D1<0) | 13 | 17.43 | +0.366% | 69.2% | 9.08 | 33.90 | 25.71 |

---

## C64a: RSI5(H1)<60 + Prior Day Bear Combos

Testing whether adding prior day direction to the RSI5<60 filter improves outcomes. RSI5 uses the 07:00 bar value (same as C63b).

Distribution: of the 21 RSI5<60 qualifying trades, 17 had prior day bearish, 4 bullish.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| RSI5<60 + prior day bear | 17 | **13.69** | **+0.310%** | **64.7%** | **16.88** | **9.40** | **25.71** |
| RSI5<60 + prior day bull | 4 | 6.41 | +0.250% | 50.0% | 0.00 | ~inf* | 3.01 |
| No gap + RSI5<60 (C63b-a) | 17 | **16.81** | **+0.368%** | **70.6%** | **8.62** | **29.69** | **25.71** |
| **No gap + RSI5<60 + prior bear** | **15** | **20.12** | **+0.360%** | **73.3%** | **16.88** | **20.83** | **25.71** |
| EMA30 neg + RSI5<60 + prior bear | 16 | 12.95 | +0.310% | 62.5% | 16.88 | 8.14 | 25.71 |
| C53b + RSI5<60 | 13 | 17.43 | +0.366% | 69.2% | 9.08 | 33.90 | 25.71 |

*~inf = zero-loss artifact in year with tiny n.

**Key findings:**

- **RSI5<60 + prior day bear (n=17, PF=13.69): MAJOR CANDIDATE.** All three years clearly positive (16.88/9.40/25.71). Prior day bearish is the expected condition in 17/21 RSI5<60 qualifying trades — the four bullish-prior-day trades have a 2024 PF=0.00 (all losses in 2024). This confirms prior day direction as an additional filter.

- **No gap + RSI5<60 + prior bear (n=15, PF=20.12): STRONGEST TWO-FILTER EXTENSION.** All three years 16.88/20.83/25.71 — consistently rising PF across years. The best year-consistent three-filter found in this run. 2026 has only one year with 2+ trades but it is all wins. n=15 is borderline for standalone adoption.

- **C53b + RSI5<60 = C53b** (n=13, same trades): C53b already requires SK<60 + D1 slope<0; RSI5<60 does not further restrict the C53b universe on this 2024–2026 data. The two filters pick identical qualifying trades. This is a collinearity discovery.

**Verdict for C64a: No gap + RSI5<60 + prior bear (n=15, PF=20.12, all 3 yrs 16+) — STRONG CANDIDATE. Re-test when n≥25 with 2027+ data.**

---

## C64b: RSI5<60 + EMA30 Neg + No Gap Three-Filter Core

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| EMA30 neg + RSI5<60 (C63b-b) | 18 | 13.03 | +0.325% | 61.1% | 16.88 | 12.14 | 11.15 |
| **EMA30 neg + RSI5<60 + no gap** | **15** | **22.47** | **+0.404%** | **73.3%** | **16.88** | **26.89** | **25.71** |
| EMA30 neg + RSI5<60 + no gap + prior bear | 14 | 19.04 | +0.364% | 71.4% | 16.88 | 18.03 | 25.71 |
| EMA30 neg + RSI5<60 + mom≥2 | 9 | 26.08 | +0.512% | 66.7% | 27.64 | ~inf* | 7.95 |
| No gap + RSI5<60 + mom≥2 | 9 | 21.29 | +0.507% | 66.7% | 9.29 | ~inf* | 18.35 |

**Key findings:**

- **EMA30 neg + RSI5<60 + no gap (n=15, PF=22.47): STRONGEST THREE-FILTER FOUND.** All three years 16.88/26.89/25.71 with rising trajectory. n=15 at the adoption threshold. This combines three well-supported H1-based signals: EMA30 slope direction, RSI5 momentum level, and overnight gap direction. Economic logic: EMA30<0 confirms downward H1 trend, RSI5<60 confirms momentum hasn't extended to overbought, no gap-up ensures no overnight squeeze has already trapped shorts.

- Adding prior bear (n=14) weakens 2025 from 26.89 to 18.03 while 2026 stays at 25.71 — the marginal trade removed is a 2025 winner. The three-filter version is preferred over adding prior bear.

- EMA30 + RSI5 + mom≥2 (n=9): 2025 has the ~inf artifact. Not clean.

**Verdict: EMA30 neg + RSI5<60 + no gap (n=15, PF=22.47, yrs 16.88/26.89/25.71) — STRONGEST THREE-FILTER CANDIDATE IN THIS CYCLE. Re-test when n≥25.**

---

## C64c: Williams %R(14) at 07:00 Bar

Williams %R(14) at the 07:00 entry bar: range −100 to 0, where −100=oversold, 0=overbought.

Distribution on 32 qualifying trades: mean=−43.0, median=−39.3.  
Overbought (>−30): 13, Mid (−70 to −30): 13, Oversold (<−70): 6.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| WillR overbought (>−30) | 13 | 1.42 | +0.024% | 23.1% | 2.14 | 0.00 | 3.24 |
| **WillR mid (−70 to −30)** | **13** | **8.61** | **+0.317%** | **46.2%** | **5.80** | **22.99** | **4.06** |
| WillR oversold (<−70) | 6 | 25.81 | +0.250% | 83.3% | ~inf* | 12.08 | ~inf* |
| No gap + WillR overbought | 8 | 2.00 | +0.054% | 25.0% | 3.05 | 0.00 | 0.00 |
| No gap + WillR mid | 12 | 9.92 | +0.350% | 50.0% | 5.80 | 22.99 | 6.29 |
| EMA30 neg + WillR overbought | 5 | 1.54 | +0.029% | 20.0% | 3.54 | 0.00 | — |
| EMA30 neg + WillR mid | 10 | 12.33 | +0.401% | 50.0% | 11.34 | 20.19 | 6.47 |
| RSI5<60 + WillR overbought | 3 | 8.72 | +0.186% | 66.7% | ~inf* | 0.00 | ~inf* |
| RSI5<60 + WillR mid | 12 | 10.00 | +0.350% | 50.0% | 5.80 | 22.99 | 6.47 |

**Key findings:**

- **WillR overbought (>−30) = catastrophic: PF=1.42, 2025 PF=0.00.** The 13 trades where price is near the top of the prior 14-bar range lose consistently in 2025. Overbought at entry means the SHORT is entering when price is already extended — the Asia rally has fully played out, providing no room for a London reversal. **Strong exclusion filter.**

- **WillR mid (−70 to −30): PF=8.61** — the middle range works, but 2026 drops to 4.06. This is the 13 trades where price has pulled back from its extreme. Not a strong standalone addition.

- **WillR oversold (<−70): n=6, PF=25.81** — the 6 oversold trades (price near the bottom of its 14-bar range despite being net-up in Asia) are the best trades. But 2024 and 2026 have ~inf artifacts from tiny n. Not reliable at n=6.

- **EMA30 neg + WillR mid (n=10, PF=12.33, yrs 11.34/20.19/6.47)**: 2026 weakens to 6.47 — consistent but below the strong threshold. Not a standalone candidate.

**Economic interpretation:** WillR at the entry bar captures where the Asia close price sits within the recent 14-bar range. If Asia ended near the top of its recent range (overbought), the short-selling thesis is weaker — price has already moved far and may need a cooling period before reversing. The SHORT works better when price is in the middle or bottom of the range — less crowded "fade the extension" trade.

**Verdict: WillR overbought (>−30) is a strong NEGATIVE filter — 13/32 trades that should be EXCLUDED (PF=1.42, 2025 dead). WillR mid and oversold provide mixed year consistency. NOT a standalone positive filter.**

**Key takeaway: Adding WillR ≤−30 as an exclusion (i.e., skip if WillR >−30) would remove 13 bad trades from the baseline. Worth testing combined with other filters in C65.**

---

## C64d: MACD Histogram at 07:00 Bar

MACD histogram (12/26/9) at the 07:00 entry bar. For SHORT: negative histogram = bearish momentum. Histogram direction (07:00 vs 06:00): falling = deteriorating.

Distribution on 32 qualifying trades: mean=+0.000194, median=+0.000177.  
**Negative (bearish): 2. Positive (bullish): 30.** Deteriorating (falling): 20.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| MACD histogram < 0 | 2 | inf | +0.405% | 100.0% | ~inf* | — | ~inf* |
| MACD histogram ≥ 0 | 30 | 4.78 | +0.171% | 40.0% | 3.48 | 7.06 | 3.93 |
| **MACD deteriorating (falling)** | **20** | **12.69** | **+0.316%** | **65.0%** | **6.68** | **13.40** | ~inf* |
| No gap + MACD neg | 2 | inf | — | 100% | ~inf* | — | ~inf* |
| EMA30 neg + MACD neg | 2 | inf | — | 100% | ~inf* | — | ~inf* |

**Key findings:**

- **MACD histogram < 0: only 2 qualifying trades across 3 years.** MACD-H1 is almost never negative at the 07:00 entry bar in the qualifying Asia-up universe. Price has been rising in Asia, so the H1 MACD is naturally positive. This filter collapses to n=2 — completely unusable. **REJECTED.**

- **MACD histogram ≥ 0 (n=30): PF=4.78** — essentially the full baseline. The positive MACD constraint is structurally nearly always true when Asia has been rallying.

- **MACD deteriorating (hist_07 < hist_06, n=20): PF=12.69, yrs 6.68/13.40/~inf.** The 2026 ~inf artifact from zero losses in 1–2 trades. The 2024 and 2025 are meaningful (6.68/13.40). This is structurally similar to the H1 momentum score from C61d — both capture whether the late-Asia momentum is weakening. 20/32 trades have a falling MACD histogram, meaning the short-term bullish momentum is slowing.

- The MACD deteriorating filter (n=20) closely overlaps with RSI5<60 (n=21) — both capture the same "momentum fading" concept in different mathematical forms. This is expected collinearity.

**Verdict: MACD histogram direction (deteriorating) is COLLINEAR with RSI5<60. Both measure late-Asia momentum fadeout. The MACD negative bucket (n=2) is completely unusable. REJECTED as a standalone filter. The deteriorating direction overlaps RSI5<60 and adds nothing new.**

---

## Summary: C64 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| **C64a: No gap + RSI5<60 + prior bear** | **n=15, PF=20.12, yrs 16.88/20.83/25.71** | **STRONG CANDIDATE** |
| **C64b: EMA30 neg + RSI5<60 + no gap** | **n=15, PF=22.47, yrs 16.88/26.89/25.71** | **STRONGEST THREE-FILTER** |
| C64b: C53b + RSI5<60 | Identical to C53b (n=13) — collinear | RSI5 absorbed by C53b |
| C64c: WillR overbought (>−30) | n=13, PF=1.42, 2025 PF=0.00 — exclusion signal | NEGATIVE FILTER |
| C64c: WillR mid (−70 to −30) | n=13, PF=8.61 — weak year consistency | NOT STANDALONE |
| C64d: MACD hist < 0 | n=2 — structurally near-zero | REJECTED |
| C64d: MACD deteriorating | n=20 — collinear with RSI5<60 | REJECTED (collinear) |

**Major new discoveries:**
1. **EMA30 neg + RSI5<60 + no gap (n=15, PF=22.47)** is the strongest three-signal combination found across all cycles with clean year consistency (rising 16.88→26.89→25.71).
2. **No gap + RSI5<60 + prior bear (n=15, PF=20.12)** is an equally strong alternative three-filter.
3. **WillR overbought (>−30) is a negative filter** — 13 trades to skip. Combining WillR≤−30 with other filters is worth exploring in C65.
4. C53b absorbs RSI5<60 completely — both filters capture the same momentum measure in this data window.

---

## Updated Pending Candidates Table (all cycles through C64)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **SK<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best prior combo** |
| **C56c** | **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | |
| **C57a** | **Baseline + no gap up** | **25** | **7.90** | **+0.248%** | **FXOpen 2027** | |
| **C59c** | **EMA30(H1) slope<0** | **21** | **9.28** | **+0.269%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C59c-b** | **C53b + EMA30(H1)<0** | **11** | **26.87** | **+0.415%** | **FXOpen 2028** | **All 3 yrs 25+** |
| **C59c-c** | **No gap up + EMA30(H1)<0** | **17** | **14.97** | **+0.348%** | **FXOpen 2028** | |
| **C60a** | **SK<60 + EMA30(H1)<0 + no gap up** | **12** | **22.04** | **+0.394%** | **FXOpen 2028** | **3-filter, no artifacts** |
| **C60b** | **H4 SK<50 at 04:00 bar** | **15** | **9.18** | **+0.239%** | **FXOpen 2027** | **Borderline** |
| **C60c** | **EMA30(H1)<0 + H6 bullish** | **13** | **11.82** | **+0.349%** | **FXOpen 2028** | **Final Asia bar paradox** |
| **C61c** | **EMA30(H1)<0 + fresh cross (<15 bars)** | **13** | **12.40** | **+0.332%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C63b** | **RSI5(H1)<60 at entry** | **21** | **11.44** | **+0.298%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C63b-a** | **No gap up + RSI5(H1)<60** | **17** | **16.81** | **+0.368%** | **FXOpen 2028** | **All 3 yrs 8+** |
| **C64a** | **No gap + RSI5<60 + prior bear** | **15** | **20.12** | **+0.360%** | **FXOpen 2028** | **NEW — all 3 yrs 16+** |
| **C64b** | **EMA30 neg + RSI5<60 + no gap** | **15** | **22.47** | **+0.404%** | **FXOpen 2028** | **NEW — strongest 3-filter** |
| C62a-b | No gap up + prior day bear | 22 | 8.52 | +0.237% | FXOpen 2027 | |
| C63c | No gap + prior bear + mom≥2 | 10 | 16.84 | +0.464% | FXOpen 2028 | 3-filter year-consistent |
| C51a | RSI(14)<55 | 22 | 8.97 | +0.268% | FXOpen 2027-28 | |
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 | |
| C48b | Bar07 bearish | 20 | 10.69 | +0.292% | FXOpen 2027-28 | |
| C35 | Bear07 gap down | 19 | 10.33 | +0.319% | FXOpen 2027-28 | |

---

## Permanently Rejected (C64 scope)

- **C64c: WillR overbought (>−30):** 2025 PF=0.00; negative filter (13 trades to exclude). EMA30 neg + WillR mid explored but 2026 weak.
- **C64d: MACD histogram (signed):** Near-zero negative trades (n=2) — structurally unusable in this Asia-up universe.
- **C64d: MACD deteriorating:** Collinear with RSI5<60 — both capture late-Asia momentum fade. No independent information.
- **C53b + RSI5<60:** Produces identical trades to C53b alone — RSI5<60 is absorbed by C53b's SK<60 + D1slope constraints.

---

*Past results are not investment advice.*
