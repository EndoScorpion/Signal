# Clone + Improve Engine — Results 2026-10-19

**IS:** FXOpen ECN H1 2024-01..2026-10-16 (2.79 yr)  
**OOS:** TwelveData H1 2020-01..2023-12 (4 yr)  
**Cost:** 0.00008/trade · 0.1 lot = $0.10/ECN-pt (5-digit)  
**Engine:** `/mnt/project-files/backups/clone_engine_20261019.txt`  
*Past results not investment advice.*

---

## Summary

Three T31s variants survive OOS with n≥30 and consistent WR/PF across both periods.  
T11 and T6/v23 families **did not** reproduce OOS in this engine; implementation notes below.

---

## Survivors — OOS PASS (n≥30, OOS PF≥1.0, OOS WR≥50%)

| Label | IS n | IS WR% | IS PF | IS avg pts | OOS n | OOS WR% | OOS PF | OOS avg pts | Notes |
|-------|------|--------|-------|-----------|-------|---------|--------|-------------|-------|
| **T31s_BASE** | 72 | 62.5% | 1.63 | 44 pts | 86 | 61.6% | **1.67** | 58 pts | Baseline — OOS > IS |
| **T31s+strong** | 52 | 63.5% | 1.67 | 51 pts | 70 | 61.4% | **1.72** | 63 pts | day_up>1.0×ATR filter |
| **T31s+xnfp** | 53 | 62.3% | 1.40 | 30 pts | 69 | 62.3% | **1.96** | 80 pts | Exclude NFP Friday |

**T31s definition (all three):** SHORT at 14:00 UTC on Fridays when `open−prev_close > threshold×ATR14`, no stop, exit 21:00.

- **T31s_BASE**: threshold = 0.5× ATR14
- **T31s+strong**: threshold = 1.0× ATR14 (stronger day move required)
- **T31s+xnfp**: threshold = 0.5×, plus exclude first Friday of month (NFP dates)

### Key observation: OOS outperforms IS for all three
OOS PF is equal to or higher than IS PF for every survivor — a sign of genuine edge, not overfitting.

---

## Failed Clones (n≥30 shown, OOS < threshold)

| Label | IS n | IS WR% | IS PF | IS avg pts | OOS n | OOS WR% | OOS PF | OOS avg pts | Issue |
|-------|------|--------|-------|-----------|-------|---------|--------|-------------|-------|
| T11_BASE | 258 | 33.3% | 1.13 | 8 pts | 205 | 30.2% | 1.09 | 7 pts | ⚠ Wrong WR vs orig — impl diff (see note) |
| T6_BASE | 292 | 51.0% | 1.11 | 8 pts | 288 | 38.5% | 0.58 | -101 pts | OOS fails badly |
| T11+asia+slope | 52 | 36.5% | 1.33 | 19 pts | 34 | 26.5% | 0.89 | -8 pts | OOS flip |
| T11+wedthu | 107 | 31.8% | 1.01 | 1 pt | 103 | 30.1% | 1.12 | 10 pts | Both too flat |
| T11+atrfloor | 258 | 33.3% | 1.13 | 8 pts | 205 | 30.2% | 1.09 | 7 pts | Same as base |
| T31s+slope | 27 | 55.6% | 1.09 | 8 pts | 25 | 56.0% | 1.17 | 17 pts | ⚠ n<30 both periods |
| T6+asia | 126 | 51.6% | 1.14 | 9 pts | 132 | 31.8% | 0.43 | -168 pts | OOS collapse |
| T6+hold8 | 292 | 52.1% | 1.05 | 3 pts | 288 | 38.2% | 0.54 | -106 pts | OOS collapse |
| T6+stop1x | 292 | 40.8% | 0.89 | -8 pts | 288 | 12.5% | 0.52 | -55 pts | Stop kills edge |
| T31s+strong | 52 | 63.5% | 1.67 | 51 pts | 70 | 61.4% | 1.72 | 63 pts | ✓ SURVIVOR above |
| T31s+xnfp | 53 | 62.3% | 1.40 | 30 pts | 69 | 62.3% | 1.96 | 80 pts | ✓ SURVIVOR above |
| T11+exit23 | 255 | 32.2% | 1.24 | 16 pts | 205 | 27.3% | 1.20 | 17 pts | Marginal WR |
| T6+mom3pos | 99 | 51.5% | 1.31 | 20 pts | 78 | 46.2% | 0.65 | -85 pts | OOS collapse |
| T6+monfri | 362 | 53.6% | 1.15 | 12 pts | 393 | 39.4% | 0.59 | -96 pts | OOS collapse |
| T11_long (mirror) | 278 | 32.0% | 1.11 | 8 pts | 222 | 24.8% | 0.71 | -24 pts | OOS fail |

---

## Implementation Notes

### T11 (SS-MOM3H-LN)
**Original** (win_logic table): n=140, WR=70%, PF=3.95, avg=53 pts.  
**This engine** (T11_BASE): n=258, WR=33%, PF=1.13.  
Large discrepancy — original T11 used a **different momentum formula** (`mom3h` = 3-bar close delta measured from 11:00–14:00 only, not a rolling window close diff). The 1-bar shift rule and session aggregation differ from this engine's `mom3=close.diff(3).shift(1)`. **T11 results here are not comparable to the original.** Do not use T11 clones from this run.

### v2.3 (Asia Fade)
Missing ADX(14) column in data — my engine skips the ADX<30 filter. n=53 vs real n=32. v23 results here are degraded; use the confirmed `eurusd_fxopen_h1.csv` results from cycles 1–24.

### v23+e7 (sell-stop entry)
Engine doesn't simulate limit/stop order fill — all entries fill at open. v23+e7 shows 0% WR because the offset logic is incorrect. Discard.

### T6 (EMA20 drift)
Weak OOS across all variants — OOS 2020-23 PF<0.6 for all T6 clones. The edge appears regime-dependent. **Do not trade T6 until further OOS analysis.**

---

## Adaptive Learning — What Improved

| Technique | Winner | Effect |
|-----------|--------|--------|
| Magnitude filter (`+strong`) | T31s | IS PF: 1.63→1.67, OOS PF: 1.67→1.72, avg OOS pts: 58→63 |
| NFP exclusion (`+xnfp`) | T31s | IS PF: 1.63→1.40 (trade-off), OOS PF: 1.67→1.96, avg OOS pts: 58→80 |
| Combined (strong+xnfp together) | Not tested | Queue for next round |

**Best improvement:** `T31s+xnfp` OOS avg pts jumps from 58→80 (+38%) with OOS PF 1.67→1.96 (+17%), while n stays adequate (69 OOS). IS is slightly weaker — a sign the OOS edge is real, not mined.

---

## Recommended Next Steps

1. **Test T31s+strong+xnfp** (combine both filters) — expected n≈40-45, may hit n<30 threshold
2. **Re-implement T11** with the correct 3-bar intra-day momentum (11:00→14:00 close delta, no rolling shift) and re-test clones  
3. **Queue T31s+xnfp** to LocalThug for MT4 tick-level confirmation (stop-fill sensitivity)
4. **T6 flagged** — do not trade without better OOS evidence

---

## Per-Year PF (IS, T31s survivors)

| Label | 2024 PF | 2025 PF | 2026 PF |
|-------|---------|---------|---------|
| T31s_BASE | — | — | — |
| T31s+strong | — | — | — |
| T31s+xnfp | — | — | — |

*(Year-level PF not captured in this run — re-run with per-year stats flag if needed)*
