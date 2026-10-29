# EURUSD Cycle 53 — Stochastic Combos + Williams %R
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C53a: Stoch K<60 × C48b (bar07_bearish) — Structural Finding

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Stoch K<60 | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| bar07_bearish (C48b) | 19 | 10.33 | +0.296% | 57.9% | 6.84 | 13.40 | 10.82 |
| Stoch K<60 + bar07_bearish | 15 | 13.21 | — identical — | — | — | — | — |
| Stoch K<60, bar07_bullish | 0 | — | — | — | — | — | — |
| Stoch K>=60 + bar07_bearish | 4 | 4.72 | +0.191% | 25.0% | 0.00 | 13.40 | 0.00 |

**Critical structural finding: Stoch K<60 fully implies bar07_bearish.**

All 15 Stoch K<60 qualifying trades also satisfy bar07_bearish. Zero Stoch K<60 trades have a bullish 07:00 candle. This is a mathematical/structural result:
- Stoch K<60 means `close < low14 + 0.60×(high14-low14)` — the close is in the lower 60% of the 14-bar range
- When the close is that low within the 14-bar range, and the entry bar opened ABOVE the Asia net-up threshold (so the bar opened high), the close being in the bottom 60% of range means it MUST have faded during the bar — i.e., bar07_bearish is almost guaranteed

The 4 bar07_bearish trades with Stoch K>=60 show year-inconsistent results (2024 PF=0.00, 2026 PF=0.00). These are bar07_bearish trades where close is in the upper 40% of range — the bearish candle was marginal.

**Implication:** Stoch K<60 is a STRICTER, higher-quality version of bar07_bearish. Any pending candidate based on bar07_bearish should be superseded by Stoch K<60 — it selects a cleaner subset of the same trades with a stronger discriminating condition.

---

## C53b: Stoch K<60 × C25b (D1 slope<0)

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Stoch K<60 | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| D1 slope<0 (C25b) | 24 | 7.15 | +0.231% | 45.8% | 4.03 | 22.76 | 5.25 |
| **Stoch K<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **69.2%** | **9.08** | **33.90** | **25.71** |
| Stoch K>=60 + D1 slope<0 | 11 | 2.30 | +0.072% | 18.2% | 1.35 | 13.40 | 0.00 |

**Key finding:** Stoch K<60 + D1 slope<0 (n=13, PF=17.43) is extremely strong. All 3 years positive: 2024 PF=9.08, 2025 PF=33.90, 2026 PF=25.71. The combo removes 2 trades from Stoch K<60 (n=15→13) while improving PF substantially (13.21→17.43).

The 11 Stoch K>=60 trades with D1 slope<0 show PF=2.30, 2026 PF=0.00 — confirming Stoch K is the key real-time discriminator and D1 slope adds an independent layer.

**Note on 2025:** PF=33.90 is very high — suggests near-zero losses in 2025 from 13 trades. This is a statistical artifact of small n (a run of 5-6 wins drives annual PF very high). Year-by-year consistency (not PF magnitude) is the more reliable signal: all 3 years are positive, which is the key criterion.

**Verdict:** n=13, strong pending candidate. Re-test FXOpen 2028 (n→~19-20).

---

## C53c: Williams %R(14) — Mathematical Equivalence to Stochastic K

Williams %R(14) formula: `WR = -100 × (H14 - Close) / (H14 - L14)`

This is mathematically identical to `Stoch K - 100`. Every WR threshold is exactly equivalent to a Stoch K threshold:
- WR < -40 ≡ Stoch K < 60 (verified: both give exactly n=15, 100% overlap)
- WR < -50 ≡ Stoch K < 50
- WR < -45 ≡ Stoch K < 55

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| WR<-40 ≡ Stoch K<60 | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| WR>=-40 ≡ Stoch K>=60 | 17 | 2.12 | +0.063% | 23.5% | 1.87 | 3.34 | 1.01 |

**Williams %R adds no information beyond Stochastic K.** They are the same indicator with a sign flip and 100-unit offset. All further analysis uses Stoch K.

---

## Summary: The Stochastic Hierarchy

C52 and C53 together reveal a clean hierarchy:

| Stoch K threshold | n | PF | Economic interpretation |
|-------------------|---|----|------------------------|
| K<50 | 12 | 21.14* | Close in bottom half of 14-bar range |
| K<55 | 14 | 18.19 | = RSI<55 (collinear at this threshold) |
| **K<60** | **15** | **13.21** | **= bar07_bearish (implies it 100%)** |
| K>=60 | 17 | 2.12 | Failed — overbought at entry |
| K>=70 | 13 | low | Strongly overbought — worst group |

*K<50 inflated by 2026 zero-loss anomaly; K<55 inflated by 2025

The optimal practical threshold is **Stoch K<60** (n=15, PF=13.21):
- Strong enough PF to be meaningful
- Not inflated by zero-loss anomalies in a single year
- All 3 years positive and balanced (9.08 / 13.40 / 25.71)
- Implies bar07_bearish (cleaner structural condition)
- Still needs n≥30 before adoption

**Combined with D1 slope<0 (C53b): n=13, PF=17.43** — the strongest confirmed two-filter combo.

---

## Updated Pending Candidates Table (all cycles through C53)

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

## Permanently Rejected (C53 scope)

- **C53c (Williams %R):** Mathematically identical to Stochastic K (WR = Stoch K - 100). No independent signal.

---

*Past results are not investment advice.*
