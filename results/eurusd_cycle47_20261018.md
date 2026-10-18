# EURUSD Cycle 47 — Prior Week Direction + Non-Q2 Seasonal Breakdown
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C47a: Prior Week Direction

Prior week return: mean=−0.00079, 59.4% of qualifying trades follow a bearish prior week.

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Prior week bearish (EUR fell) | 19 | 4.63 | +0.158% | 36.8% | 4.19 | 7.02 | 3.63 |
| Prior week bullish (EUR rose) | 12 | 7.69 | +0.252% | 58.3% | 4.91 | 7.09 | ~inf |

**Note on 2026 PF=65M for bullish:** This reflects zero losses in a small 2026 sample — only a few trades, all winners. Statistically unreliable.

### Prior week return magnitude tiers:

| Prior week bucket | n | PF | avg% | 2024 PF | 2025 PF | 2026 PF |
|------------------|---|----|------|---------|---------|---------|
| Big bear week (>50 pip down) | 15 | 4.50 | +0.148% | 8.48 | 1.68 | 3.63 |
| Small bear | 4 | 5.06 | +0.194% | 0.00 | ~inf | — |
| Flat week | 0 | — | — | — | — | — |
| Small bull | 3 | inf | +0.365% | ~inf | — | ~inf |
| Big bull week (>50 pip up) | 9 | 5.27 | +0.214% | 2.37 | 7.09 | — |

**Key finding:** Prior week direction looks interesting on the surface (bullish prior week → PF=7.69) but the n=12 sample and 2026 having zero losses make this unreliable. The 2024 PF=4.91 is positive but modest. More importantly, the "small bull" and "small bear" buckets each have n≤4, producing inf/0 statistics from near-zero denominators.

**Structural check:** 59.4% of trades follow a bearish prior week. While not as extreme as the 87.5% base rate problems encountered in C44a/C45c, the split is uneven enough (19/12) that the bullish subgroup is very small. With only 12 trades in the bullish group, any signal here needs much more data.

**Verdict:** **Permanently rejected** — bullish prior week n=12 is far below n≥30, with 2026 PF inflated by zero losses. Year-inconsistency in tier buckets (big bear week: 2025 PF=1.68). No stable directional edge from prior week return.

---

## C47b: Non-Q2 Seasonal Breakdown (Q1 vs Q3 vs Q4)

Q2 (Apr-Jun) identified as weak in C42. This tests the remaining quarters.

| Quarter | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|---------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Q1 Jan-Mar | 13 | 5.71 | +0.166% | 53.8% | 1.12 | 6.28 | 21.71 |
| Q2 Apr-Jun (weak) | 8 | 1.65 | +0.036% | 25.0% | 0.00 | 2.22 | 3.15 |
| Q3 Jul-Sep | 6 | 5.98 | +0.229% | 33.3% | 3.22 | 17.14 | 0.00 |
| Q4 Oct-Dec | 5 | 13.21 | +0.424% | 60.0% | 15.77 | 8.43 | — |

**Q4 observation:** Only 5 trades but PF=13.21, avg=+0.424%, all available years strongly positive (2026 has no Q4 trades yet — data ends Oct 16). Interesting but n=5 is far too small.

**Q3 concern:** 2026 PF=0.00 — zero wins in Q3 2026. Small sample but notable.

### Skip Q2 + worst non-Q2 quarter:

Worst quarter among Q1/Q3/Q4 = Q1 (PF=5.71, 2024 PF=1.12)

| Combo | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| Skip Q2 only (C42 baseline) | 24 | 7.22 | +0.236% | 50.0% | 5.34 | 9.12 | 9.14 |
| Skip Q2 + Q1 | 11 | 8.77 | +0.318% | 45.5% | 9.10 | 13.17 | 0.00 |

**Key finding:** Skipping both Q2 and Q1 boosts PF to 8.77 and avg to +0.318%, but 2026 PF=0.00 (zero wins in just 2 remaining Q3/Q4 trades in 2026). This means the combination may be overfitting to specific quarters in 2024/2025.

**The better skip:** C42 (Skip Q2 only) with n=24, PF=7.22, ALL THREE YEARS improving, remains the superior seasonal filter. Adding Q1 exclusion helps 2024/2025 but kills 2026 at the small sample level.

**Verdict:** Q4 timing is intriguing but n=5 is useless. Skipping Q1 in addition to Q2 is **rejected** — 2026 PF=0.00 is a red flag and n=11 is far too small. **No new pending candidates from C47b.** The C42 (skip Q2) filter remains the best seasonal finding.

---

## Summary: C47 Findings

Both C47a and C47b fail to produce new pending candidates:
- **C47a:** Prior week direction — n too small (12/19), 2026 inflated by zero losses, no stable signal
- **C47b:** Additional quarter exclusions — further reduces n below useful threshold, 2026 inconsistency

**The seasonal story remains:** Skip Q2 (C42) is the only seasonal filter worth retaining. Quarter-level granularity within non-Q2 is insufficient sample.

---

## Updated Pending Candidates Table (all cycles through C47)

| ID | Filter | n | PF | avg% | Re-test when |
|----|--------|---|----|------|--------------|
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 |
| C35 | Bear07 at 07:00 entry | 19 | 10.33 | +0.319% | FXOpen 2027-28 |
| C37 | ATR expanding (>5d ago) | 17 | 8.52 | +0.252% | FXOpen 2027 |
| C43 | 0-1 prior Asia up days | 16 | 8.53 | +0.292% | FXOpen 2027-28 |
| C42 | Skip Q2 (Apr-Jun) | 24 | 7.22 | +0.236% | FXOpen 2027 |
| C25b+C35 | D1slope + bear07 | 17 | 12.16 | +0.324% | FXOpen 2028 |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 |
| C45b* | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 (borderline) |
| C46c | ATR ≥ 7pip floor | 28 | 5.92 | +0.209% | FXOpen 2027 |

---

## Permanently Rejected (C47 scope)

- **C47a (prior week direction):** n=12 in bullish group; 2026 PF inflated (zero losses); no stable year-consistent edge
- **C47b (skip additional quarters):** Skip Q2+Q1 reduces n to 11, 2026 PF=0.00; over-fitting concern; C42 remains superior

---

*Past results are not investment advice.*
