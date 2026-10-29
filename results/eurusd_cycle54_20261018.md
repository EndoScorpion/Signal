# EURUSD Cycle 54 — MACD, Stoch K<60 Combos, EMA50 Context
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C54a: MACD(12,26,9) Histogram at Entry

MACD histogram at the 07:00 entry bar: is pre-entry momentum already negative?

Distribution on 32 qualifying trades: mean=+0.000194, median=+0.000177. Overwhelmingly positive — the Asia rally has already pushed MACD into bullish territory by 07:00.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| MACD hist < 0 | 2 | inf | +0.405% | 100.0% | ~inf | — | ~inf |
| MACD hist > 0 | 30 | 4.78 | +0.171% | 40.0% | 3.48 | 7.06 | 3.93 |
| MACD hist falling | 10 | 3.29 | +0.103% | 40.0% | 0.77 | ~inf* | 5.24 |

*2025 MACD hist falling PF=~inf due to zero losses in 2025 (very small n).

**Key finding: MACD is useless as a filter for this setup.** Only 2/32 qualifying trades have negative MACD histogram. The Asia rally requirement (asia_net≥0.25×ATR) already means the overnight move was net upward — MACD(12,26,9) on hourly bars will almost always be positive by 07:00 given a positive overnight session. There is no independent signal.

MACD hist falling (n=10) degrades performance: 2024 PF=0.77 (negative), making it year-inconsistent.

**Verdict: PERMANENTLY REJECTED. MACD histogram at entry is structurally collinear with the Asia net-up baseline condition — it cannot discriminate within the qualifying set.**

---

## C54b: Stoch K<60 × C43 (0-1 Prior Asia Up Days)

Testing intersection of two pending candidates: Stoch K<60 (n=15, PF=13.21) and C43 0-1 prior Asia up (n=16, PF=8.53).

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Stoch K<60 | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| 0-1 prior Asia up (C43) | 15 | 9.77 | +0.317% | 53.3% | 12.90 | 10.37 | 4.54 |
| Stoch K<60 + 0-1 consec | 9 | 10.29 | +0.348% | 55.6% | 11.85 | 9.09 | 10.78 |

**Key finding:** The intersection (n=9) drops n from 15 to 9 while also dropping PF (13.21→10.29). Stoch K<60 is the stronger discriminator; adding C43 removes 6 good trades while barely improving average return. The two filters are partially correlated but the intersection is not additive.

Note: C43 baseline here shows n=15 (vs n=16 documented in C43 original results) — likely due to the stochastic requiring 14 bars warmup, which may trim 1 row from the start of data.

**Verdict: No new candidate. Stoch K<60 alone (C52c-b) dominates the intersection.**

---

## C54c: Stoch K<60 × C42 (Skip Q2 — Apr-Jun)

Testing intersection of Stoch K<60 and the seasonal Q2 exclusion.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Skip Q2 (C42) | 24 | 7.22 | +0.236% | 50.0% | 5.34 | 9.12 | 9.14 |
| Stoch K<60 alone | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| Stoch K<60 + skip Q2 | 13 | 11.35 | +0.317% | 61.5% | 9.08 | 11.60 | 17.77 |

**Key finding:** Stoch K<60 + skip Q2 (n=13, PF=11.35) is all-3-years positive and strong, but is outperformed by the simpler Stoch K<60 alone (PF=13.21) and by C53b Stoch K<60 + D1 slope<0 (PF=17.43). Adding the Q2 exclusion removes 2 trades from Stoch K<60 while reducing PF from 13.21 to 11.35. The Q2 exclusion adds no value when Stoch K<60 is already applied.

**Verdict: Below C53b. Stoch K<60 already handles the seasonal edge implicitly — or the overlap is too small to observe improvement. No new candidate from this combination.**

---

## C54d: H1 Close vs EMA50 at Entry

EMA50 measures the 50-bar (50-hour) trend at entry.

