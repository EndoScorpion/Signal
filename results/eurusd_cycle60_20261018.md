# EURUSD Cycle 60 — Three-Filter EMA30 Combos, H4 Stochastic, Pre-Entry H1 Bar Direction
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C60a: Three-Filter Combos with EMA30(H1)

Building on C59c (EMA30(H1) slope<0 at 07:00 is a strong binary filter), testing whether adding a third filter to C53b+EMA30 or no-gap-up+EMA30 creates a viable three-filter combination.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| C53b + EMA30 neg | 11 | 26.87 | +0.415% | 72.7% | 25.92 | 28.86 | 25.71 |
| No gap up + EMA30 neg | 17 | 14.97 | +0.348% | 64.7% | 11.10 | 15.53 | 25.71 |
| **SK<60 + EMA30 neg + no gap up** | **12** | **22.04** | **+0.394%** | **75.0%** | **25.92** | **18.03** | **25.71** |
| C53b + no gap up + EMA30 neg | 10 | 40.91 | +0.462% | 80.0% | 25.92 | ~inf* | 25.71 |
| EMA30 neg + D1slope<0 | 16 | 13.18 | +0.330% | 56.2% | 9.10 | 20.45 | 11.15 |
| EMA30 neg + D1slope<0 + no gap up | 12 | 32.98 | +0.461% | 75.0% | 13.38 | ~inf* | 25.71 |

*~inf = zero losses in 2025 within this tiny set — artifact of eliminating 1-2 trades.

**Key finding: SK<60 + EMA30 neg + no gap up (n=12, PF=22.04)** is the cleanest three-filter combination tested. All three years show real, non-artifact PFs: 25.92/18.03/25.71. This is the only three-filter combination where n=12 has a genuine year-3 (2025) result rather than near-zero losses.

Note on C53b vs SK<60 within this combo: C53b = SK<60 + D1slope<0. The SK<60 + EMA30 neg + no gap up combination (n=12) is essentially C53b sans the D1slope filter, replaced by the no-gap-up exclusion. The C53b + no gap up + EMA30 neg (n=10) has 2025=~inf because the removal of 2 additional trades eliminates all 2025 losses — a 1-2 trade artifact.

**Economic logic:** The three-filter set confirms the SHORT from three independent timescales and mechanisms simultaneously:
1. SK<60: price is in the lower half of its 14-bar range at entry (not overbought on H1 scale)
2. EMA30(H1)<0: the 30-bar H1 trend is pointing down (recent 30-hour momentum is bearish)
3. No gap up: London opened below Asia close (no overnight momentum gap lifting the entry)

**Verdict: NEW CANDIDATE. SK<60 + EMA30(H1) neg + no gap up (n=12, PF=22.04, 25.92/18.03/25.71). Year-consistent, no artifacts. Re-test when n≥20 (estimated FXOpen 2028).**

---

## C60b: H4 Stochastic(5,3) at 04:00–07:59 Bar

The H4 bar from 04:00–07:59 (the pre-London H4 bar) carries the stochastic state on the 4-hour timeframe. Testing whether a low H4 stochastic at this bar confirms the SHORT entry.

H4 Stoch computation: standard 5-period stochastic on 4H bars (4H resample from UTC midnight alignment: bars at 00:00, 04:00, 08:00, …). The 04:00 bar is the last H4 bar before entry.

Distribution on 32 qualifying trades: mean=52.4, median=51.2.  
- <30: 9, 30–50: 6, 50–70: 7, ≥70: 10

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| **H4 SK<50 (oversold side)** | **15** | **9.18** | **+0.239%** | **60.0%** | **13.98** | **7.81** | **7.30** |
| H4 SK≥50 (overbought side) | 17 | 3.56 | +0.139% | 29.4% | 1.65 | 6.75 | 2.86 |
| H4 SK<30 | 9 | 10.38 | +0.195% | 66.7% | ~inf* | 5.51 | 17.77 |
| C53b + H4 SK<50 | 11 | 16.66 | +0.325% | 72.7% | 13.98 | 13.48 | 25.71 |
| EMA30 neg + H4 SK<50 | 12 | 14.36 | +0.289% | 66.7% | ~inf* | 5.51 | 11.15 |
| No gap up + H4 SK<50 | 12 | 17.17 | +0.316% | 75.0% | 13.98 | ~inf* | 11.60 |

*~inf = zero losses in that year within this tiny group — artifact.

**Key finding: H4 SK<50 (n=15, PF=9.18, 13.98/7.81/7.30)** — all three years positive with real values. H4 SK≥50 (n=17) is weak across all years: 1.65/6.75/2.86. The split is meaningful and consistent in direction.

