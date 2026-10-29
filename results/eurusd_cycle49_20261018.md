# EURUSD Cycle 49 — 08:00 Entry Test, Bar07 Combos, C35 vs C48b Overlap
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C49a: 08:00 Entry After Confirming Bar07 Bearish

C48b found that qualifying trades where the 07:00 bar closes bearish have PF=10.69. But the 07:00 bar's close is only known at 08:00. Testing whether waiting for the 08:00 open (after observing 07:00 bearish close) preserves the edge.

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline (07:00)** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Bar07 bearish, 07:00 entry | 19 | 10.33 | +0.296% | 57.9% | 6.84 | 13.40 | 10.82 |
| **Bar07 bearish, 08:00 entry** | **19** | **5.17** | **+0.209%** | **36.8%** | **4.14** | **6.00** | **4.83** |

**Key finding:** Waiting for 08:00 entry DESTROYS the edge. PF drops from 10.33→5.17 (worse than baseline 5.38 on a per-trade basis), win rate drops from 57.9%→36.8%. The fade works precisely because price is extended at the 07:00 open — waiting one hour gives back most of the move. **The C48b filter is not practically implementable as a late entry.** However, it remains valid as a selection filter applied at 07:00 — using the 07:00 bar's direction as a real-time confirmation is only possible with a bar that closes at 07:59 (H1 bar), so this is known at 08:00 and cannot be used at 07:00 entry.

**Resolution:** C48b (bar07_bearish) is a **retroactive classifier** — it describes which 07:00 trades succeeded, not a signal you can act on at 07:00 open. The entry must stay at 07:00. C48b's value is in understanding what makes trades work, not as a timing filter. However, it does suggest that having a real-time signal for "the 07:00 bar is closing down" (via a faster instrument or price alert) could help in live trading at the 07:59 close.

**Verdict for live trading:** Enter at 07:00 as now. C48b is a post-hoc performance descriptor, not a new entry rule.

---

## C49b: Bar07_Bearish Combos with Top Candidates

| Combo | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| D1slope + bar07_bearish | 17 | 12.16 | +0.324% | 58.8% | 6.84 | 22.76 | 10.82 |
| SkipQ2 + bar07_bearish | 16 | 10.05 | +0.309% | 56.2% | 9.08 | 12.14 | 7.48 |
| ATR_exp + bar07_bearish | 11 | 17.82 | +0.381% | 72.7% | 9.08 | ~inf | 7.83 |
| 0-1consec + bar07_bearish | 13 | 8.19 | +0.300% | 46.2% | 7.87 | 10.37 | 4.54 |

**Notes:**
- D1slope + bar07_bearish (n=17, PF=12.16): Same PF as D1+bear07 from C44b — highly likely overlapping sets
- ATR_exp + bar07_bearish (n=11): 2025 has zero losses (PF=inf inflated) — statistically unreliable
- SkipQ2 + bar07_bearish (n=16, PF=10.05): All 3 years positive; the cleanest combo here

**None of these combos has n≥30.** All are pending at the n<30 threshold. They confirm that bar07_bearish stacks well with other filters but we need more data.

---

## C49c: Overlap Between C35 (Bear07) and C48b (Bar07_Bearish Candle)

C35 = `open07 < prev_close` (07:00 open is below prior bar's close — opening gap down)  
C48b = `close07 < open07` (07:00 bar closes lower than it opened — intrabar fade)

These measure different things: C35 is about the gap at bar open, C48b is about bar direction.

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Both C35 + C48b | 8 | 12.23 | +0.398% | 62.5% | 7.70 | 18.03 | ~inf |
| C48b only (not C35) | 11 | 8.65 | +0.223% | 54.5% | 4.21 | 9.59 | 9.63 |
| C35 only (not C48b) | 5 | 1.54 | +0.029% | 20.0% | 2.05 | — | 0.00 |
| Neither | 8 | 1.35 | +0.022% | 25.0% | 2.24 | 0.00 | 3.01 |

**Critical finding:**
1. **C35 without C48b confirmation (n=5) is nearly worthless:** PF=1.54, win=20%, 2026 PF=0.00. The C35 (bear07 open gap) signal is largely only good WHEN it coincides with the bar also closing lower.
2. **C48b alone (n=11) is excellent:** PF=8.65, all 3 years positive and consistent.
3. **Trades where NEITHER signal fires (n=8)** show PF=1.35, confirming these are the worst trades.

**Implication:** C48b (bar07 bearish candle) is a STRONGER discriminator than C35 (bear07 open gap), and the two signals are largely additive. The 19 trades with bar07_bearish (8 both + 11 C48b-only) are the best group; the 5 C35-only trades are barely above breakeven.

**Revised view of C35:** C35's PF=10.33 (pending candidate) may be driven primarily by the 8 trades that also satisfy C48b (both). The 5 C35-only trades have PF=1.54 — near worthless. This suggests C35 as a standalone filter is overstated, and C48b is the better underlying signal.

**Updated interpretation:** For a live rule, **bar07_bearish** (C48b) is the more fundamental signal. C35 adds nothing beyond what C48b captures and may be noise.

---

## Summary of C48b vs C35 Reanalysis

| Signal | n | PF | Notes |
|--------|---|----|-------|
| C35 (open gap) | 19 | 10.33 | Overstated — driven by 8 both-signal trades |
| C48b (candle) | 20 | 10.69 | Stronger — C48b-only 11 trades remain excellent |
| Both together | 8 | 12.23 | Best but n=8 (inflated by zero losses in 2026) |

---

## Updated Pending Candidates Table (all cycles through C49)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 | |
| **C48b** | **Bar07 bearish (close<open)** | **20** | **10.69** | **+0.292%** | **FXOpen 2027-28** | **Stronger than C35** |
| C35 | Bear07 (open gap down) | 19 | 10.33 | +0.319% | FXOpen 2027-28 | Driven by C48b overlap |
| C37 | ATR expanding (>5d ago) | 17 | 8.52 | +0.252% | FXOpen 2027 | |
| C43 | 0-1 prior Asia up days | 16 | 8.53 | +0.292% | FXOpen 2027-28 | |
| C42 | Skip Q2 (Apr-Jun) | 24 | 7.22 | +0.236% | FXOpen 2027 | |
| C25b+C35 | D1slope + bear07 | 17 | 12.16 | +0.324% | FXOpen 2028 | Likely = D1+C48b |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 | |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 | |
| C45b* | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 (borderline) | |
| C46c | ATR ≥ 7pip floor | 28 | 5.92 | +0.209% | FXOpen 2027 | |

---

## Permanently Rejected (C49 scope)

- **C49a (08:00 delayed entry):** Waiting for 08:00 destroys the edge — PF drops from 10.33→5.17; entry must stay at 07:00
- **C35 standalone re-evaluation:** C35 without C48b confirmation shows PF=1.54 (n=5). C35's apparent strength is driven by trades that also satisfy C48b. C35 is not independently rejected but its standalone value is lower than previously thought.

---

*Past results are not investment advice.*
