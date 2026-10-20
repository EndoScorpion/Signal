# B62 MR Backtest — Survivors Analysis
**EA:** Strong2010b_claude_b42_mr (b62)  
**Data:** FXOpen ECN EUR/USD 5-digit, M15, Spread 2  
**Periods covered:** 2011–2024 + 2025-26 ("2526")  
**Run date:** 2026-10-19  
**Deposit:** $10,000  

---

## ⚠️ CRITICAL ISSUES — Results Must Be Treated With Caution

### Issue 1: Set Files Applied to Wrong EA
The four param sets (`MR_RegimeSwitch_b62_base`, `_allow_h05h09`, `_allow_h05h10`, `_skip_h16h19`) contain parameters for a **different EA version** (b62 with `ZTF`, `ZPeriod`, `ZTrigger`, `HoldBars`, `UseRegime`, `RegimePeriod`, `RestrictHours`, etc.). None of these parameter names exist in `Strong2010b_claude_b42_mr`. MT4's strategy tester silently ignores unrecognised parameters — **all 60 runs used the EA's compiled defaults**. The four "sets" therefore produced **identical results**.

Evidence: Every (set × year) pair has exactly the same trade count, win%, net profit and profit factor.

### Issue 2: Zero Trades 2019, 2020, 2021
All 60 combinations produced **0 trades** in 2019, 2020 and 2021. Cause unknown — likely one of:
- FXOpen ECN 5-digit history not available / gaps for those years in the tester
- The EA's internal regime filter (`UseSellRegime`, `SellRegimePeriod=1200`) blocking all entries

These three years are excluded from period analysis below but flagged as a data/configuration defect.

### Issue 3: Cost Model Not Applied
MT4 tester included spread (2 pts) only. The full cost model (`cost_model.json` — swap/financing, regulatory fees, commission, taxes) was **not applied** to these results. All figures below are **pre-full-cost**. Applying the cost model would push net returns further negative.

---

## Period Analysis (EA Defaults, All Sets Identical)

### Period 1: 2015–2019

| Year | N | Win% | Net P% | PF |
|------|---|------|--------|----|
| 2015 | 1215 | 77.1% | −1.64% | 0.81 |
| 2016 | 928  | 81.6% | −1.80% | 0.64 |
| 2017 | 1010 | 88.8% | −1.65% | 0.51 |
| 2018 | 791  | 73.6% | −2.36% | 0.63 |
| 2019 | 0    | —    | 0%     | — (ZERO TRADES) |

**Period 1 verdict: NEGATIVE** — All 4 active years net negative, PF < 1.0 in all years.

### Period 2: 2020–2022

| Year | N | Win% | Net P% | PF |
|------|---|------|--------|----|
| 2020 | 0   | —    | 0%     | — (ZERO TRADES) |
| 2021 | 0   | —    | 0%     | — (ZERO TRADES) |
| 2022 | 947 | 72.9% | −0.26% | 0.97 |

**Period 2 verdict: NEGATIVE** — 2/3 years have zero trades (disqualifying); sole active year is net negative.

### Period 3: 2023–2026

| Year | N | Win% | Net P% | PF |
|------|---|------|--------|----|
| 2023 | 735  | 84.3% | −1.25% | 0.63 |
| 2024 | 617  | 81.5% | −0.45% | 0.87 |
| 2526 | 1033 | 85.0% | −0.82% | 0.82 |

**Period 3 verdict: NEGATIVE** — All 3 years net negative, PF < 1.0 in all.

---

## Edge Assessment — Full History (All Years Active)

| Year | N | Win% | Avg Win ($) | Avg Loss ($) | Net P% | PF |
|------|---|------|-------------|--------------|--------|----|
| 2011 | 1142 | 75.6% | — | — | −2.35% | 0.73 |
| 2012 | 971  | 78.9% | — | — | −1.99% | 0.68 |
| 2013 | 1185 | 83.5% | — | — | −2.22% | 0.62 |
| 2014 | 870  | 77.5% | — | — | −0.80% | 0.86 |
| 2015 | 1215 | 77.1% | — | — | −1.64% | 0.81 |
| 2016 | 928  | 81.6% | — | — | −1.80% | 0.64 |
| 2017 | 1010 | 88.8% | — | — | −1.65% | 0.51 |
| 2018 | 791  | 73.6% | — | — | −2.36% | 0.63 |
| 2019 | 0    | —    | — | — | 0.00%  | — |
| 2020 | 0    | —    | — | — | 0.00%  | — |
| 2021 | 0    | —    | — | — | 0.00%  | — |
| 2022 | 947  | 72.9% | ~0.34 | ~−2.92 | −0.26% | 0.97 |
| 2023 | 735  | 84.3% | ~0.34 | ~−2.92 | −1.25% | 0.63 |
| 2024 | 617  | 81.5% | — | — | −0.45% | 0.87 |
| 2526 | 1033 | 85.0% | — | — | −0.82% | 0.82 |

**Root cause of negative edge:** High win rate (73–89%) is undermined by a badly skewed risk:reward ratio. Average winning trade ~$0.03–$0.34; average losing trade ~$2.92–$3.08. This is a structural defect in the EA's TP/SL design at these parameter defaults — tiny TP (7 pts) vs large SL (290 pts).

---

## Survivors

**ZERO SURVIVORS.**

CLAUDE.md rules applied:
- Rule: n < 30 → reject → *2019, 2020, 2021 rejected (0 trades)*
- Rule: reject rules with inconsistent periods → *all 3 periods negative*
- Rule: keep only rules positive net of costs in ≥2 of 3 periods → *no combination meets this*

All 60 (param_set × year) combinations and all 4 param sets are rejected.

---

## Required Actions Before Re-Test

1. **Fix set files:** Create correct `.set` files using parameter names that actually exist in `Strong2010b_claude_b42_mr`. Key parameters to vary: `SellWinFrom`, `SellWinTo`, `SessBlockFrom`, `SessBlockTo`, `DayBlock`, `FriHour`.
2. **Investigate 0-trade years:** Check FXOpen ECN history coverage for 2019/2020/2021 in `mt4_tester2`. Run a single test for 2020 with a known-working set file and inspect the tester log.
3. **Fix TP/SL:** The compiled-default `tp=7` with a 290-pt SL produces a theoretical R:R of 7:290 ≈ 0.024. Even at 89% win rate this is losing. A correct TP must be ≥ 3× the average loss, or the SL must be tightened proportionally.
4. **Apply full cost model** after fixing above issues: `python3 backtest_costs.py --data data/history --hold 3 --cost cost_model.json`

---

*Past results are not financial advice. Data source: FXOpen ECN (survivor bias flag: N/A — EA tested across full period including drawdown years).*
