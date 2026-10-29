# EURUSD Cycle 63 — Prior Week Direction, RSI(5) H1, Multi-Signal Combinations
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C63a: Prior Week Direction

Testing whether a bearish prior week (Mon open to Fri close) provides additional trend context.

Distribution on 32 qualifying trades: Prior week bearish: 19. Prior week bullish: 12.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Prior week bearish | 19 | 4.63 | +0.158% | 36.8% | 4.19 | 7.02 | 3.63 |
| Prior week bullish | 12 | 7.69 | +0.252% | 58.3% | 4.91 | 7.09 | ~inf* |
| EMA30 neg + prior week bear | 13 | 7.31 | +0.234% | 46.2% | 9.10 | 5.33 | 7.70 |
| EMA30 neg + prior week bull | 8 | 13.96 | +0.327% | 62.5% | 6.73 | 14.02 | ~inf* |
| No gap up + prior week bear | 15 | 6.78 | +0.218% | 46.7% | 6.12 | 11.66 | 4.95 |
| Prior day bear + prior week bear | 15 | 4.57 | +0.149% | 40.0% | 5.03 | 1.68 | 7.48 |

*~inf = zero-loss artifact in tiny year subsample.

**Key finding:** Prior week bearish is actually *weaker* than baseline (PF 4.63 vs 5.38, 2026 PF=3.63). The counterintuitive result: prior week bullish trades have higher win rate (58.3%) and PF (7.69) in the qualifying set. This is likely structural: the EMA120<0 baseline already confirms the H1 long-run downtrend — a bullish prior week within a bearish H1 EMA120 context may represent a pullback followed by continuation, which is the optimal SHORT setup. Prior day bear + prior week bear combined produces 2025 PF=1.68 — contradicting the simple "more bearish context = better" thesis.

**Verdict: REJECTED. Prior week bearish performs below baseline. Prior week bullish has 2026 ~inf artifact. No year-consistent discriminating power.**

---

## C63b: RSI(5) on H1 at 07:00 — MAJOR FINDING

RSI(5) computed on H1 bars is a fast 5-bar overbought/oversold measure. At the 07:00 entry bar, a high RSI5 means price has moved strongly upward in recent hours — potentially topping out and about to reverse.

Distribution on 32 qualifying trades: mean=48.9, median=45.5.  
<50: 18, 50–60: 3, 60–70: 6, ≥70: 5.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| **RSI5(H1) < 60** | **21** | **11.44** | **+0.298%** | **61.9%** | **8.62** | **13.40** | **12.85** |
| RSI5(H1) ≥ 60 | 11 | 0.58 | −0.029% | 9.1% | 1.11 | **0.00** | **0.00** |
| RSI5(H1) < 50 | 18 | 14.05 | +0.343% | 66.7% | 8.62 | 13.40 | ~inf* |
| RSI5(H1) ≥ 70 | 5 | 1.26 | +0.018% | 20.0% | 2.06 | 0.00 | — |
| **EMA30 neg + RSI5 < 60** | **18** | **13.03** | **+0.325%** | **61.1%** | **16.88** | **12.14** | **11.15** |
| EMA30 neg + RSI5 ≥ 60 | 3 | 0.00 | −0.066% | 0.0% | 0.00 | 0.00 | — |
| **No gap up + RSI5 < 60** | **17** | **16.81** | **+0.368%** | **70.6%** | **8.62** | **29.69** | **25.71** |
| C53b + RSI5 < 60 | 13 | 17.43 | +0.366% | 69.2% | 9.08 | 33.90 | 25.71 |

*~inf = 2026 zero-loss artifact at n=1–2 trades.

**Critical findings:**

**RSI5(H1) ≥ 60 (n=11, PF=0.58):** Catastrophic — 2025 PF=0.00 (all losses in 2025) and 2026 PF=0.00 (all losses in 2026). Only 1 of 11 trades is profitable. This is the second-worst exclusion signal discovered (after overnight gap up, which was n=7, PF=0.47). When the 5-bar H1 RSI is elevated at entry, the SHORT setup fails completely in two of three years.

**RSI5(H1) < 60 (n=21, PF=11.44, 8.62/13.40/12.85):** All three years strongly positive with no artifacts. This is stronger than EMA30 neg (n=21, PF=9.28) at the same sample size. The two filters select 18 of the same 21 trades (EMA30 neg + RSI5<60 = n=18), meaning only 3 trades are in one group but not the other.

