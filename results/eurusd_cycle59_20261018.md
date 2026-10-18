# EURUSD Cycle 59 — Asia Velocity, H4 Pre-Entry Bar, EMA30(H1), Asia Net Magnitude
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C59a: Asia Velocity (asia_net / asia_range)

Asia velocity measures the directional quality of the overnight session: `velocity = asia_net / asia_range`. 1.0 = moved straight up; ~0.1 = wide range but minimal net direction.

Distribution on 32 qualifying trades: mean=0.479, median=0.480.  
- <0.2: 4, 0.2–0.4: 10, 0.4–0.6: 7, ≥0.6: 11

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| High velocity (≥0.4) | 18 | 5.63 | +0.193% | 44.4% | 7.16 | 3.94 | 7.75 |
| Low velocity (<0.4) | 14 | 5.07 | +0.177% | 42.9% | 1.71 | 21.87 | 4.65 |
| No gap up + high vel. | 13 | 9.61 | +0.276% | 53.8% | 9.61 | 13.68 | 5.97 |
| No gap up + low vel. | 12 | 6.41 | +0.217% | 50.0% | 2.01 | 21.87 | 9.07 |

**Key finding:** Asia velocity provides no consistent year-to-year split. High velocity has 2025 PF=3.94 (weak); low velocity has 2024 PF=1.71. The mean velocity of 0.48 reflects that qualifying sessions (asia_net≥0.25×ATR on a 2.2×ATR range) cluster around a 50% velocity regardless of outcome.

**Verdict: REJECTED. Asia velocity is year-inconsistent across both buckets. No discriminating power.**

---

## C59b: H4 Pre-Entry Bar (Hours 4-6 Before London Open)

The hours 4-6 H4-equivalent bar (the 3 hours immediately before the 07:00 entry) tests whether a bearish close of the pre-London period improves results.

Distribution: 9/32 qualifying trades had a bearish hours 4-6 bar; 23/32 bullish.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| H4 pre-entry bearish | 9 | 9.35 | +0.299% | 55.6% | 10.65 | 11.66 | 2.17 |
| H4 pre-entry bullish | 23 | 4.14 | +0.141% | 39.1% | 3.13 | 3.84 | 7.47 |
| No gap up + H4 bear | 8 | 12.03 | +0.345% | 62.5% | 10.65 | 11.66 | ~inf* |

*~inf = zero losses in 2026 within this 8-trade set.

**Key finding:** H4 pre-entry bearish (n=9) shows PF=9.35 and 2024/2025 are genuinely good (10.65/11.66), but **2026 PF=2.17 is weak.** The economic logic is reasonable — a pullback in the 3 hours before London means Asia is already losing its bid — but n=9 and year-3 weakness make this insufficient for adoption.

No gap up + H4 bear (n=8): 2026 PF=~inf is a 1-trade artifact (no 2026 losses in 8 trades).

**Verdict: SMALL-N CURIOSITY. n=9 is below adoption threshold and 2026 PF=2.17 raises concern. Re-test when n≥15 with more data (FXOpen 2027+). Not a current candidate.**

---

## C59c: EMA30(H1) Slope at 07:00 — MAJOR FINDING

EMA30 on H1 bars is a faster intraday trend indicator than the D1 EMA20 (C25b). At the 07:00 entry bar, EMA30(H1) slope<0 means the 30-bar intraday trend is pointing down.

Distribution on 32 qualifying trades: Negative EMA30 slope: 21 trades. Positive: 11 trades. Mean=−0.000020.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| EMA30(H1) slope < 0 | 21 | **9.28** | **+0.269%** | **52.4%** | **8.48** | **9.12** | **11.15** |
| EMA30(H1) slope ≥ 0 | 11 | 1.43 | +0.026% | 27.3% | 1.12 | 2.22 | 1.52 |
| **C53b + EMA30 neg** | **11** | **26.87** | **+0.415%** | **72.7%** | **25.92** | **28.86** | **25.71** |
| SK<60 + EMA30 neg | 13 | 17.37 | +0.359% | 69.2% | 25.92 | 11.60 | 25.71 |
| No gap up + EMA30 neg | 17 | **14.97** | **+0.348%** | **64.7%** | **11.10** | **15.53** | **25.71** |

**Critical finding: EMA30(H1) slope is the cleanest year-consistent binary filter discovered since C53b.**

**EMA30(H1) < 0 (n=21, PF=9.28):** All three years positive — 8.48, 9.12, 11.15. This is a genuine high-n improvement. Excludes 11 trades where the H1 trend is locally upward at the entry moment. The negative bucket is the fifth-largest candidate by n (after C51a, C25b, C42, and baseline+no-gap-up).

**EMA30(H1) ≥ 0 (n=11, PF=1.43):** Catastrophic — all three years near-breakeven or worse (1.12/2.22/1.52). When the H1 30-bar EMA is rising at the 07:00 entry, the SHORT setup fails consistently. This is nearly as bad as the gap-up signal.

**C53b + EMA30 neg (n=11, PF=26.87, 25.92/28.86/25.71):** The most year-consistent three-filter result ever recorded in this research. All three years at 25+. This is remarkable — no 2025 or 2026 anomalies, no ~inf artifacts, real trades distributed across all three years.

