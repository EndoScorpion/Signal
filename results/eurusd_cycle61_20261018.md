# EURUSD Cycle 61 — EMA30 Magnitude, EMA50(H1), Bars Since Cross, H1 Momentum Score
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C61a: EMA30(H1) Slope Magnitude (normalized by ATR)

Testing whether steeper negative EMA30 slope predicts better outcomes than shallower negative slope.

**Normalization result:** All 21 EMA30-negative qualifying trades have raw-normalized slope <−0.001 — the normalization produces no spread (the threshold collapses). Raw slope used instead.

Raw slope on 21 neg trades: mean=−0.000055, median=−0.000043, p25=−0.000082, p75=−0.000022.

Splitting at median (−0.000043):

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **EMA30 neg baseline** | **21** | **9.28** | **+0.269%** | **52.4%** | **8.48** | **9.12** | **11.15** |
| Below median (steeper) | 10 | 14.49 | +0.326% | 70.0% | ~inf* | 10.03 | ~inf* |
| Above median (shallower) | 11 | 6.42 | +0.218% | 36.4% | 7.46 | 6.39 | 4.51 |

*~inf = zero-loss artifact in year with 1–3 trades.

**Key finding:** The below-median (steeper) split has 2024 and 2026 near-infinity from tiny within-year n. The above-median (shallower) group (n=11, PF=6.42) actually has clean year-by-year data but represents a downgrade from the full EMA30 neg group — at 7.46/6.39/4.51. No clean threshold within the EMA30<0 group separates better outcomes.

**Verdict: REJECTED. No usable slope magnitude threshold found. The EMA30<0 binary is the natural boundary; subdividing by magnitude produces n=10 artifacts.**

---

## C61b: EMA50(H1) Slope at 07:00

EMA50 on H1 bars is a slower intraday trend than EMA30 (50 bars ≈ 2.1 calendar days). Testing whether it provides independent signal.

Distribution on 32 qualifying trades: Negative: 25. Positive: 7. Mean=−0.000040.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| EMA50 slope < 0 | 25 | 5.50 | +0.196% | 44.0% | 4.67 | 6.39 | 5.23 |
| EMA50 slope ≥ 0 | 7 | 4.88 | +0.150% | 42.9% | 2.17 | ~inf* | 8.55 |
| EMA30 neg + EMA50 neg | 20 | 8.44 | +0.254% | 50.0% | 8.48 | 9.12 | 6.64 |
| EMA30 neg + EMA50 pos | 1 | inf | +0.570% | 100.0% | — | — | ~inf* |
| C53b + EMA50 neg | 11 | 14.40 | +0.353% | 63.6% | 9.08 | 28.86 | 15.31 |
| No gap up + EMA50 neg | 19 | 8.35 | +0.267% | 52.6% | 5.37 | 15.53 | 6.45 |

*~inf = tiny-n year artifact.

**Key finding:** EMA50 slope<0 covers 25/32 qualifying trades and adds almost nothing over baseline (PF 5.50 vs 5.38). The positive group (n=7) has a 2025 infinity artifact. When combined with EMA30 neg, we get n=20 vs n=21 for EMA30 neg alone — losing one trade for a PF drop (8.44 vs 9.28) and a weaker 2026 (6.64 vs 11.15). EMA50 is structurally similar to EMA30 at the H1 level and provides no independent information at the 50-bar timescale in this data.

**Verdict: REJECTED. EMA50 is dominated by EMA30<0. Adding it as a filter only reduces n and PF. Not an independent signal at H1 50-bar timescale.**

---

## C61c: Bars Since EMA30 Last Crossed Zero — CANDIDATE

Testing whether a "fresh" EMA30 slope reversal (recent cross from positive to negative) outperforms an established bearish EMA30 trend.

Distribution on 21 EMA30-negative qualifying trades: mean=13.6 bars, median=3.0.  
<10 bars: 13, 10–30 bars: 5, 30–70 bars: 3, ≥70 bars: 0.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **EMA30 neg baseline** | **21** | **9.28** | **+0.269%** | **52.4%** | **8.48** | **9.12** | **11.15** |
| Fresh EMA30 neg (<15 bars) | 13 | **12.40** | **+0.332%** | **61.5%** | **16.88** | **8.99** | **14.04** |
| Established EMA30 neg (≥15) | 8 | 5.39 | +0.167% | 37.5% | 0.00 | 9.32 | 7.37 |
| Long-established (≥50 bars) | 2 | 22.28 | +0.591% | 50.0% | 0.00 | ~inf* | — |
| C53b + fresh EMA30 neg | 6 | 50.79 | +0.506% | 83.3% | 25.92 | ~inf* | ~inf* |
| C53b + established EMA30 neg | 5 | 14.22 | +0.305% | 60.0% | — | 20.43 | 7.37 |

**Key finding:** Fresh EMA30 neg (<15 bars since the slope crossed to negative, n=13): PF=12.40 with all three years strongly positive (16.88/8.99/14.04). The established group (≥15 bars, n=8) has 2024 PF=0.00 — catastrophic, meaning all 2024 trades in this bucket were losses.

