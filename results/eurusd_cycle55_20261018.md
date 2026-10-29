# EURUSD Cycle 55 — Stoch K<55 Combos, Asia Quality, Bar07 Position
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C55a: Stoch K<55 + D1 Slope<0 (Analogous to C53b)

Testing whether K<55 threshold + D1 slope produces a different set than K<60 + D1 slope (C53b).

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Stoch K<55 alone | 14 | 18.19 | +0.355% | 71.4% | 9.08 | 37.55 | 25.71 |
| Stoch K<60 alone | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| D1 slope<0 (C25b) | 24 | 7.15 | +0.231% | 45.8% | 4.03 | 22.76 | 5.25 |
| **Stoch K<55 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **69.2%** | **9.08** | **33.90** | **25.71** |
| Stoch K<60 + D1 slope<0 (C53b) | 13 | 17.43 | +0.366% | 69.2% | 9.08 | 33.90 | 25.71 |

**Critical finding: Stoch K<55 + D1slope<0 and Stoch K<60 + D1slope<0 are IDENTICAL.** Both produce n=13 with identical PF=17.43 and identical year-by-year results. The 14th K<55 trade (the one extra vs K<60) does not have D1 slope<0, so the intersection is the same 13 trades.

This confirms the hierarchy: **C53b is the canonical best combo**, equivalent at either K<55 or K<60 threshold when combined with D1 slope<0. The label "C53b" (K<60 + D1slope<0) covers both.

**Verdict: No new independent candidate. C53b confirmed as unique best combo at n=13, PF=17.43.**

---

## C55b: Stoch K<55 + C43 (0-1 Prior Asia Up Days)

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Stoch K<55 alone | 14 | 18.19 | +0.355% | 71.4% | 9.08 | 37.55 | 25.71 |
| 0-1 prior Asia up (C43) | 15 | 9.77 | +0.317% | 53.3% | 12.90 | 10.37 | 4.54 |
| Stoch K<55 + 0-1 consec | 8 | 15.21 | +0.406% | 62.5% | 11.85 | 25.47 | 10.78 |

**Key finding:** The intersection (n=8) has all 3 years positive (11.85/25.47/10.78) and highest avg=+0.406%. However, n=8 is critically small and below the n≥30 adoption threshold. The avg return is inflated by the tiny sample.

Note: C43 here shows year-2026 PF=4.54 (weak) standalone; when intersected with K<55 it improves 2026 to 10.78, suggesting these two filters together may select higher-quality 2026 trades.

**Verdict: Statistical curiosity but n=8 is too small for any conclusion. Watch for re-test when n→15+ at FXOpen 2028+.**

---

## C55c: Asia Session Quality (Fade Ratio)

The Asia fade ratio measures how much of the Asia rally retraced before the Asia session close: `(asia_high - asia_close) / asia_net`. 0 = price closed at the Asia high; 1.0 = price fully retraced the rally; >1.0 = price went below the open.

Distribution on 32 qualifying trades: mean=0.991, median=0.498.
- <0.3 (Asia very firm): 7 trades
- 0.30–0.50: 9 trades  
- 0.50–1.0: 8 trades
- >1.0 (rally fully reversed): 8 trades

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Asia firm (<30% fade) | 7 | 10.06 | +0.342% | 57.1% | ~inf* | 1.46 | 10.40 |
| Asia mid (30-50% fade) | 10 | 1.14 | +0.008% | 30.0% | 0.00 | 1.30 | 6.06 |
| Asia faded (≥50% fade) | 16 | 6.61 | +0.213% | 43.8% | 1.71 | 33.98 | 4.43 |
| Asia firm + Stoch K<60 | 4 | 40.41 | +0.540% | 75.0% | ~inf | ~inf | 10.40 |

*2024 Asia firm PF is ~inf (zero losses in 2024); all single-year anomalies from tiny n.

**Key finding: Asia fade ratio is strongly year-inconsistent.** Asia "firm" has 2025 PF=1.46 (near-breakeven) despite very high 2024 and 2026. Asia "mid" is catastrophic (PF=1.14, 2024 PF=0.00). Asia "faded" has 2025 PF=33.98 but 2024 PF=1.71.

The apparent "Asia firm + Stoch K<60" n=4 with PF=40.41 is meaningless at that sample size — all year PFs are ~inf from zero losses in tiny n.

**Verdict: REJECTED. Asia fade ratio shows no consistent year-to-year pattern. The splits are erratic, likely due to small n (~7-16 per bucket). Not a usable filter.**

---

## C55d: Bar07 Open Position Within 07:00 Range

The 07:00 bar's open position within its own high-low range: 0=at low, 1=at high. For a SHORT entry at open, a high position (open near the bar's high) is intuitively favorable.

Distribution on 32 qualifying trades: mean=0.552, median=0.703.
- <0.3 (open near low): 10 trades
- 0.30–0.50: 3 trades
- 0.50–0.70: 3 trades
- ≥0.7 (open near high): 16 trades

The median=0.703 confirms most opens are in the upper half of the 07:00 bar.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Open upper half (pos≥0.5) | 19 | 6.25 | +0.183% | 52.6% | 6.85 | 2.18 | 12.48 |
| Open lower half (pos<0.5) | 13 | 4.54 | +0.189% | 30.8% | 1.30 | 12.50 | 0.00 |
| Open top 30% (pos≥0.7) | 16 | 7.01 | +0.200% | 56.2% | 5.43 | 2.18 | ~inf* |
| Open bottom 30% (pos<0.3) | 10 | 2.21 | +0.077% | 20.0% | 1.57 | 4.45 | 0.00 |
| SK<60 + open upper half | 13 | 8.82 | +0.240% | 61.5% | 9.08 | 3.10 | 25.71 |

*Open top 30%, 2026: ~inf due to zero losses in 2026 (small n).

**Key finding: Open position is year-inconsistent.** Open upper half has 2025 PF=2.18 (weak). Open lower half has 2026 PF=0.00 (all losses). SK<60 + upper half shows 2025 PF=3.10 — acceptable but lower than SK<60 alone (2025 PF=13.40). The open position at 07:00 is largely determined by exogenous price action and adds noise.

**Verdict: REJECTED. Bar07 open position shows no consistent year-over-year discrimination. Year inversions in multiple buckets confirm no reliable signal.**

---

## Summary: C55 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C55a: SK<55 + D1slope | IDENTICAL to C53b — same 13 trades | Confirmed C53b; no new candidate |
| C55b: SK<55 + C43 | n=8, PF=15.21, all years positive but tiny n | Small-n curiosity, re-test 2028+ |
| C55c: Asia fade ratio | Year-inconsistent across all buckets | REJECTED |
| C55d: Bar07 open position | Year-inconsistent; inversions in 2025/2026 | REJECTED |

**C53b (n=13, PF=17.43) remains the definitive best combo. C55 confirms its uniqueness.**

---

## Updated Pending Candidates Table (all cycles through C55)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **Stoch K<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best combo = also SK<55+D1** |
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

## Permanently Rejected (C55 scope)

- **C55c (Asia fade ratio):** Year-inconsistent across all fade buckets. Small n per bucket (~7-16) drives erratic annual PFs.
- **C55d (Bar07 open position):** Year-inconsistent with 2026 PF=0.00 for lower half, 2025 PF=2.18 for upper half. No usable split.

---

*Past results are not investment advice.*
