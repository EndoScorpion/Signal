# EURUSD Cycle 58 — Asia Peak Hour, Wed/Thu, Prior London, Asia Range
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C58a: Asia Peak Hour (When Did Asia Reach Its High?)

Hypothesis: an Asia high formed early (hours 0-3) gives more consolidation time before London, suggesting "stale" momentum — better SHORT setup. A late peak (hours 4-6) means momentum is still fresh at the London open.

Distribution on 32 qualifying trades: mean=4.5, median=5.0.  
- Hour 1: 3 trades, Hour 2: 2, Hour 3: 4, Hour 4: 4, Hour 5: 4, Hour 6: 15

**15/32 trades peaked at hour 6 — the final Asia bar before London.**

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Asia peak early (hrs 0-3) | 9 | 3.51 | +0.130% | 33.3% | 0.00 | 5.70 | 3.19 |
| Asia peak late (hrs 4-6) | 23 | 6.36 | +0.208% | 47.8% | 4.81 | 8.29 | 8.60 |
| C53b + early peak | 5 | 14.17 | +0.305% | 60.0% | 0.00 | ~inf* | 7.37 |
| C53b + late peak | 8 | 19.60 | +0.404% | 75.0% | 13.98 | 13.48 | ~inf* |
| No gap up + late peak | 19 | 7.76 | +0.250% | 52.6% | 5.41 | 18.36 | 7.08 |

*~inf = zero losses in that year, artifact of tiny n.

**Key finding: Asia peak hour is structurally skewed by our entry condition.** The requirement `asia_net ≥ 0.25×ATR` selects sessions that closed UP from their open — which structurally biases the peak hour toward the end of Asia (hour 6 is the final bar and the close bar, so many sessions "peak at close"). 15/32 trades at hour 6 confirms this endogeneity.

Late peak (n=23, PF=6.36) is marginally better than baseline but offers no discriminating power vs early peak at realistic n. Early peak has 2024 PF=0.00.

**Verdict: REJECTED. Asia peak hour is collinear with the asia_net≥0.25×ATR entry condition. Distribution skewed to hour 6 (the close). No usable filter.**

---

## C58b: Wednesday vs Thursday Breakdown

Testing whether one day within the Wed/Thu pair drives all the performance.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline (Wed+Thu)** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Wednesday only | 18 | 5.57 | +0.194% | 38.9% | 3.09 | 14.83 | 4.78 |
| Thursday only | 14 | 5.13 | +0.176% | 50.0% | 5.56 | 3.90 | 9.55 |
| C53b Wednesday | 9 | 13.18 | +0.392% | 55.6% | 7.70 | 28.86 | 13.23 |
| C53b Thursday | 4 | ~inf | +0.308% | 100.0% | ~inf | ~inf | ~inf |

**Key finding: Both days contribute similarly. Wednesday (PF=5.57) and Thursday (PF=5.13) are nearly identical at the baseline level. The year patterns differ (Wed: strong 2025; Thu: strong 2024/2026) but neither consistently dominates.**

C53b Thu (n=4) has PF=~inf and 100% win rate — 4 trades, all profitable, all-year ~inf. Zero useful information.

**Verdict: NOT A CANDIDATE. No meaningful day-level split. Both Wednesday and Thursday contribute to the edge; excluding either reduces n without reliable PF improvement. The combined Wed/Thu filter remains correct.**

---

## C58c: Prior London Session Direction

Hypothesis: when the prior day's London session (07:00-21:00) was bearish, it confirms the SHORT trend context.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Prior London bearish | 28 | 4.95 | +0.167% | 42.9% | 5.37 | 4.37 | 5.25 |
| Prior London bullish | 4 | 8.23 | +0.319% | 50.0% | 0.00 | ~inf | ~inf |
| C53b + prior bear | 11 | 21.58 | +0.330% | 72.7% | 25.92 | 13.48 | 25.71 |
| No gap up + prior bear | 23 | 7.46 | +0.220% | 52.2% | 6.11 | 10.60 | 7.16 |

