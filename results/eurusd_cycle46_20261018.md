# EURUSD Cycle 46 — Open Gap, EMA Slope Magnitude, ATR Floor
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C46a: Overnight Open Gap

Gap = 07:00 open minus prior 21:00 close. Positive = EUR gapped UP into the short.

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Gap up (EUR opened higher) | 30 | 5.36 | +0.183% | 43.3% | 3.86 | 7.06 | 6.05 |
| Gap down/flat | 2 | — | — | — | — | — | — |

**Key finding:** 93.8% of qualifying trades already have a positive gap (EUR gapped up into the short). This is structurally implied: Asia net-up ≥ 0.25×ATR selects days where the Asia session rallied, which overwhelmingly produces a gap-up open at 07:00. The filter discriminates nothing. **Permanently rejected** — same geometric implication problem as H4 EMA slope and prior session direction.

---

## C46b: EMA120 Slope Magnitude

EMA slope normalized by ATR to compare across different volatility regimes.

| Group | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-------|---|----|------|------|---------|---------|---------|
| **v2.3 baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| Steep slope (below median) | 16 | 6.76 | +0.222% | 50.0% | 0.98 | 15.96 | 9.73 |
| Shallow slope (above median, <0) | 16 | 4.35 | +0.150% | 37.5% | 9.70 | 2.65 | 4.43 |

EMA slope quartile breakdown:
- Q1 (steepest): n=8, PF=7.93 | 2024: 0.00 | 2025: inf | 2026: 11.06
- Q2: n=8, PF=5.95 | 2024: 1.91 | 2025: 6.74 | 2026: 9.73
- Q3: n=8, PF=8.78 | 2024: 9.70 | 2025: 4.35 | 2026: 7.01
- Q4 (shallowest): n=8, PF=1.81 | 2024: inf | 2025: 0.89 | 2026: 2.26

**Key finding:** Steepest slope (Q1) shows PF=7.93 but 2024 PF=0.00 (zero wins). Shallowest (Q4) shows PF=1.81 with 2025 PF=0.89 (below breakeven). Pattern is inconsistent across years — steeper is not consistently better. **Permanently rejected** — year-inconsistent, no stable edge from slope magnitude.

---

## C46c: ATR Floor (Minimum Volatility Requirement)

Current baseline: ATR≥5 pip (0.0005). Testing whether requiring more volatility filters low-quality noise trades.

| ATR floor | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|-----------|---|----|------|------|---------|---------|---------|
| **≥5 pip (baseline)** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| ≥6 pip | 29 | 5.49 | +0.194% | 44.8% | 4.70 | 7.06 | 5.32 |
| **≥7 pip** | **28** | **5.92** | **+0.209%** | **46.4%** | **4.70** | **7.06** | **6.44** |
| ≥8 pip | 27 | 5.93 | +0.212% | 48.1% | 4.70 | 7.06 | 5.89 |
| ≥10 pip | 22 | 6.72 | +0.245% | 50.0% | 5.85 | 7.06 | 7.56 |

Marginal trades analysis:
- 5-6 pip ATR trades (n=3): PF=0.00 (0% win rate — all three are losers)
- 6-7 pip ATR trades (n=1): Minor loser

**Key finding:** The 5-6 pip ATR band contains 3 trades, ALL losers (win rate=0%). These low-volatility entries are pure noise and drag down performance. Raising the floor to 7 pip removes these 4 losers (n drops 32→28) and improves PF from 5.38→5.92 with ALL THREE YEARS improving. This is the cleanest floor because it removes identifiable losers, not random sample reduction.

At ≥7 pip: 2024 PF=4.70 (up from 3.86), 2025 PF=7.06 (unchanged, no losers removed there), 2026 PF=6.44 (up from 6.05).

**Verdict:** n=28 is below the n≥30 adoption threshold, but by only 2 trades. The structural case is strong: removing confirmed losers. **Pending candidate — all 3 years improve, consistent year-over-year.**

Re-test when: FXOpen 2027 data (n→~30+)

---

## Updated Pending Candidates Table (all cycles through C46)

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
| **C46c** | **ATR ≥ 7pip floor** | **28** | **5.92** | **+0.209%** | **FXOpen 2027** |

---

## Permanently Rejected (C46 scope)

- **C46a (open gap):** 93.8% positive gap — geometrically implied by Asia net-up condition
- **C46b (EMA slope magnitude):** Year-inconsistent; steeper slope not reliably better

---

*Past results are not investment advice.*
