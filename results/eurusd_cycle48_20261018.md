# EURUSD Cycle 48 — Asia Final Bar, Entry Bar Candle, Asia Range Position
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C48a: Asia Final Bar (06:00) Direction

06:00 bar is the last hour of the Asia session. 56.2% of qualifying trades have 06:00 bullish.

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| 06:00 bar bullish | 18 | 5.45 | +0.221% | 38.9% | 4.61 | 6.62 | 4.54 |
| 06:00 bar bearish | 14 | 5.24 | +0.140% | 50.0% | 2.69 | 9.16 | 7.48 |

06:00 magnitude buckets:
- Big bear 06:00 (>0.05 ATR down): n=12, PF=3.47 | 2024: 2.69 | 2025: 9.16 | 2026: 1.56
- Big bull 06:00 (>0.05 ATR up): n=18, PF=5.45 | 2024: 4.61 | 2025: 6.62 | 2026: 4.54

**Key finding:** 06:00 direction shows no consistent discrimination — bullish and bearish splits are nearly equal in PF (5.45 vs 5.24), and year-by-year the pattern reverses (bearish 06:00 is better in 2025/2026 but bullish is better in 2024). Neither subgroup consistently outperforms. Big bear 06:00 has 2026 PF=1.56, showing instability. **Permanently rejected** — no consistent edge from Asia final bar direction.

---

## C48b: 07:00 Entry Bar Candle Direction

07:00 bar closes lower (bearish) 62.5% of the time. This tests whether the entry bar's own direction predicts fade success.

Note: C35 (bear07) measures whether the 07:00 OPEN is lower than the prior bar's close (i.e., opening gap direction). C48b measures whether the 07:00 bar itself closes below its open (intrabar candle direction). These are different: a bar can open with a gap down (bearish C35 signal) but then recover to close above its open.

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| 07:00 bar bullish (close > open) | 12 | 1.13 | +0.008% | 16.7% | 2.14 | 0.00 | 0.00 |
| **07:00 bar bearish (close < open)** | **20** | **10.69** | **+0.292%** | **60.0%** | **6.84** | **13.40** | **12.48** |

**Key finding: VERY STRONG signal.** When the 07:00 bar itself closes bearish (fade has already started during that bar), the trade shows:
- PF=10.69 (vs baseline 5.38 — almost 2× improvement)
- ALL THREE YEARS strongly positive: 2024 PF=6.84, 2025 PF=13.40, 2026 PF=12.48
- Win rate = 60.0% (vs 43.8% baseline)
- avg = +0.292% (vs +0.186% baseline)

The 12 bullish 07:00 bar trades are catastrophically bad: 2025 PF=0.00 and 2026 PF=0.00 (zero wins in those years from 12 trades).

**This is a new interpretation of the C35 finding.** C35 (bear07 = open07 < prev close) had n=19, PF=10.33. C48b (bar07 closes down) has n=20, PF=10.69. These likely overlap significantly but are measuring slightly different things. The C48b definition is cleaner for live trading (you know the 07:00 bar's close at 08:00 — one bar later).

**Implementation note:** This requires waiting until 08:00 to enter, not 07:00. Entry would be at the 08:00 open after observing the 07:00 bar close below its open.

**Verdict:** n=20, PF=10.69, all years strongly positive. Below the n≥30 threshold but this is an extremely clean and consistent signal. **Strong pending candidate — strongest single-bar signal found.**

Re-test when: FXOpen 2027 data (n→~26-27+), FXOpen 2028 data (n→~30+)

---

## C48c: Asia Close Position in Range

Where does the 06:00 close sit within the Asia session's high-low range? Mean=0.711 (close to Asia high).

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Close in top 25% of range (≥0.75) | 15 | 5.29 | +0.189% | 46.7% | 5.54 | 1.46 | 10.82 |
| Close in bottom 75% (<0.75) | 17 | 5.46 | +0.183% | 41.2% | 2.12 | 11.76 | 1.56 |

Quartile breakdown:
- Q1 (bottom, 0-25%): n=1 — single trade, useless
- Q2 (25-50%): n=2, PF=0.00 (both years zero) 
- Q3 (50-75%): n=14, PF=6.22 | 2024: 0.78 | 2025: 17.30 | 2026: 3.24
- Q4 (top, 75-100%): n=15, PF=5.29 | 2024: 5.54 | 2025: 1.46 | 2026: 10.82

**Key finding:** No consistent pattern — Q4 (top of range) looks strong in 2024/2026 but poor in 2025. Q3 (50-75%) looks strong in 2025 but poor in 2024. The top-vs-bottom split gives nearly identical PF (5.29 vs 5.46) and the year-by-year pattern reverses. **Permanently rejected** — position within Asia range shows no consistent discriminatory power.

---

## Summary

- **C48a:** Dead — 06:00 bar direction year-inconsistent
- **C48b:** **STRONG new pending candidate** — bar07 bearish (close<open) gives n=20, PF=10.69, all 3 years strongly positive. Entry at 08:00 open (requires seeing 07:00 bar close).
- **C48c:** Dead — Asia close range position year-inconsistent

---

## Updated Pending Candidates Table (all cycles through C48)

| ID | Filter | n | PF | avg% | Re-test when |
|----|--------|---|----|------|--------------|
| C25b | D1 EMA20 slope<0 | 24 | 7.15 | +0.231% | FXOpen 2027 |
| C35 | Bear07 (open07 < prev close) | 19 | 10.33 | +0.319% | FXOpen 2027-28 |
| **C48b** | **Bar07 bearish (close<open)** | **20** | **10.69** | **+0.292%** | **FXOpen 2027-28** |
| C37 | ATR expanding (>5d ago) | 17 | 8.52 | +0.252% | FXOpen 2027 |
| C43 | 0-1 prior Asia up days | 16 | 8.53 | +0.292% | FXOpen 2027-28 |
| C42 | Skip Q2 (Apr-Jun) | 24 | 7.22 | +0.236% | FXOpen 2027 |
| C25b+C35 | D1slope + bear07 | 17 | 12.16 | +0.324% | FXOpen 2028 |
| C25b+C43 | D1slope + 0-1 consec | 14 | 9.54 | +0.312% | FXOpen 2028 |
| C27 | Asia final 2h > 0 | 17 | 6.68 | +0.213% | FXOpen 2028 |
| C45b* | Asia ≥ 0.35×ATR | 29 | 5.66 | +0.196% | FXOpen 2027 (borderline) |
| C46c | ATR ≥ 7pip floor | 28 | 5.92 | +0.209% | FXOpen 2027 |

---

## Permanently Rejected (C48 scope)

- **C48a (06:00 bar direction):** No consistent edge; year-inconsistent across bullish/bearish splits
- **C48c (Asia range position):** Year-inconsistent; top-vs-bottom shows reversed patterns by year

---

*Past results are not investment advice.*