The H4 stochastic is a new timescale: while the H1 Stoch(14,3) measures the 14-bar H1 range position (14 hours), the H4 Stoch(5,3) measures the 5-bar H4 range position (20 hours) on a coarser timeframe. When the H4 stochastic is below 50 at the 04:00 pre-entry bar, the short-to-medium 4H timeframe is in the lower half of its range — consistent with the SHORT bias.

**Distribution problem:** The baseline qualifying trades split almost evenly (15 SK<50, 17 SK≥50). Mean=52.4 confirms no strong bias. The filter is genuinely discriminating, not a structural artifact.

**Concern:** 2025 PF=7.81 is the weakest of the three years. While all years are positive, the 2025 performance is the least convincing. Combined configurations show artifacts (~inf in 2024 or 2025) from n<10 sub-groups.

**C53b + H4 SK<50 (n=11, PF=16.66, 13.98/13.48/25.71):** Genuinely good three-year consistency, no artifacts. But n=11 is below adoption threshold.

**Verdict: CANDIDATE (borderline). H4 SK<50 standalone (n=15, all 3 years positive at 13.98/7.81/7.30). The 2025 PF=7.81 is the weakest link. Re-test when n≥20 (FXOpen 2027+). Not as clean as C59c but adds H4 timescale confirmation.**

---

## C60b2: H4 RSI(14) at 04:00–07:59 Bar

Testing RSI(14) on H4 bars at the pre-entry bar.

Distribution on 32 qualifying trades: mean=42.0, median=41.4. 
- <40: 14, 40–50: 12, ≥50: 6. **Zero trades with H4 RSI≥60.**

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| H4 RSI<50 | 26 | 5.18 | +0.186% | 42.3% | 4.03 | 6.39 | 5.23 |
| H4 RSI≥50 | 6 | 6.49 | +0.186% | 50.0% | 3.25 | ~inf* | 8.55 |
| H4 RSI<40 | 14 | 6.58 | +0.185% | 50.0% | 1.23 | 9.26 | 15.31 |

**Key finding: H4 RSI is structurally biased toward low values on qualifying trades.** Mean=42 and zero trades above 60 means the baseline filter (EMA120<0, ADX<30) already selects for H4 bearish-RSI conditions. The H4 RSI<50 split covers 26/32 qualifying trades (81%) — nearly the full set. No discriminating power.

**Verdict: REJECTED. H4 RSI is structurally collinear with EMA120<0 baseline condition. Mean=42.0 on qualifying trades; barely any high-RSI qualifying trades exist. H4 RSI<40 shows 2024 PF=1.23 (near-breakeven). No independent filter value.**

---

## C60c: Consecutive Bearish H1 Bars Before 07:00 Entry

Testing whether bearish momentum in the 3 hours before the London open (hours 4, 5, 6) improves SHORT entry quality. Separately, testing whether the final Asia H1 bar (hour 6) direction matters.

Distribution on 32 qualifying trades:
- 0 bear bars (hrs 4-6): 7, 1 bear: 16, 2 bear: 8, 3 bear (all): 1. Mean=1.09.
- Hour 6 bearish: 12 trades. Hour 6 bullish: 20 trades.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| ≥2 of 3 pre-entry hrs bearish | 9 | 8.36 | +0.260% | 44.4% | 2.06 | 27.59 | 1.78 |
| 0 pre-entry hrs bearish | 7 | 0.54 | -0.030% | 14.3% | 0.00 | 0.00 | 3.30 |
| H6 bar bearish | 12 | 3.47 | +0.095% | 41.7% | 2.69 | 9.16 | 1.56 |
| **H6 bar bullish** | **20** | **6.36** | **+0.240%** | **45.0%** | **4.61** | **6.62** | **10.82** |
| **EMA30 neg + H6 bullish** | **13** | **11.82** | **+0.349%** | **53.8%** | **10.95** | **9.11** | **25.71** |
| EMA30 neg + H6 bearish | 8 | 5.24 | +0.140% | 50.0% | 5.80 | 9.16 | 0.00 |
| EMA30 neg + ≥2 bear hrs | 7 | 9.71 | +0.313% | 42.9% | 2.06 | 27.59 | 0.00 |
| No gap up + H6 bearish | 8 | 5.11 | +0.139% | 50.0% | 5.25 | 9.16 | 0.00 |

**Critical finding — H6 bullish paradox:**

**H6 bearish (n=12)** shows 2026 PF=1.56 (weak) — when the final Asia H1 bar is bearish, the SHORT is less reliable. The intuition "bearish bar before entry = good SHORT confirmation" is WRONG.

**H6 bullish (n=20, PF=6.36, 4.61/6.62/10.82):** When the final Asia bar is bullish, the SHORT outperforms. 2026 PF=10.82 is strong. This is counterintuitive but has an economic explanation: a bullish H6 bar means the Asia session closed on a final up-push into the London open. This creates a "final squeeze" before the London reversal — a stronger fade setup because the bullish H6 gives late longs an extra entry, loading up the short side with more trapped momentum.