Economic interpretation: When EMA30(H1) has *just* turned negative, the SHORT aligns with a fresh momentum reversal — the market recently stopped rising and is now pointing down. An established negative slope may represent a prolonged downtrend where price has already moved and the Asia bounce is a genuine reversion opportunity, weakening the SHORT thesis.

The C53b + fresh EMA30 neg (n=6) has the 2025/2026 infinity artifacts from within-year zero-loss, but 2024 PF=25.92 is real (same as C53b itself). n=6 is too small for standalone adoption.

**Verdict: BORDERLINE CANDIDATE. Fresh EMA30 neg (<15 bars): n=13, PF=12.40, all 3 years 8+. n=13 is at the small-n boundary. Re-test when n≥20 with 2027+ data. Economic logic is sound — fresh reversal vs established trend.**

---

## C61d: H1 Momentum Score (Bearish H1 Bars in Hours 2–6)

Testing whether the count of bearish H1 bar closes in the 5 bars immediately before the 07:00 entry (hours 2, 3, 4, 5, 6) predicts SHORT performance. Score 5 = all 5 bars bearish = strong intraday downward momentum.

Distribution on 32 qualifying trades: mean=1.81, median=2.0.  
Score 0: 2, Score 1: 12, Score 2: 10, Score 3: 6, Score 4: 2, Score 5: 0.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Low score (0–1 bear) | 14 | 3.10 | +0.090% | 42.9% | 1.48 | 4.29 | 5.36 |
| Mid score (==2 bear) | 10 | 3.58 | +0.143% | 30.0% | 1.50 | 7.05 | 4.69 |
| High score (≥3 bear) | 8 | **16.75** | **+0.408%** | **62.5%** | **28.47** | **15.48** | **9.09** |
| EMA30 neg + high score | 7 | 15.71 | +0.435% | 57.1% | 28.47 | 15.48 | 6.08 |
| C53b + high score | 4 | inf | +0.813% | 100.0% | ~inf* | ~inf* | ~inf* |
| No gap up + low score | 12 | 3.99 | +0.116% | 50.0% | 1.48 | 9.50 | 5.36 |

*All three C53b+high years have zero losses — artifact from n=4.

**Key finding:** High H1 momentum (≥3 of 5 pre-entry H1 bars bearish, n=8): PF=16.75, all three years clearly positive (28.47/15.48/9.09). 2026 PF=9.09 is the weakest but still strong. The low-score group (n=14, essentially the "Asia rallied with minimal H1 intraday weakness") has 2024 PF=1.48 — near breakeven in the earliest year.

Economic interpretation: If the 5 H1 bars before the 07:00 London entry show ≥3 bearish closes, it means the intraday short-term trend is weakening despite the Asia net-up filter having fired. The SHORT at London open fades an overnight rally that has started to lose momentum in its final hours — the "trapped longs" setup is more fully formed.

The low/mid score groups combined (n=24) produce PF<4 — a significant drag on the baseline. High score is a genuine exclusion filter for the bottom 8 trades.

**Verdict: SMALL-N CANDIDATE. n=8, PF=16.75, all 3 years 9+. n=8 is below the threshold for standalone adoption, but direction and economic logic are strong. Re-test when n≥15. Combined with EMA30 neg: n=7, similar PF.**

---

## Summary: C61 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C61a: EMA30 slope magnitude | Median split produces n=10 artifacts; shallower bucket degrades | REJECTED |
| C61b: EMA50(H1) slope | 25/32 neg; adds nothing over EMA30<0 | REJECTED |
| **C61c: Bars since EMA30 cross** | **n=13, PF=12.40, all 3 yrs 8+; established group has 2024 PF=0** | **BORDERLINE CANDIDATE** |
| **C61d: H1 momentum score** | **High (≥3/5 bear): n=8, PF=16.75, all 3 yrs 9+** | **Small-n candidate** |

**EMA50 adds nothing once EMA30 is already in the filter set** — both measure intraday H1 trend direction and are highly collinear. The discovery of the "bars since cross" (C61c) is the more interesting finding: fresh EMA30 reversals are substantially better than established negative trends, suggesting the trade works best as a short-term momentum fade rather than a long-run trend-following filter.

---

## Updated Pending Candidates Table (all cycles through C61)

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
| **C61c** | **EMA30(H1)<0 + fresh cross (<15 bars)** | **13** | **12.40** | **+0.332%** | **FXOpen 2027** | **NEW — all 3 yrs 8+** |
| **C61d** | **H1 momentum score ≥3 (hrs 2–6)** | **8** | **16.75** | **+0.408%** | **FXOpen 2027** | **NEW — n=8 small-n** |
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

## Permanently Rejected (C61 scope)

- **C61a (EMA30 slope magnitude):** No clean threshold within EMA30<0. Median split produces tiny-n year artifacts.
- **C61b (EMA50(H1) slope):** Structurally collinear with EMA30(H1). No independent signal; reduces n without PF gain.

---

*Past results are not investment advice.*
