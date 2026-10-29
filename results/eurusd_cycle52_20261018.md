# EURUSD Cycle 52 — RSI Combos + Stochastic at Entry
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C52a: RSI<55 × C48b (bar07_bearish)

Testing the two strongest standalone signals from C48b and C51a.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| RSI<55 (C51a) | 22 | 8.97 | +0.268% | 54.5% | 6.81 | 10.07 | 11.15 |
| bar07_bearish (C48b) | 19 | 10.33 | +0.296% | 57.9% | 6.84 | 13.40 | 10.82 |
| RSI<55 + bar07_bearish | 18 | **11.80** | **+0.317%** | **61.1%** | **6.84** | **13.40** | **25.71** |
| RSI>=55 + bar07_bearish | 1 | 0.00 | -0.075% | 0.0% | — | — | 0.00 |

**Critical structural finding:** 18 of 19 bar07_bearish trades ALSO have RSI<55 — the two signals are 94.7% correlated. When a bar closes bearish (bar07_bearish), RSI is almost always already below 55. The combo adds only 1 trade of discrimination over bar07_bearish alone (removes the one RSI>=55 case, which was a loser). The two signals are largely **collinear** — they measure the same underlying condition from different angles.

The combo (n=18, PF=11.80, 2026 PF=25.71) is excellent but adds little over C48b alone (n=19). RSI<55 is the more fundamental description of the same phenomenon.

**Verdict:** n=18, confirmed strong but no independent contribution beyond C48b. Both signals are pending candidates for the same future re-test window.

---

## C52b: RSI<55 × C25b (D1 EMA slope<0)

RSI<55 combined with the daily EMA trend filter.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| D1 slope<0 (C25b) | 24 | 7.15 | +0.231% | 45.8% | 4.03 | 22.76 | 5.25 |
| RSI<55 (C51a) | 22 | 8.97 | +0.268% | 54.5% | 6.81 | 10.07 | 11.15 |
| RSI<55 + D1 slope<0 | 17 | **12.26** | **+0.325%** | **58.8%** | **6.84** | **22.76** | **11.15** |
| RSI>=55 + D1 slope<0 | 7 | 1.07 | +0.004% | 14.3% | 1.64 | — | 0.00 |

**Key finding:** The combo (n=17) preserves all 3 years strongly: 2024 PF=6.84, 2025 PF=22.76, 2026 PF=11.15. The RSI and D1 slope conditions are more independent than RSI + bar07_bearish — 17/22 RSI<55 trades also have D1 slope<0 (77% overlap vs 94% for bar07_bearish).

The 7 RSI>=55 trades with D1 slope<0 show catastrophic performance (PF=1.07, 2026 PF=0.00) — confirming RSI<55 is the key discriminator that D1 slope alone doesn't capture.

**Note on 2025 anomaly:** 2025 PF=22.76 is suspiciously high. This is the same figure as D1 slope<0 alone — the RSI filter doesn't reduce the 2025 PF, suggesting RSI<55 and D1 slope<0 overlap perfectly in 2025 (all 2025 qualifying trades with D1 slope<0 also had RSI<55).

**Verdict:** Strong combo. n=17, pending FXOpen 2028.

---

## C52c: Stochastic(14,3) K at 07:00 Entry

Stoch K measures where the close sits within the 14-bar high-low range. Given the Asia rally, Stoch K is expected to be elevated. Distribution: mean=57.0, median=60.7, with 13/32 trades at K>=70.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Stoch K<50 | 12 | 21.14* | +0.394% | 75.0% | 9.08 | 32.51 | ~inf† |
| **Stoch K<55** | **14** | **18.19** | **+0.355%** | **71.4%** | **9.08** | **37.55** | **25.71** |
| Stoch K<60 | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| Stoch K>=50 | 20 | 2.09 | +0.061% | 25.0% | 1.87 | 3.19 | 0.80 |

†Stoch K<50, 2026: zero losses in sample (1-2 trades), inflating PF to ~141M. Unreliable.
*Stoch K<50 PF=21.14 partly inflated by 2026 zero-loss anomaly.

**Stoch K<55 is the strongest discriminator found in this entire study.**
- PF=18.19 (vs baseline 5.38 — 3.4× improvement)
- All 3 years strongly positive: 2024 PF=9.08, 2025 PF=37.55, 2026 PF=25.71
- Win rate = 71.4% (vs 43.8% baseline)
- avg = +0.355% (vs +0.186% baseline)