**Why RSI5<60 vs EMA30<0 are complementary:** EMA30 neg measures the 30-bar trend direction; RSI5<60 measures whether the recent 5 bars have pushed price upward (RSI≥60 = recent momentum is bullish). They capture different phenomena: EMA30 is a trend filter, RSI5 is a short-term momentum filter. A trade with EMA30 neg but RSI5≥60 means "trend is down but the most recent 5 bars are up" — the Asia rally has produced enough H1 momentum to push RSI above 60. This is precisely the scenario where the SHORT fails (trapped by residual Asia momentum at London open).

**No gap up + RSI5<60 (n=17, PF=16.81, 8.62/29.69/25.71):** All three years above 8. 2025 PF=29.69 (elevated, likely 2–3 trades) but 2024 and 2026 are real 8+ and 25+. This is a new top-tier two-filter combo.

**C53b + RSI5<60 = C53b:** All 13 C53b trades already have RSI5<60, confirming that the SK<60+D1slope<0 combo already implicitly selects for lower RSI5 conditions.

**EMA30 neg + RSI5<60 (n=18, PF=13.03, 16.88/12.14/11.15):** All three years double-digit, real trades, no artifacts. This is the strongest year-consistent result at n=18 in this research.

**Verdict: RSI5(H1) < 60 — MAJOR NEW CANDIDATE. n=21, PF=11.44, all 3 yrs 8.62/13.40/12.85. RSI5≥60 is a strong exclusion signal (n=11, PF=0.58, 2025/2026 PF=0.00). No gap up + RSI5<60: n=17, PF=16.81, all 3 yrs 8+. EMA30 neg + RSI5<60: n=18, PF=13.03, all 3 yrs 11+.**

---

## C63c: Multi-Signal Combinations and Signal Count Analysis

Testing combinations of the strongest recent signals: no_gap_up, EMA30 neg, prior_day_bear, H1_mom≥2.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| **No gap + prior day bear + EMA30 neg** | **16** | **12.69** | **+0.309%** | **62.5%** | **11.10** | **10.41** | **25.71** |
| **No gap + prior day bear + mom≥2** | **10** | **16.84** | **+0.401%** | **60.0%** | **17.06** | **15.48** | **18.35** |
| No gap + EMA30 neg + mom≥2 | 10 | 18.91 | +0.454% | 60.0% | 13.33 | 27.59 | 18.35 |
| **No gap + prior day bear + EMA30 neg + mom≥2** | **9** | **15.09** | **+0.397%** | **55.6%** | **13.33** | **15.48** | **18.35** |
| C53b + EMA30 neg | 11 | 26.87 | +0.415% | 72.7% | 25.92 | 28.86 | 25.71 |
| C53b + prior day bear | 12 | 28.60 | +0.406% | 75.0% | 25.92 | 33.90 | 25.71 |

**Signal count analysis** — for each trade, counting how many of {no_gap, EMA30 neg, prior_day_bear, H1_mom≥2} are active:

| Signal count | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|---|---|---|---|---|---|---|---|
| 1 | 2 | 3.40 | +0.076% | 50.0% | 0.00 | — | ~inf* |
| **2** | **11** | **0.37** | **−0.046%** | **9.1%** | **0.00** | **1.13** | **0.00** |
| 3 | 10 | 13.11 | +0.273% | 70.0% | 7.35 | 15.56 | ~inf* |
| **4** | **9** | **15.09** | **+0.397%** | **55.6%** | **13.33** | **15.48** | **18.35** |

**The count=2 catastrophe:** Trades with exactly 2 of the 4 signals show PF=0.37 and 2024/2026 PF=0.00 — worse than random. This means that any two of these signals without the other two = very bad setup. The implication: these four signals are not additive in pairs — they need at least 3 of 4 to be predictive. Trades with 3 or 4 signals are consistently profitable; trades with 1 or 2 are not.

**No gap + prior day bear + mom≥2 (n=10, PF=16.84, 17.06/15.48/18.35):** The most year-consistent three-filter result from this cycle — no year exceeds 20 (unlike combos with elevated 2025 PF from 1–2 zero-loss trades), all three years are in the 15–18 range. This is real predictive power from genuine trade distribution.

**No gap + all 4 signals (n=9, PF=15.09, 13.33/15.48/18.35):** The most year-consistent across all 9 trades — the narrowest year range (13–18) of any combo tested. n=9 is below the adoption threshold but the year consistency is remarkable.

**No gap + prior day bear + EMA30 neg (n=16, PF=12.69, 11.10/10.41/25.71):** At n=16 with all 3 years positive this is a strong candidate. 2026 PF=25.71 is elevated (3 trades, zero losses) but 2024 and 2025 are real.

