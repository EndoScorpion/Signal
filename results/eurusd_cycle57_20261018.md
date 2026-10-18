# EURUSD Cycle 57 — Overnight Gap Deeper Analysis + C53b+Gap Combo
**Date:** 2026-10-18  
**Base:** v2.3 — EMA120<0, ADX<30, ATR<75pct, ATR≥5pip, Wed/Thu, Asia net-up≥0.25×ATR, Entry 07:00 SHORT, Stop 0.80×ATR, Exit 21:00  
**Data:** FXOpen ECN H1 (n=17,247 bars, 2024-01-02 to 2026-10-16)  
**Cost:** 0.00008/trade

---

## C57a: No-Gap-Up as Standalone Baseline Modifier

C56c found the overnight gap-up exclusion within SK<60. This cycle tests it directly on the full baseline.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **Baseline** | **32** | **5.38** | **+0.186%** | **43.8%** | **3.86** | **7.06** | **6.05** |
| No gap up (open07≤close06) | 25 | **7.90** | **+0.248%** | **52.0%** | **4.76** | **17.14** | **7.16** |
| Gap up only (open07>close06) | 7 | 0.47 | -0.035% | 14.3% | 0.00 | 0.00 | 3.01 |
| Exactly flat (open07=close06) | 12 | 9.28 | +0.239% | 58.3% | 5.03 | 15.93 | 9.63 |
| Gap down only (open07<close06) | 13 | 7.03 | +0.256% | 46.2% | 4.67 | 18.03 | 2.33 |

**Key findings:**

- **No gap up (n=25): PF=7.90, all 3 years positive (4.76/17.14/7.16).** Excluding just 7 gap-up trades lifts baseline PF from 5.38 to 7.90. This is the cleanest standalone filter improvement — a pure exclusion rule requiring no additional calculation beyond what's already in C56c.
- **Gap up confirmed catastrophic** (C56c finding replicated exactly): PF=0.47, 2024 PF=0.00, 2025 PF=0.00. Seven trades, all concentrated losers.
- **Exactly flat (n=12): PF=9.28** — the flat-open subset outperforms gap-down within the no-gap-up group. When London opens exactly where Asia closed, the SHORT setup is strongest.
- **Gap down (n=13): PF=7.03, 2026 PF=2.33** — valid standalone but 2026 is notably weak vs the flat subset.

**Verdict: NEW STANDALONE CANDIDATE. Baseline + no gap up (n=25, PF=7.90) is the highest-n qualifying filter found so far that improves all three years. Re-test when n≥30 (estimated FXOpen mid-2027).**

---

## C57b: C53b + No Gap Up

Testing whether adding the gap-up exclusion to C53b (n=13, PF=17.43) further improves results.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| **C53b (SK<60+D1slope<0)** | **13** | **17.43** | **+0.366%** | **69.2%** | **9.08** | **33.90** | **25.71** |
| C53b + no gap up | 12 | 22.04 | +0.401% | 75.0% | 9.08 | ~inf* | 25.71 |
| C53b + gap down only | 6 | 18.64 | +0.511% | 66.7% | 7.70 | ~inf* | ~inf* |
| C53b + exactly flat | 6 | 32.84 | +0.291% | 83.3% | ~inf* | ~inf* | 22.88 |

*~inf = near-zero denominator (zero losses in that year), artifact of tiny n.

**Key finding: C53b + no gap up (n=12) removes 1 trade (the 1 gap-up within the C53b set) and shows 2025 near-zero losses — an artifact of eliminating a single bad trade. This is a 1-trade effect, not an independent signal.**

- C53b already had only 1 gap-up qualifying trade (confirmed: C57c shows SK<60 + gap up n=1). Removing it produces the astronomical 2025 PF.
- All sub-groups at n=6 are statistically meaningless; year-level PFs of ~inf confirm this.
- The gap-up exclusion adds no independent value within C53b because C53b's SK<60 filter already captures 14/15 qualifying no-gap-up trades (the entire C56c pool).

**Verdict: NOT A NEW CANDIDATE. C53b + no gap up is a 1-trade improvement artifact. C53b's SK<60 already filters most gap-ups. No adoption.**

---

## C57c: Gap Direction × Stoch K Thresholds

Decomposing the 32 qualifying trades by both gap direction and SK threshold to understand the interaction.

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| SK<60 + no gap up | 14 | 15.57 | +0.352% | 71.4% | 9.08 | 20.83 | 25.71 |
| SK<60 + gap up | 1 | 0.00 | -0.061% | 0.0% | — | 0.00 | — |
| SK>=60 + no gap up | 11 | 3.26 | +0.115% | 27.3% | 2.54 | 12.11 | 0.00 |
| SK>=60 + gap up | 6 | 0.54 | -0.031% | 16.7% | 0.00 | 0.00 | 3.01 |

**Key findings:**