Note on 2025: PF=37.55 is extremely high, suggesting few or zero losses in 2025 from 14 trades. This needs careful interpretation — with n=14, a run of 4-5 wins easily drives the annual PF very high.

**Stoch K<60 provides a slightly more conservative threshold:**
- n=15, PF=13.21, all 3 years strongly positive: 9.08 / 13.40 / 25.71
- This threshold is more robust: 2025 PF=13.40 (same as bar07_bearish group) without the extreme inflation

**RSI vs Stochastic correlation:**
RSI<55 AND Stoch K<55 gives n=14 — identical to Stoch K<55 alone. This means Stoch K<55 already implies RSI<55 in this dataset. The two measures are collinear at the <55 threshold — Stoch K<55 is the stronger condition that encompasses RSI<55.

**Economic interpretation:** Stoch K measures where the current close sits within the 14-bar range. The Asia rally already happened (asia_net≥0.25×ATR baseline requirement). But if Stoch K is still <55 after that rally, it means:
- The recent 14-bar range is large (ATR high period), OR
- The close is still in the lower half of recent range despite the overnight up-move
- Either way, EUR has NOT broken into overbought Stochastic territory despite the rally — the underlying downtrend (EMA120<0) is absorbing the counter-move, and the 07:00 entry captures the start of the reversal back.

**Verdict:** Stoch K<55 is the strongest single-bar momentum filter found. n=14, which is very small; 2025 PF likely inflated by lucky streak. Pending: re-test FXOpen 2028 when n→~20+. Stoch K<60 (n=15) is the more conservative and reliable threshold to watch.

---

## Summary

| Test | Key Finding | n | PF | All years? |
|------|-------------|---|----|------------|
| C52a: RSI+bar07b | Collinear (94% overlap); combo n=18, PF=11.80 | 18 | 11.80 | Yes (6.84/13.40/25.71) |
| C52b: RSI+D1 | Independent combo: n=17, PF=12.26 | 17 | 12.26 | Yes (6.84/22.76/11.15) |
| **C52c: Stoch K<55** | **Strongest single filter ever found** | **14** | **18.19** | **Yes (9.08/37.55/25.71)** |
| C52c: Stoch K<60 | Conservative threshold, more robust | 15 | 13.21 | Yes (9.08/13.40/25.71) |

**The RSI and Stochastic story is now clear:** These momentum indicators are collinear at low thresholds. The common signal they capture: "the Asia rally did NOT push EUR into technical overbought territory" — and this is the key predictor of a successful London-session fade. When EUR IS technically overbought (high Stoch K, high RSI), the fade fails badly.

---

## Updated Pending Candidates Table (all cycles through C52)

| ID | Filter | n | PF | avg% | Re-test when |
|----|--------|---|----|------|--------------|
| **C52c** | **Stoch K<55 at entry** | **14** | **18.19** | **+0.355%** | **FXOpen 2028** |
| **C52c-b** | **Stoch K<60 at entry** | **15** | **13.21** | **+0.324%** | **FXOpen 2028** |
| C51a | RSI(14)<55 at entry | 22 | 8.97 | +0.268% | FXOpen 2027-28 |
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 |
| C48b | Bar07 bearish (close<open) | 20 | 10.69 | +0.292% | FXOpen 2027-28 |
| C35 | Bear07 (open gap down) | 19 | 10.33 | +0.319% | FXOpen 2027-28 |
| C37 | ATR expanding (>5d ago) | 17 | 8.52 | +0.252% | FXOpen 2027 |
| C43 | 0-1 prior Asia up days | 16 | 8.53 | +0.292% | FXOpen 2027-28 |
| C42 | Skip Q2 (Apr-Jun) | 24 | 7.22 | +0.236% | FXOpen 2027 |
| C25b+C35 | D1slope + bear07 | 17 | 12.16 | +0.324% | FXOpen 2028 |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 |
| C51b | C48b + C46c combo | 16 | 12.18 | +0.343% | FXOpen 2028 |
| C52b | RSI<55 + D1 slope<0 | 17 | 12.26 | +0.325% | FXOpen 2028 |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 |
| C45b* | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 (borderline) |
| C46c | ATR ≥ 7pip floor | 28 | 5.92 | +0.209% | FXOpen 2027 |
| C51c* | Extension <0.1×ATR | 26 | 6.85 | +0.233% | FXOpen 2027 (needs more data) |

---

*Past results are not investment advice.*