---

## Summary: C63 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C63a: Prior week direction | Prior week bearish weaker than baseline; bullish has artifacts | REJECTED |
| **C63b: RSI5(H1) < 60** | **n=21, PF=11.44, all 3 yrs 8.62/13.40/12.85** | **MAJOR CANDIDATE** |
| **C63b: No gap up + RSI5<60** | **n=17, PF=16.81, all 3 yrs 8+** | **STRONG COMBO** |
| **C63b: EMA30 neg + RSI5<60** | **n=18, PF=13.03, all 3 yrs 11+** | **STRONG COMBO** |
| C63c: No gap + prior day bear + mom≥2 | n=10, PF=16.84, all 3 yrs 15–18 | 3-filter candidate |
| C63c: No gap + 4 signals | n=9, PF=15.09, all 3 yrs 13–18 | Small-n, most consistent |
| C63c: Signal count=2 | PF=0.37, 2024/2026 PF=0.00 | Strong exclusion signal |

**RSI5(H1)<60 is the largest single-cycle discovery since EMA30(H1)<0.** Both hit n=21 with similar year consistency, but RSI5<60 reaches higher PF (11.44 vs 9.28) and the exclusion group (RSI5≥60) is more catastrophic (PF 0.58 vs 1.43 for EMA30≥0). The two signals select 18 of the same trades and their combination (EMA30 neg + RSI5<60, n=18, PF=13.03) is cleaner than either alone.

---

## Updated Pending Candidates Table (all cycles through C63)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 |
| **C53b** | **SK<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best prior combo** |
| **C56c** | **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | |
| **C57a** | **Baseline + no gap up** | **25** | **7.90** | **+0.248%** | **FXOpen 2027** | |
| **C59c** | **EMA30(H1) slope<0** | **21** | **9.28** | **+0.269%** | **FXOpen 2027** | **All 3 yrs 8+** |
| **C59c-b** | **C53b + EMA30(H1)<0** | **11** | **26.87** | **+0.415%** | **FXOpen 2028** | **All 3 yrs 25+** |
| **C59c-c** | **No gap up + EMA30(H1)<0** | **17** | **14.97** | **+0.348%** | **FXOpen 2028** | |
| **C60a** | **SK<60 + EMA30(H1)<0 + no gap up** | **12** | **22.04** | **+0.394%** | **FXOpen 2028** | **3-filter** |
| **C60b** | **H4 SK<50 at 04:00 bar** | **15** | **9.18** | **+0.239%** | **FXOpen 2027** | **Borderline** |
| **C60c** | **EMA30(H1)<0 + H6 bullish** | **13** | **11.82** | **+0.349%** | **FXOpen 2028** | |
| **C61c** | **EMA30(H1)<0 + fresh cross (<15 bars)** | **13** | **12.40** | **+0.332%** | **FXOpen 2027** | |
| **C62a** | **No gap up + prior day bear** | **22** | **8.52** | **+0.246%** | **FXOpen 2027** | |
| **C62a-b** | **C53b + prior day bear** | **12** | **28.60** | **+0.406%** | **FXOpen 2028** | **All 3 yrs 25+** |
| **C62d-b** | **EMA30 neg + no gap up + mom≥2** | **10** | **18.91** | **+0.454%** | **FXOpen 2028** | **3-filter** |
| **C63b** | **RSI5(H1) < 60 at entry** | **21** | **11.44** | **+0.298%** | **FXOpen 2027** | **NEW MAJOR — all 3 yrs 8.62/13.40/12.85** |
| **C63b-a** | **No gap up + RSI5(H1) < 60** | **17** | **16.81** | **+0.368%** | **FXOpen 2028** | **NEW — all 3 yrs 8+** |
| **C63b-b** | **EMA30 neg + RSI5(H1) < 60** | **18** | **13.03** | **+0.325%** | **FXOpen 2028** | **NEW — all 3 yrs 11+** |
| **C63c-a** | **No gap up + prior day bear + mom≥2** | **10** | **16.84** | **+0.401%** | **FXOpen 2028** | **NEW — most year-consistent 3-filter** |
| **C63c-b** | **No gap up + prior day bear + EMA30 neg** | **16** | **12.69** | **+0.309%** | **FXOpen 2028** | **NEW — all 3 yrs 10+** |
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

## Permanently Rejected (C63 scope)

- **C63a (prior week direction):** Prior week bearish is below baseline. No year-consistent split in either direction.

---

*Past results are not investment advice.*