- **The gap-up catastrophe is almost entirely in SK≥60.** Of 7 gap-up trades: 6 are SK≥60 (PF=0.54, all years terrible) and 1 is SK<60 (a total loss).
- **SK≥60 + no gap up (n=11): PF=3.26, 2026 PF=0.00 — year-inconsistent.** Even after removing gap-ups from the SK≥60 group, 2026 PF=0.00 (zero wins). This bucket is structurally poor: SK≥60 means price is already elevated relative to recent range, reducing SHORT upside.
- **SK<60 + no gap up = C56c finding (n=14, PF=15.57):** Confirmed. This is the clean interaction.
- **The structural insight:** SK<60 already excludes most gap-up scenarios (only 1/15 SK<60 trades had a gap up). The gap direction and SK level are correlated — gap-ups tend to push SK higher.

**Verdict: Confirms C56c (SK<60 + no gap up) as the correct interaction. SK≥60 + no gap up is NOT a usable filter (2026 PF=0.00). No new candidates.**

---

## C57d: Asia Close Position (How Near to Asia High?)

`asia_close_pos = (asia_close - asia_low) / (asia_high - asia_low)`. 0 = closed at the Asia range low, 1 = closed at the Asia range high. Hypothesized that closing near the Asia high preserves SHORT momentum into London.

Distribution on 32 qualifying trades:  
mean=0.711, median=0.735  
- <0.5 (closed below midrange): 3 trades  
- 0.5–0.7: 10 trades  
- ≥0.7 (closed near high): 19 trades  

| Configuration | n | PF | avg% | win% | 2024 PF | 2025 PF | 2026 PF |
|--------------|---|----|------|------|---------|---------|---------|
| Asia close high (pos≥0.7) | 19 | 5.35 | +0.181% | 47.4% | 4.66 | 3.90 | 8.26 |
| Asia close mid (0.5–0.7) | 10 | 6.38 | +0.225% | 40.0% | 0.97 | 14.29 | — |
| Asia close low (<0.5) | 3 | 2.73 | +0.087% | 33.3% | ~inf | 0.00 | 0.00 |
| SK<60 + Asia close high | 10 | 15.58 | +0.334% | 70.0% | 7.70 | ~inf* | 25.71 |
| SK<60 + Asia close low | 0 | — | — | — | — | — | — |

*~inf = zero losses in 2025 within this tiny subset, artifact.

**Key findings:**

- **Distribution is severely skewed: 19/32 qualifying trades have pos≥0.7.** The Asia session that generates our setup (net-up ≥0.25×ATR) naturally closes near its high — the closing position filter cannot discriminate within the qualifying set.
- **No meaningful PF difference across buckets:** 5.35 vs 6.38 vs 2.73 — all weak, and year-inconsistency is pervasive. Asia close mid has 2024 PF=0.97 (near-breakeven).
- **Asia close low (n=3): statistically void.** Only 3 trades.
- **SK<60 + Asia close high (n=10): 2025 PF=~inf is an artifact** (no 2025 losses in this tiny set). Not a finding.

**Verdict: REJECTED. Asia close position provides no discriminating power within the qualifying set. The baseline filter (asia_net≥0.25×ATR) already selects for Asia sessions that close near their high — the position variable is endogenous to the entry condition.**

---

## Summary: C57 Findings

| Test | Key Finding | Verdict |
|------|-------------|---------|
| C57a: No-gap-up standalone | n=25, PF=7.90, all 3 years positive | **NEW CANDIDATE** (re-test when n≥30, ~2027) |
| C57b: C53b + no gap up | 1-trade effect; 2025 PF=~inf artifact | NOT a candidate |
| C57c: Gap × SK thresholds | Gap catastrophe in SK≥60; SK<60+no gap up confirmed | Confirms C56c; no new candidates |
| C57d: Asia close position | Distribution skewed (19/32 pos≥0.7); no discrimination | REJECTED |

**C57a (baseline + no gap up) is the main new finding.** It's broader than C56c — applies to the full baseline rather than the SK<60 subset — and is the only filter approaching n≥30 with all-years-positive consistency.

---

## Updated Pending Candidates Table (all cycles through C57)

| ID | Filter | n | PF | avg% | Re-test when | Notes |
|----|--------|---|----|------|--------------|-------|
| C52c | Stoch K<55 at entry | 14 | 18.19 | +0.355% | FXOpen 2028 | = RSI<55 (collinear) |
| **C53b** | **Stoch K<60 + D1 slope<0** | **13** | **17.43** | **+0.366%** | **FXOpen 2028** | **Best combo** |
| **C56c** | **SK<60 + no gap up** | **14** | **15.57** | **+0.352%** | **FXOpen 2028** | **Gap-up exclusion, SK<60** |
| **C57a** | **Baseline + no gap up** | **25** | **7.90** | **+0.248%** | **FXOpen 2027** | **Standalone gap exclusion** |
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

## Permanently Rejected (C57 scope)

- **C57b (C53b + no gap up):** 1-trade-removal artifact; 2025 PF=~inf from zero losses in a 12-trade set. Not an independent signal.
- **C57d (Asia close position):** Structurally collinear with entry condition (asia_net≥0.25×ATR already selects high close-position sessions). Distribution too skewed (19/32 at pos≥0.7) to discriminate.

---

*Past results are not investment advice.*
