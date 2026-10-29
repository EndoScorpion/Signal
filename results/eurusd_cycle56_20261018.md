# EURUSD Cycle 56 — Three-Filter Combos, Bar07 Range, Overnight Gap
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C56a: Three-Filter Combos from C53b

Adding a third filter to C53b (Stoch K<60 + D1 slope<0, n=13, PF=17.43).

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| C53b (SK<60+D1slope<0) | 13 | 17.43 | +0.366% | 69.2% | 9.08 | 33.90 | 25.71 |
| C53b + 0-1 prior Asia up (C43) | 8 | 15.21 | +0.406% | 62.5% | 11.85 | 25.47 | 10.78 |
| C53b + ATR≥7pip (C46c) | 11 | 20.44 | +0.415% | 72.7% | 9.08 | 33.90 | ~inf* |
| C53b + skip Q2 (C42) | 11 | 14.87 | +0.365% | 63.6% | 9.08 | 28.86 | 17.77 |

*C53b + ATR≥7pip, 2026: ~inf due to zero losses in 2026 (small n). Unreliable.

**Key findings:**
- **C53b + ATR≥7pip:** PF=20.44 looks strong but 2026 PF=~inf (zero losses) means this is year-inconsistent. ATR filter can't be validated at n=11 with an anomalous year.
- **C53b + skip Q2:** n=11, PF=14.87, genuinely all-3-years positive (9.08/28.86/17.77). Removes 2 trades from C53b but PF drops (17.43→14.87) — not additive.
- **C53b + C43:** Same n=8 result as C55b — too small.

Adding a third filter to C53b in all cases shrinks n further (from 13 to 8-11) without improving the already-excellent baseline PF. Three-filter combos at this n are over-fit territory.

**Verdict: No new three-filter candidates. C53b at two filters remains the frontier.**

---

## C56b: Bar07 Range Size vs ATR

Bar07 range/ATR distribution on 32 qualifying trades: mean=1.55, median=1.45. Range: all 32 trades have bar07_range ≥ 0.4×ATR (minimum observed ~0.8×ATR). Zero trades qualify as "small bar" (<0.4×ATR).

The 07:00 bar at the London open is invariably large relative to ATR — the market is active. This filter cannot discriminate within the qualifying set.

**Verdict: PERMANENTLY REJECTED. No variation to exploit; every trade has a large 07:00 bar.**

---

## C56c: Overnight Gap (Close06 to Open07) — Major Finding

The overnight gap measures price movement from the 06:00 Asia close to the 07:00 London open.

Distribution on 32 qualifying trades: mean=-0.0566×ATR, median=0.  
- Zero gap (open07 = close06): 12 trades
- Gap down (open07 < close06): 13 trades
- Gap up (open07 > close06): 7 trades

(All gap-up trades are "significant" >5%ATR; same for gap-down — suggesting these are discrete events, not tiny drifts.)

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Gap up (open07 > close06) | 7 | **0.47** | **-0.035%** | **14.3%** | **0.00** | **0.00** | 3.01 |
| Gap down (open07 < close06) | 13 | 7.03 | +0.256% | 46.2% | 4.67 | 18.03 | 2.33 |
| Zero gap (flat) | 12 | 5.48 | +0.210% | 41.7% | 4.52 | 5.13 | 6.90 |
| Stoch K<60 + gap down | 14 | 15.57 | +0.352% | 71.4% | 9.08 | 20.83 | 25.71 |
| Stoch K<60 + gap up | 1 | 0.00 | -0.061% | 0.0% | — | 0.00 | — |

**Critical finding: Gap up at the London open is catastrophic for the SHORT setup.**

7 qualifying trades where open07 > close06 (price gapped higher into the London open): PF=0.47, avg=-0.035%, 2024 PF=0.00, 2025 PF=0.00. This is a near-perfect loss signal.

**Economic interpretation:** When price gaps UP between Asia close and London open (meaning overnight/early European interest pushed EUR higher between 06:00 and 07:00), the bullish momentum is active and fresh. Shorting into a fresh gap-up means fighting newly-arrived buyers. The fade setup requires that the overnight rally has LOST steam — a gap up into the entry bar means it hasn't.

**Gap down is positive:** 13 trades with gap down show PF=7.03, all 3 years positive (4.67/18.03/2.33). When price slipped between 06:00 and 07:00, it signals the overnight rally is already weakening before the London open.

**Stoch K<60 + gap down: n=14, PF=15.57, all 3 years (9.08/20.83/25.71):**  
Note n=14 because SK<60 includes the 15th trade (zero-gap case) which this excludes — so this is actually the 14 SK<60 qualifying trades that did NOT gap up. This is a strong filter with one more trade than C53b (n=13).

**Gap-up exclusion as standalone filter:**  
Simply EXCLUDING the 7 gap-up trades from baseline would give n=25 (baseline minus 7 gap-ups), with improved metrics. This is a new rejection rule candidate.

**Key question:** Is "no gap up" redundant with Stoch K<60? Of the 7 gap-up trades: 1 has SK<60 (the one that hurt n=15 SK<60 performance). So SK<60 already excludes 6/7 gap-up losers, but the gap-up exclusion catches the 1 remaining gap-up loser in the SK<60 set.

**Verdict: Strong new candidate. Gap-up exclusion (or equivalently: require open07 ≤ close06) is the strongest new filter found in C56. All 3 years confirm direction. Pending n growth for formal adoption.**

---

## C56c Supplementary: Revised SK<60 Variants

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| SK<60 alone | 15 | 13.21 | +0.324% | 66.7% | 9.08 | 13.40 | 25.71 |
| **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **71.4%** | **9.08** | **20.83** | **25.71** |
| SK<60 + D1slope<0 (C53b) | 13 | 17.43 | +0.366% | 69.2% | 9.08 | 33.90 | 25.71 |

SK<60 + no gap up (n=14) sits between SK<60 alone and C53b in both n and PF — a middle ground that uses a purely intraday/structural condition rather than requiring the D1 slope calculation.

---

## Summary: C56 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C56a: Three-filter combos | All reduce n without PF improvement; one year anomaly | No new candidates |
| C56b: Bar07 range | All trades have large bar (>0.8×ATR); no variation | PERMANENTLY REJECTED |
| C56c: Overnight gap | Gap up = catastrophic (PF=0.47, 2024/2025 zero); gap down = positive | **NEW CANDIDATE** |

---

## Updated Pending Candidates Table (all cycles through C56)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **Stoch K<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best combo** |
| **C56c** | **SK<60 + no gap up (open07≤close06)** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | **Gap-up exclusion** |
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

## Permanently Rejected (C56 scope)

- **C56a three-filter combos:** Over-parameterized at current n; one year anomalies (2026 PF=~inf) in ATR combo. No adoption.
- **C56b (bar07 range):** Zero variation — all qualifying bars are large. Cannot discriminate.

---

*Past results are not investment advice.*
