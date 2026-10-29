# EURUSD Cycle 50 — Wednesday vs Thursday, Profit Target, Exit Time
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C50a: Wednesday vs Thursday

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Wednesday | 18 | 5.57 | +0.194% | 38.9% | 3.09 | 14.83 | 4.78 |
| Thursday | 14 | 5.13 | +0.176% | 50.0% | 5.56 | 3.90 | 9.55 |

**Key finding:** Nearly identical PF (5.57 vs 5.13) but years invert — Wednesday dominates 2025, Thursday dominates 2024/2026. There is no consistent day-of-week superiority within the Wed/Thu window. Both are needed for sample size. **Permanently rejected** — no consistent within-window day distinction.

---

## C50b: Fixed Profit Target (Take Profit at N×ATR)

Adding a profit target means the trade exits early if price moves down by N×ATR before 21:00.

| Configuration | n | PF | avg% | win% | Stop% | Target% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|-------|---------|---------|---------|---------|
| **No target (baseline)** | **32** | **5.38** | **+0.186%** | **43.8%** | **56.2%** | **0%** | **3.86** | **7.06** | **6.05** |
| Target 0.5×ATR | 32 | 1.01 | +0.000% | 68.8% | 31.2% | 68.8% | 0.59 | 1.51 | 1.42 |
| Target 0.8×ATR | 32 | 1.76 | +0.018% | 68.8% | 31.2% | 68.8% | 1.03 | 2.59 | 2.52 |
| Target 1.0×ATR | 32 | 2.04 | +0.026% | 65.6% | 34.4% | 65.6% | 1.33 | 3.31 | 2.08 |
| Target 1.5×ATR | 32 | 2.59 | +0.046% | 62.5% | 37.5% | 62.5% | 2.06 | 2.85 | 3.25 |
| Target 2.0×ATR | 32 | 2.89 | +0.061% | 56.2% | 43.8% | 56.2% | 1.69 | 3.86 | 4.41 |

**Key finding:** Every profit target degrades performance. Adding a 0.5×ATR target nearly destroys the strategy (PF=1.01). Even a 2.0×ATR target cuts PF from 5.38 to 2.89.

The stop rate of 56.2% shows most losing trades are stopped out hard. Win rate with target goes up (68.8%) but profit factor collapses because the target caps winners while losers still stop out at 0.80×ATR. The risk:reward with a target becomes unfavorable — risking 0.80×ATR to earn 0.5-2.0×ATR doesn't work here.

**Implication:** The trade's PnL distribution is asymmetric the other way — winners tend to be large (continue moving all day), losers are stopped quickly. The hold-to-21:00 approach correctly captures this. **Confirmed: no profit target. 21:00 exit optimal.**

---

## C50c: Earlier Exit Time

| Exit time | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-----------|---|----|------|------|---------|---------|---------|
| Exit 15:00 | 32 | 3.23 | +0.090% | 43.8% | 1.15 | 5.10 | 6.43 |
| Exit 17:00 | 32 | 3.66 | +0.113% | 43.8% | 1.49 | 5.75 | 5.19 |
| Exit 19:00 | 32 | 4.55 | +0.151% | 43.8% | 2.23 | 7.07 | 5.71 |
| **Exit 21:00 (baseline)** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |

**Key finding:** Win rate is identical across all exit times (43.8%) — confirming that wins and losses are decided within the stop range (8:00-20:00), not by early exit timing. But avg profit per trade increases monotonically with later exit. Earlier exit times cut avg from +0.186% down to +0.090% at 15:00.

The 2024 degradation is most severe with early exit (PF=1.15 at 15:00 vs 3.86 at 21:00). The fade continues through the European session and into US pre-close — cutting the trade short misses the bulk of the move. **Confirmed: 21:00 exit is optimal. No change.**

---

## Summary

All three C50 tests confirm the current v2.3 parameters:
- **Wed vs Thu:** Neither is consistently better; both are needed
- **Profit target:** Never helps — the trade needs to hold until 21:00
- **Exit time:** 21:00 is monotonically best; earlier exits reduce returns

---

## Updated Pending Candidates Table (all cycles through C50)

No new candidates. Table unchanged from C49.

| ID | Filter | n | PF | avg% | Re-test when |
|----|--------|---|----|------|--------------|
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 |
| C48b | Bar07 bearish (close<open) | 20 | 10.69 | +0.292% | FXOpen 2027-28 |
| C35 | Bear07 (open gap down) | 19 | 10.33 | +0.319% | FXOpen 2027-28 |
| C37 | ATR expanding (>5d ago) | 17 | 8.52 | +0.252% | FXOpen 2027 |
| C43 | 0-1 prior Asia up days | 16 | 8.53 | +0.292% | FXOpen 2027-28 |
| C42 | Skip Q2 (Apr-Jun) | 24 | 7.22 | +0.236% | FXOpen 2027 |
| C25b+C35 | D1slope + bear07 | 17 | 12.16 | +0.324% | FXOpen 2028 |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 |
| C45b* | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 (borderline) |
| C46c | ATR ≥ 7pip floor | 28 | 5.92 | +0.209% | FXOpen 2027 |

---

## Permanently Rejected (C50 scope)

- **C50a (Wed vs Thu distinction):** Year-inconsistent; both days needed for sample size
- **C50b (profit target):** All targets degrade PF from 5.38 down to 1.01-2.89; no target confirmed optimal
- **C50c (earlier exit):** 21:00 exit monotonically best; earlier exits reduce avg per trade

---

*Past results are not investment advice.*
