# EURUSD Cycle 62 — Prior Day Direction, Weekly Open, Asia Compactness, H1 Momentum Combos
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C62a: Prior Day Close Direction — CANDIDATES

Testing whether the entry day's prior-day close (Tue for Wed entry, Wed for Thu) was bearish (close < open), confirming the intermediate-term trend.

Distribution on 32 qualifying trades: Prior day bearish: 26. Prior day bullish: 6. Strongly skewed toward prior-day bearish — the EMA120<0 baseline already selects downtrend conditions.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Prior day bearish | 26 | 5.87 | +0.195% | 46.2% | 5.37 | 4.95 | 10.82 |
| Prior day bullish | 6 | 3.76 | +0.145% | 33.3% | 0.00 | ~inf* | 1.56 |
| **No gap up + prior day bear** | **22** | **8.52** | **+0.246%** | **54.5%** | **6.11** | **12.03** | **10.82** |
| No gap up + prior day bull | 3 | 5.38 | +0.262% | 33.3% | 0.00 | ~inf* | 0.00 |
| **C53b + prior day bear** | **12** | **28.60** | **+0.406%** | **75.0%** | **25.92** | **33.90** | **25.71** |
| EMA30 neg + prior day bear | 19 | 8.78 | +0.251% | 52.6% | 8.48 | 6.12 | 25.71 |

*~inf = zero-loss artifact in a tiny year subsample.

**Key findings:**

**Prior day bullish (n=6):** Catastrophic — 2024 PF=0.00 (all losses), 2025 ~inf artifact, 2026 PF=1.56. Confirmed as a strong exclusion signal. When the prior day was UP into a Wednesday/Thursday Asia-up setup, the SHORT consistently fails. This aligns with: when two consecutive days show upward momentum (prior day bull + Asia up tonight), the trend is not just intact but strengthening — the SHORT fades a sustained move, not an overextension.

**No gap up + prior day bear (n=22, PF=8.52):** All three years cleanly positive (6.11/12.03/10.82). This is a genuine new two-filter candidate at n=22, well above the small-n boundary. Slightly weaker than C59c (9.28) but at higher n and with a different filter dimension.

**C53b + prior day bear (n=12, PF=28.60):** All three years at 25+ (25.92/33.90/25.71). This is the same pattern as C53b+EMA30 neg — both reach the 25+ level across all years. n=12 is at the small-n boundary.

**EMA30 neg + prior day bear (n=19):** 2025 drops to PF=6.12 (from 9.12 in EMA30 neg alone) when requiring prior day bear — this combination is weaker than EMA30 neg alone despite having lower n. The two signals are not as complementary as expected. 2026 is excellent (25.71) but 2025 weakness is concerning.

**Verdict: NO GAP UP + PRIOR DAY BEAR — NEW CANDIDATE (n=22, PF=8.52, all 3 years 6+). C53B + PRIOR DAY BEAR — SMALL-N CANDIDATE (n=12, PF=28.60, all 3 yrs 25+, re-test 2028).**

---

## C62b: Price Above/Below Weekly Open at 07:00 Entry

Testing whether the entry price being above or below the current week's opening price provides directional context for the fade.

Distribution: Above weekly open: 9. Below weekly open: 23.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Above weekly open | 9 | 6.28 | +0.186% | 44.4% | 1.93 | ~inf* | 4.07 |
| Below weekly open | 23 | 5.10 | +0.186% | 43.5% | 4.34 | 4.95 | 11.13 |
| EMA30 neg + above weekly open | 6 | 9.68 | +0.266% | 50.0% | 4.21 | ~inf* | 4.51 |
| EMA30 neg + below weekly open | 15 | 9.13 | +0.271% | 53.3% | 9.86 | 6.12 | ~inf* |
| No gap up + below weekly open | 18 | 8.15 | +0.259% | 55.6% | 5.67 | 12.03 | 11.13 |

*~inf = tiny-n year zero-loss artifact.

**Key finding:** The weekly open split produces no clean discrimination. Both buckets have ~same avg% (+0.186%). Every combination with weekly open has at least one year with a ~inf artifact from tiny within-year subsamples. The "above weekly open" group is only n=9 — too small to be meaningful. Both EMA30 neg sub-splits have a ~inf year artifact.

**Verdict: PERMANENTLY REJECTED. Weekly open provides no discriminating power in this dataset. The above/below split is 9/23 with significant artifact contamination.**

