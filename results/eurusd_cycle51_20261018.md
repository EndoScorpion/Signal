# EURUSD Cycle 51 — RSI at Entry, Pending Combos, Asia-to-Entry Extension
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C51a: RSI(14) at 07:00 Entry

RSI(14) is computed on the H1 close series up to and including the 07:00 bar open (i.e., at 07:00, before the bar closes). Tests whether EUR overbought/not-overbought conditions predict fade success.

RSI distribution on 32 qualifying trades: mean=51.1, median=50.6, range 22.1–75.9. Most trades (14/32) have RSI<50.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| RSI<55 | 22 | **8.97** | **+0.268%** | **54.5%** | **6.81** | **10.07** | **11.15** |
| RSI>=55 | 10 | 1.07 | +0.004% | 20.0% | 1.31 | 0.00 | 1.52 |
| RSI>=50 | 18 | 1.28 | +0.017% | 22.2% | 1.50 | 1.06 | 1.01 |
| RSI>=60 | 7 | 1.57 | +0.034% | 28.6% | 1.57 | 0.00 | ~inf* |
| RSI>=70 | 3 | 0.00 | -0.072% | 0.0% | 0.00 | — | — |

*RSI>=60 2026 inflated: zero losses in 2026 from n=1 trade.

**Key finding: STRONG SIGNAL. RSI<55 at entry is the most consistent pattern found.**
- PF=8.97 with all 3 years strongly positive: 2024 PF=6.81, 2025 PF=10.07, 2026 PF=11.15
- Win rate jumps from 43.8% → 54.5%
- avg improves from +0.186% → +0.268%

**Economic interpretation:** The v2.3 baseline already requires EMA120<0 (bearish trend) and Asia net-up (overnight rally). When RSI stays below 55 despite the Asia rally, it means:
1. The bullish counter-trend momentum has NOT been strong enough to push RSI into overbought territory (>55)
2. The underlying trend is still dominating — the Asia rally is weak within the broader downtrend
3. When RSI spikes above 55-60 at entry, those are stronger counter-trend moves that resist the London-session fade

Conversely, high RSI (>=55) at entry → catastrophic: PF=1.07, win=20%, 2025 PF=0.00.

**n=22 — below n≥30 threshold.** Cannot be adopted yet but this is the cleanest directional signal found in this session. Rate of inclusion: 22/32 = 68.75% of baseline trades — not structurally implied.

**Verdict:** Strong pending candidate. Re-test when FXOpen 2027 data available (n→~28-29), adopt at FXOpen 2028 (n→~30+).

---

## C51b: C48b (bar07_bearish) × C46c (ATR≥7pip) Combo

Both are existing pending candidates. Testing whether they combine additively.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| C48b: bar07 bearish | 19 | 10.33 | +0.296% | 57.9% | 6.84 | 13.40 | 10.82 |
| C46c: ATR≥7pip | 28 | 5.92 | +0.209% | 46.4% | 4.70 | 7.06 | 6.44 |
| **C48b + C46c combined** | **16** | **12.18** | **+0.343%** | **62.5%** | **9.08** | **13.40** | **15.39** |

**Key finding:** The combo (n=16) outperforms both components. All 3 years strongly positive and with improving trajectory (2024 PF=9.08, 2025 PF=13.40, 2026 PF=15.39). The 2026 figure (PF=15.39) is the best single-year performance seen for any combo.

However, n=16 is well below the n≥30 threshold. The intersection retains about 84% of C48b trades (16/19) but only 57% of C46c trades (16/28), suggesting significant overlap — C46c is a fairly broad filter.

**Verdict:** Strong combo candidate. n<30; re-test at FXOpen 2028.

---

## C51c: Asia-to-Entry Price Extension

How far did price extend from Asia session close (06:00 close) to the 07:00 entry bar open, normalized by ATR?

Formula: `extension = (open07 - asia_close) / ATR14`

Distribution on 32 qualifying trades:
- mean=-0.057×ATR, median=0.000×ATR, min=-0.488×ATR, max=+0.188×ATR
- Q1=-0.160, Q3=0.000

**Critical observation:** The MEDIAN extension is 0.000 or slightly negative. This means most qualifying trades have the 07:00 bar opening at or BELOW the Asia session close. The Asia net-up filter (asia_net≥0.25×ATR) ensures the Asia session itself rallied — but the pre-London period (07:00 bar) often gives back some of that gain.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| Extension <0.1×ATR | 26 | 6.85 | +0.233% | 50.0% | 4.76 | 9.93 | 7.16 |
| Extension 0.1-0.3×ATR | 6 | 0.67 | -0.018% | 16.7% | 0.00 | 0.00 | 3.01 |
| Extension >0.3×ATR | 0 | — | — | — | — | — | — |

**Key finding:** When the 07:00 bar opens significantly ABOVE the Asia close (extension >0.1×ATR, n=6), the trade is terrible: PF=0.67, win=16.7%, 2024 and 2025 both zero. These are cases where the overnight rally continued right up to entry — the position already has less room to fade.

The dominant group (extension <0.1×ATR, n=26) performs well. However, the two groups don't have enough n for a reliable binary cutoff.

**Verdict:** Directionally interesting (large extensions hurt) but n=6 in the "bad" group makes this unreliable. The >0.1×ATR filter would reject only 6/32 trades (18.75% base rate) and we'd need n≥30 in each group. **Pending — re-test at FXOpen 2027.**

---

## Summary

| Test | Finding | Verdict |
|------|---------|---------|
| C51a: RSI<55 | n=22, PF=8.97, all 3 years 6.81/10.07/11.15 | **Strong pending** |
| C51b: C48b+C46c | n=16, PF=12.18, all 3 years 9.08/13.40/15.39 | **Combo pending** |
| C51c: Extension <0.1×ATR | n=26, PF=6.85 vs rejected 6-trade hi-ext group | Inconclusive (n=6 in bad group) |

C51a (RSI<55) is the session's **top new finding** — the most consistent directional signal in recent cycles. RSI>=55 at entry is catastrophically bad (PF=1.07, 2025 PF=0.00).

---

## Updated Pending Candidates Table (all cycles through C51)

| ID | Filter | n | PF | avg% | Re-test when |
|----|--------|---|----|------|--------------|
| **C51a** | **RSI(14)<55 at entry** | **22** | **8.97** | **+0.268%** | **FXOpen 2027-28** |
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
| **C51b** | **C48b + C46c combo** | **16** | **12.18** | **+0.343%** | **FXOpen 2028** |
| C51c* | Extension <0.1×ATR | 26 | 6.85 | +0.233% | FXOpen 2027 (needs >0.1 n≥10) |

---

## Permanently Rejected (C51 scope)

- **C51c high extension (>0.1×ATR):** n=6 in rejection group; directionally suggests large extensions hurt, but too few to rely on. Borderline directional finding only.

---

*Past results are not investment advice.*