Economic interpretation: EMA30(H1) captures whether the H1 bar trend itself is bearish at the 07:00 entry. EMA120(H1) (the existing baseline filter) measures the long-run hourly trend; EMA30(H1) measures the recent 30-bar (30-hour ≈ 1.25 day) trend. They are complementary at different timescales. When both are negative, the SHORT bias is confirmed at two timescales simultaneously.

**Why is this independent from D1 EMA20 slope (C25b)?** D1 EMA20 uses daily close prices; EMA30(H1) uses H1 close prices. The 30-bar H1 window ≈ 30 hours ≈ 1.25 calendar days of trading, but computed on intraday bars including overnight sessions. The D1 close-based slope smooths over intraday noise; the H1 EMA30 captures where price actually is now vs the recent past.

**No gap up + EMA30 neg (n=17, PF=14.97, 11.10/15.53/25.71):** Strong new two-filter combo. All 3 years positive. n=17 is well above the small-n danger zone.

---

## C59d: Asia Net Magnitude Tiers

Testing whether the size of the Asia rally (relative to ATR) predicts SHORT performance.

Distribution on 32 qualifying trades: mean=1.094×ATR, median=0.912×ATR.  
Minimum qualifying is 0.25×ATR; 24/32 trades have asia_net ≥ 0.70×ATR.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Small net (0.25–0.4×ATR) | 5 | 4.31 | +0.130% | 40.0% | 3.54 | 0.00 | ~inf* |
| Mid net (0.4–0.7×ATR) | 6 | 7.73 | +0.250% | 50.0% | 1.59 | ~inf* | 3.47 |
| Large net (≥0.7×ATR) | 21 | 5.04 | +0.180% | 42.9% | 4.92 | 5.29 | 4.78 |

*~inf = single-year zero-loss artifact at tiny n.

**Key finding:** The asia_net floor (0.25×ATR) combined with Asia range always ≥1.2×ATR means most qualifying trades have large asia_net. The large net group (n=21) mirrors the full baseline (PF=5.04 vs 5.38) — no improvement. Small/mid groups are statistically void.

**Verdict: PERMANENTLY REJECTED. Distribution too skewed (24/32 large net). Entry condition already selects for large nets. No usable split.**

---

## Summary: C59 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C59a: Asia velocity | Year-inconsistent in both buckets | REJECTED |
| C59b: H4 pre-entry bar | n=9, PF=9.35, 2026 PF=2.17 weak | Small-n curiosity, re-test 2027+ |
| **C59c: EMA30(H1) slope** | **n=21, PF=9.28, all 3 years; C53b+EMA30 n=11, PF=26.87, 25+/yr** | **NEW CANDIDATE** |
| C59d: Asia net magnitude | Skewed to large net; no variation | PERMANENTLY REJECTED |

**C59c is the most important finding since C53b.** The EMA30(H1) slope is a clean, year-consistent binary filter with a large negative group (n=21, PF=9.28) and a strongly negative positive group (n=11, PF=1.43). The combination C53b + EMA30 neg (n=11, 25.92/28.86/25.71) is the most year-consistent result in this research.

---

## Updated Pending Candidates Table (all cycles through C59)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **SK<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best prior combo** |
| **C56c** | **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | **Gap-up exclusion, SK<60** |
| **C57a** | **Baseline + no gap up** | **25** | **7.90** | **+0.248%** | **FXOpen 2027** | **Standalone gap exclusion** |
| **C59c** | **EMA30(H1) slope < 0** | **21** | **9.28** | **+0.269%** | **FXOpen 2027** | **NEW — all 3 yrs 8+** |
| **C59c-b** | **C53b + EMA30(H1) < 0** | **11** | **26.87** | **+0.415%** | **FXOpen 2028** | **NEW — all 3 yrs 25+ (!!!)** |
| **C59c-c** | **No gap up + EMA30(H1) < 0** | **17** | **14.97** | **+0.348%** | **FXOpen 2028** | **NEW — all 3 yrs positive** |
| C52c-b | SK<60 alone | 15 | 13.21 | +0.324% | FXOpen 2028 | |
| C51a | RSI(14)<55 | 22 | 8.97 | +0.268% | FXOpen 2027-28 | |
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 | |
| C48b | Bar07 bearish | 20 | 10.69 | +0.292% | FXOpen 2027-28 | |
| C35 | Bear07 gap down | 19 | 10.33 | +0.319% | FXOpen 2027-28 | |
| C37 | ATR expanding | 17 | 8.52 | +0.252% | FXOpen 2027 | |
| C43 | 0-1 prior Asia up | 16 | 8.53 | +0.292% | FXOpen 2027-28 | |
| C42 | Skip Q2 | 24 | 7.22 | +0.236% | FXOpen 2027 | |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 | |
| C51b | C48b + C46c | 16 | 12.18 | +0.343% | FXOpen 2028 | |
| C52b | RSI<55 + D1slope | 17 | 12.26 | +0.325% | FXOpen 2028 | Superseded by C53b |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 | |
| C45b | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 | |
| C46c | ATR ≥ 7pip | 28 | 5.92 | +0.209% | FXOpen 2027 | |

---

## Permanently Rejected (C59 scope)

- **C59a (Asia velocity):** Year-inconsistent. Both high/low buckets show year inversions.
- **C59d (Asia net magnitude):** 24/32 qualifying trades have large net — structurally collinear with entry condition.

---

*Past results are not investment advice.*