---

## C62c: Asia Range / Prior Day Range (Compact Asia)

Testing whether a compact Asia session (small range relative to the prior day) predicts better SHORT outcomes.

Distribution on 32 qualifying trades: mean=0.42, median=0.36.  
<0.5: 24, 0.5–1.0: 7, ≥1.0: 1. Strongly skewed — 87.5% of qualifying trades have a compact Asia.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Compact Asia (<0.6 ratio) | 28 | 5.37 | +0.177% | 42.9% | 4.24 | 6.50 | 6.05 |
| Very compact (<0.4) | 18 | 3.52 | +0.121% | 33.3% | 4.81 | 0.00 | 15.31 |
| Wide Asia (≥0.6) | 4 | 5.44 | +0.246% | 50.0% | 2.13 | 8.86 | — |
| EMA30 neg + compact | 18 | 8.94 | +0.253% | 50.0% | 7.46 | 9.26 | 11.15 |
| C53b + compact | 11 | 27.23 | +0.421% | 72.7% | 21.98 | 33.90 | 25.71 |
| No gap up + compact | 21 | 8.70 | +0.248% | 52.4% | 5.51 | 28.46 | 7.16 |

**Key finding:** 28 of 32 qualifying trades (87.5%) have compact Asia (<0.6 of prior day). This is structurally determined by the entry conditions: asia_range typically stays compact on days when the overnight net move is 0.25–1×ATR because sustained rallies require range. The compact filter is effectively the same dataset minus 4 wide trades. Very compact (<0.4, n=18) has 2025 PF=0.00 — catastrophic.

**Verdict: PERMANENTLY REJECTED. Structurally collinear with entry conditions — 87.5% of trades qualify. Very compact bucket shows year-catastrophic 2025. No usable split.**

---

## C62d: H1 Momentum Combos — MAJOR FINDING

Building on C61d (high H1 momentum n=8), testing broader thresholds and three-filter combos.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| **H1 mom ≥2 (broader)** | **18** | **7.16** | **+0.260%** | **44.4%** | **5.77** | **10.15** | **6.33** |
| **EMA30 neg + mom ≥2** | **12** | **12.59** | **+0.368%** | **50.0%** | **9.08** | **27.59** | **7.95** |
| EMA30 neg + mom ≥3 | 7 | 15.71 | +0.435% | 57.1% | 28.47 | 15.48 | 6.08 |
| **No gap up + mom ≥2** | **13** | **12.09** | **+0.369%** | **53.8%** | **8.74** | **27.59** | **8.28** |
| No gap up + mom ≥3 | 5 | 40.72 | +0.635% | 80.0% | ~inf* | 15.48 | ~inf* |
| **EMA30 neg + no gap up + mom≥2** | **10** | **18.91** | **+0.454%** | **60.0%** | **13.33** | **27.59** | **18.35** |
| C53b + mom ≥2 | 7 | 22.78 | +0.522% | 71.4% | 13.98 | ~inf* | 18.35 |

*~inf = zero-loss year artifact.

**Critical findings:**

**EMA30 neg + no gap up + mom≥2 (n=10, PF=18.91, 13.33/27.59/18.35):** All three years are real, no infinity artifacts. 2024: 13.33 (6 real trades), 2025: 27.59 (2 real trades — elevated but not artifact), 2026: 18.35 (2 real trades). n=10 is at the small-n boundary but every year has genuine wins and losses. This is a three-filter combination with consistent year behavior.

**No gap up + mom≥2 (n=13, PF=12.09, 8.74/27.59/8.28):** All three years above 8. 2025 elevated from small-n but not ~inf. This is the cleanest two-filter result from C62 — n=13, straightforward, no gaps in year coverage.

**H1 mom≥2 standalone (n=18, PF=7.16, 5.77/10.15/6.33):** All three years positive, modest improvement over baseline. This is essentially "half the trades where ≥2 of 5 pre-entry bars were bearish."

Economic interpretation: H1 momentum score ≥2 means at least 2 of the 5 hourly bars from 02:00–06:00 closed bearish. This is a lower threshold than ≥3 (C61d), catching more of the final-Asia-hour weakness pattern. The combination with EMA30 neg and no-gap-up creates a three-way confirmation: (1) H1 trend currently bearish [EMA30 neg], (2) no overnight gap up to reset the SHORT premise [no gap up], (3) the last 5 pre-London bars showed at least moderate bearish pressure [mom≥2].