**Critical finding: 28/32 qualifying trades (87.5%) had a bearish prior London session.** This is a near-total structural correlation with the EMA120<0 trend filter — when the hourly trend is bearish, the prior London session was also almost always bearish. The "prior London bearish" condition is de facto a near-constant on the qualifying set; it barely filters at all.

The prior-bullish group (n=4) has 2024 PF=0.00 and ~inf in other years — statistically void.

**Verdict: REJECTED. Prior London direction is structurally redundant with EMA120<0. 28/32 qualifying trades already have a bearish prior London session. No discriminating power.**

---

## C58d: Asia Range Width vs ATR

Hypothesis: a wider Asia range represents stronger overnight conviction, improving the SHORT setup.

Distribution on 32 qualifying trades: mean=2.225×ATR, median=2.100×ATR.  
- All 32 trades have Asia range ≥ 1.2×ATR. Zero trades below 0.8×ATR.

**All 32 qualifying trades have very wide Asia ranges (mean=2.2×ATR).** This mirrors C56b (bar07 range always >0.8×ATR) — the London open and the Asia session are both periods of high volatility in EUR/USD. The Asia net requirement (≥0.25×ATR) does not filter for wide ranges specifically, but the qualifying trades naturally cluster at 2×ATR anyway.

**Verdict: PERMANENTLY REJECTED. Zero variation — all trades have Asia range ≥ 1.2×ATR. Cannot discriminate within the qualifying set. Same fundamental finding as C56b for the bar07 range.**

---

## Summary: C58 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C58a: Asia peak hour | Skewed to hour 6 (close); collinear with asia_net≥0.25×ATR | REJECTED |
| C58b: Wed vs Thu | Both ~PF=5.5; C53b Thu n=4 (all wins = meaningless) | Not a candidate |
| C58c: Prior London | 28/32 bearish prior London; redundant with EMA120<0 | REJECTED |
| C58d: Asia range width | All 32 trades ≥1.2×ATR; zero variation | PERMANENTLY REJECTED |

**No new candidates in C58. All four tests revealed structural collinearity with existing baseline conditions.**

---

## Updated Pending Candidates Table (all cycles through C58)

No changes to the C57 table. C57a (baseline + no gap up, n=25, PF=7.90) remains the newest candidate.

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **Stoch K<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best combo** |
| **C56c** | **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | **Gap-up exclusion, SK<60** |
| **C57a** | **Baseline + no gap up** | **25** | **7.90** | **+0.248%** | **FXOpen 2027** | **Standalone gap exclusion** |
| C52c-b | Stoch K<60 at entry | 15 | 13.21 | +0.324% | FXOpen 2028 | |
| C51a | RSI(14)<55 at entry | 22 | 8.97 | +0.268% | FXOpen 2027-28 | |
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 | |
| C48b | Bar07 bearish (close<open) | 20 | 10.69 | +0.292% | FXOpen 2027-28 | Superseded by Stoch K<60 |
| C35 | Bear07 (open gap down) | 19 | 10.33 | +0.319% | FXOpen 2027-28 | |
| C37 | ATR expanding (>5d ago) | 17 | 8.52 | +0.252% | FXOpen 2027 | |
| C43 | 0-1 prior Asia up days | 16 | 8.53 | +0.292% | FXOpen 2027-28 | |
| C42 | Skip Q2 (Apr-Jun) | 24 | 7.22 | +0.236% | FXOpen 2027 | |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 | |
| C51b | C48b + C46c combo | 16 | 12.18 | +0.343% | FXOpen 2028 | |
| C52b | RSI<55 + D1 slope<0 | 17 | 12.26 | +0.325% | FXOpen 2028 | Superseded by C53b |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 | |
| C45b* | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 (borderline) | |
| C46c | ATR ≥ 7pip floor | 28 | 5.92 | +0.209% | FXOpen 2027 | |

---

## Permanently Rejected (C58 scope)

- **C58a (Asia peak hour):** Collinear with entry condition. Hour 6 concentration artifact of asia_net>0 filter.
- **C58c (prior London direction):** 28/32 qualifying trades have bearish prior London — near-constant, redundant with EMA120<0.
- **C58d (Asia range width):** All 32 qualifying trades have Asia range ≥1.2×ATR. Zero variation possible.

---

*Past results are not investment advice.*