Distribution: 7/32 qualifying trades are ABOVE EMA50 at 07:00; 25/32 are BELOW EMA50. The SHORT setup already tends to enter below the medium-term EMA (price faded from highs).

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Above EMA50 at entry | 7 | 4.88 | +0.150% | 42.9% | 2.17 | ~inf* | 8.55 |
| Below EMA50 at entry | 25 | 5.50 | +0.196% | 44.0% | 4.67 | 6.39 | 5.23 |
| Stoch K<60 + below EMA50 | 13 | 11.01 | +0.307% | 61.5% | 9.08 | 11.60 | 15.31 |

*Above EMA50 2025 PF is ~inf due to zero losses (very small n).

**Key finding:** EMA50 split is marginally directional (below=5.50 vs above=4.88) but not strongly discriminating. The 7 above-EMA50 trades have inflated 2025 PF due to near-zero losses (tiny n). Stoch K<60 + below EMA50 (n=13, PF=11.01) is similar to Stoch K<60 + skip Q2 (n=13, PF=11.35) but weaker than C53b (PF=17.43).

**Verdict: EMA50 context adds no independent edge beyond Stoch K<60. The EMA120 slope (already in baseline) captures the same direction at a higher level.**

---

## Summary: C54 All-Rejected

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C54a: MACD hist | Only 2/32 negative; structurally collinear with Asia net-up | PERMANENTLY REJECTED |
| C54b: SK<60 + C43 | Intersection n=9, PF=10.29 — weaker than SK<60 alone | No candidate |
| C54c: SK<60 + C42 | n=13, PF=11.35 — below C53b (17.43) | No candidate |
| C54d: EMA50 | Marginally directional; SK<60+below EMA50 n=13, PF=11.01 | No candidate |

**C54 produces no new pending candidates. C53b (Stoch K<60 + D1 slope<0, n=13, PF=17.43) remains the best combo.**

---

## Updated Pending Candidates Table (all cycles through C54)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **Stoch K<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best combo** |
| C52c-b | Stoch K<60 at entry | 15 | 13.21 | +0.324% | FXOpen 2028 | Implies bar07_bearish |
| C51a | RSI(14)<55 at entry | 22 | 8.97 | +0.268% | FXOpen 2027-28 | = Stoch K<55 (collinear) |
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 | |
| C48b | Bar07 bearish (close<open) | 20 | 10.69 | +0.292% | FXOpen 2027-28 | Superseded by Stoch K<60 |
| C35 | Bear07 (open gap down) | 19 | 10.33 | +0.319% | FXOpen 2027-28 | C48b dependent |
| C37 | ATR expanding (>5d ago) | 17 | 8.52 | +0.252% | FXOpen 2027 | |
| C43 | 0-1 prior Asia up days | 16 | 8.53 | +0.292% | FXOpen 2027-28 | |
| C42 | Skip Q2 (Apr-Jun) | 24 | 7.22 | +0.236% | FXOpen 2027 | |
| C25b+C35 | D1slope + bear07 | 17 | 12.16 | +0.324% | FXOpen 2028 | Superseded by C53b |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 | |
| C51b | C48b + C46c combo | 16 | 12.18 | +0.343% | FXOpen 2028 | |
| C52b | RSI<55 + D1 slope<0 | 17 | 12.26 | +0.325% | FXOpen 2028 | Superseded by C53b |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 | |
| C45b* | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 (borderline) | |
| C46c | ATR ≥ 7pip floor | 28 | 5.92 | +0.209% | FXOpen 2027 | |

---

## Permanently Rejected (C54 scope)

- **C54a (MACD histogram):** Structurally useless — the Asia net-up baseline ensures MACD is positive at entry in 30/32 trades. No discriminating power within the qualifying set.
- **C54b–d combos:** None additive beyond Stoch K<60 alone or C53b.

---

*Past results are not investment advice.*