**EMA30 neg + H6 bullish (n=13, PF=11.82, 10.95/9.11/25.71):** All three years at 9+, no artifacts. This is a genuine new finding — when the H1 EMA30 trend is already down but the final Asia bar is still closing up, the SHORT has a strong setup: bearish medium-term momentum colliding with one last bullish push.

**Concerning finding — 0 bearish pre-entry hrs (n=7):** PF=0.54, 2024/2025 PF=0.00. When all three pre-entry H1 bars are bullish, the SHORT almost always fails. This is a strong exclusionary signal.

**≥2 bear pre-entry hrs (n=9):** Year-inconsistent (2.06/27.59/1.78). Not reliable.

**Verdict:**
- **EMA30 neg + H6 bullish (n=13, PF=11.82, 10.95/9.11/25.71): NEW CANDIDATE.** All three years 9+, no artifacts, n=13. Re-test when n≥20 (FXOpen 2028).
- **0 bearish pre-entry hrs (n=7, PF=0.54): EXCLUSION SIGNAL.** When 0/3 pre-entry H1 bars are bearish, avoid the trade — 2024/2025 PF=0.00.
- **H6 bearish: PERMANENTLY REJECTED** — structurally worse than H6 bullish, 2026 PF=1.56.
- **≥2 consecutive bear hrs: REJECTED** — year-inconsistent.

---

## Summary: C60 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| **C60a: SK<60+EMA30neg+no gap up** | **n=12, PF=22.04, 25.92/18.03/25.71** | **NEW CANDIDATE — no artifacts** |
| C60b: H4 SK<50 | n=15, PF=9.18, all 3 yrs positive (13.98/7.81/7.30) | Borderline candidate — 2025 weakest |
| C60b2: H4 RSI | H4 RSI skewed low (mean=42); 26/32 trades below 50 | REJECTED — collinear with EMA120<0 |
| **C60c: EMA30 neg + H6 bullish** | **n=13, PF=11.82, 10.95/9.11/25.71** | **NEW CANDIDATE** |
| C60c: 0 bear pre-entry hrs exclusion | n=7, PF=0.54, 2024/2025 PF=0.00 | Exclusion signal (small n) |

**Two new candidates in C60:**
1. **SK<60 + EMA30(H1) neg + no gap up (n=12, PF=22.04):** First clean 3-filter combination with no year-artifacts. Confirms entry quality from three independent dimensions: H1 range position, H1 EMA trend, overnight gap direction.
2. **EMA30(H1) neg + H6 bullish (n=13, PF=11.82):** Counterintuitive but robust — when Asia closes its final bar up but the 30-bar H1 trend is still bearish, the SHORT outperforms. The final Asia bid creates the trapped-longs setup that the London reversal exploits.

---

## Updated Pending Candidates Table (all cycles through C60)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **SK<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best prior combo** |
| **C56c** | **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | **Gap-up exclusion, SK<60** |
| **C57a** | **Baseline + no gap up** | **25** | **7.90** | **+0.248%** | **FXOpen 2027** | **Standalone gap exclusion** |
| **C59c** | **EMA30(H1) slope<0** | **21** | **9.28** | **+0.269%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C59c-b** | **C53b + EMA30(H1)<0** | **11** | **26.87** | **+0.415%** | **FXOpen 2028** | **All 3 yrs 25+ (!!)** |
| **C59c-c** | **No gap up + EMA30(H1)<0** | **17** | **14.97** | **+0.348%** | **FXOpen 2028** | **All 3 yrs positive** |
| **C60a** | **SK<60 + EMA30(H1)<0 + no gap up** | **12** | **22.04** | **+0.394%** | **FXOpen 2028** | **NEW — 3 filters, no artifacts** |
| **C60b** | **H4 SK<50 at 04:00 bar** | **15** | **9.18** | **+0.239%** | **FXOpen 2027** | **NEW — all 3 yrs positive (borderline)** |
| **C60c** | **EMA30(H1)<0 + H6 bullish** | **13** | **11.82** | **+0.349%** | **FXOpen 2028** | **NEW — final Asia bar bullish paradox** |
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

## Permanently Rejected (C60 scope)

- **C60b2 (H4 RSI):** 26/32 qualifying trades have H4 RSI<50 (mean=42). Structurally collinear with EMA120<0. No discriminating power.
- **C60c H6 bearish:** 2026 PF=1.56 — final Asia bar bearish is structurally worse than bullish. Rejected.
- **C60c ≥2 consecutive bear hrs:** Year-inconsistent (2.06/27.59/1.78). Rejected.

---

*Past results are not investment advice.*