**No gap up + mom≥3 (n=5):** 2024 and 2026 near-infinity from n=2 and n=1 trades — too small to evaluate.

**Verdict: NO GAP UP + MOM≥2 — NEW CANDIDATE (n=13, PF=12.09, all 3 yrs 8+). EMA30 NEG + NO GAP UP + MOM≥2 — THREE-FILTER CANDIDATE (n=10, PF=18.91, all 3 yrs 13+/real).**

---

## Summary: C62 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| **C62a: Prior day direction** | **No gap up + prior day bear: n=22, PF=8.52, all 3 yrs 6+** | **NEW CANDIDATE** |
| C62a-combo: C53b + prior day bear | n=12, PF=28.60, all 3 yrs 25+ | Small-n candidate |
| C62b: Weekly open | Both buckets year-inconsistent, artifact-laden | PERMANENTLY REJECTED |
| C62c: Asia compactness | 87.5% compact — collinear with entry conditions | PERMANENTLY REJECTED |
| **C62d: No gap up + mom≥2** | **n=13, PF=12.09, all 3 yrs 8+** | **NEW CANDIDATE** |
| **C62d: EMA30 + no gap up + mom≥2** | **n=10, PF=18.91, all 3 yrs 13+** | **Three-filter candidate** |

**Two new two-filter candidates and one three-filter candidate found.** Prior day direction joins the growing body of evidence that consecutive bearish signals (EMA120<0, EMA30<0, prior day bear, H1 pre-entry weakness) compound in predictive power for the Asia-London SHORT. The weekly open and Asia compactness are permanently closed as avenues.

---

## Updated Pending Candidates Table (all cycles through C62)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 |
| **C53b** | **SK<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best prior combo** |
| **C56c** | **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | |
| **C57a** | **Baseline + no gap up** | **25** | **7.90** | **+0.248%** | **FXOpen 2027** | |
| **C59c** | **EMA30(H1) slope<0** | **21** | **9.28** | **+0.269%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C59c-b** | **C53b + EMA30(H1)<0** | **11** | **26.87** | **+0.415%** | **FXOpen 2028** | **All 3 yrs 25+** |
| **C59c-c** | **No gap up + EMA30(H1)<0** | **17** | **14.97** | **+0.348%** | **FXOpen 2028** | |
| **C60a** | **SK<60 + EMA30(H1)<0 + no gap up** | **12** | **22.04** | **+0.394%** | **FXOpen 2028** | **3-filter, no artifacts** |
| **C60b** | **H4 SK<50 at 04:00 bar** | **15** | **9.18** | **+0.239%** | **FXOpen 2027** | **Borderline** |
| **C60c** | **EMA30(H1)<0 + H6 bullish** | **13** | **11.82** | **+0.349%** | **FXOpen 2028** | **Final Asia bar paradox** |
| **C61c** | **EMA30(H1)<0 + fresh cross (<15 bars)** | **13** | **12.40** | **+0.332%** | **FXOpen 2027** | **Borderline** |
| **C61d** | **H1 momentum score ≥3** | **8** | **16.75** | **+0.408%** | **FXOpen 2027** | **Small-n** |
| **C62a** | **No gap up + prior day bear** | **22** | **8.52** | **+0.246%** | **FXOpen 2027** | **NEW — all 3 yrs 6+** |
| **C62a-b** | **C53b + prior day bear** | **12** | **28.60** | **+0.406%** | **FXOpen 2028** | **NEW — all 3 yrs 25+** |
| **C62d-a** | **No gap up + H1 mom≥2** | **13** | **12.09** | **+0.369%** | **FXOpen 2028** | **NEW — all 3 yrs 8+** |
| **C62d-b** | **EMA30 neg + no gap up + mom≥2** | **10** | **18.91** | **+0.454%** | **FXOpen 2028** | **NEW — 3-filter, all 3 yrs 13+** |
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

## Permanently Rejected (C62 scope)

- **C62b (weekly open):** Year-inconsistent in both buckets, multiple ~inf artifacts from n=9/23 split.
- **C62c (Asia compactness):** 87.5% of trades compact — collinear with entry conditions. Very compact group 2025 PF=0.00.

---

*Past results are not investment advice.*
