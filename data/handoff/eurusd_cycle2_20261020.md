# EUR/USD FXOpen ECN — improvement cycle 2 (2026-10-20)

LOCAL ONLY: this file holds win logic, so don't commit it. Research only: no orders, no MT4, MT4_PAUSE still in place. All results are net of 8 pts per trade (COST 0.00008, same as cycle 1) and given in points; at 0.1 lot, 1 pt = $0.10. Past results are not advice.

## Data and how this run differs from cycle 1
- `eurusd_fxopen_h1.csv` and `eurusd_twelvedata_h1_2020_2026.csv` are **not on this PC**, and neither is the cycle-1 report. I rebuilt the engine from `backups/clone_gen13_20261019.txt` (same indicators, same `run()` exit logic, same COST).
- History used: `Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server\EURUSD60.hst` (the clean aligned-v2 rebuild of the FXOpen M1 zip, ~6,230 bars/yr, no holes), converted from server time (UTC+2/+3 on US DST) to UTC. Clock check: on NFP Fridays the biggest H1 range is at 12:00/13:00 UTC, which is correct.
- I didn't use `hst_out\cloud_export\EURUSD_H1_FXOpenEU-ECN.csv`: it has no 2023–2024 data, only part of 2020 and 2025, and its "time_utc" column is really server time.
- Split: **IS = FXOpen 2024–26** (same as cycle 1). **OOS = FXOpen 2020–23** (cycle 1 used TwelveData for these years). **EXT = FXOpen 2011–19** (extra years no one has tuned on).
- Stack v2 = G11-3 (Fri 14:00 short, day move > 0.3×ATR, MMR ≥ −1, Gate A, skips the first Friday, exits 22) + Mon17x22 + T82 (exits 21). No stops, one trade at a time per leg.

## Baseline: Stack v2 does not hold up out of sample on FXOpen
| Segment | n | WR% | PF | avg pts | net pts | max DD pts | PF per year |
|---|---|---|---|---|---|---|---|
| IS 2024–26 | 111 | — | **2.90** | +60.2 | +6,682 | 737 | — |
| OOS 2020–23 | 135 | 49.6 | **0.71** | −24.6 | −3,325 | 4,316 | 0.78 / 0.49 / 0.93 / 0.77 |
| EXT 2011–19 | 311 | — | 0.99 | — | — | — | — |

By leg, OOS 2020–23:
- G11-3: n=34, WR 35%, PF 0.55. IS: n=34, PF 6.91.
- Mon17: n=72, PF 0.82. IS: n=53, PF 1.57.
- T82: n=29, PF 0.86. IS: n=24, PF 2.20.

IS trade counts are close to cycle 1 (Mon17 had 57 in IS there), so the IS rebuild matches. The OOS failure therefore comes from the data source (TwelveData vs FXOpen for 2020–23), not from the engine.

**Clock-shift test:** I moved the FXOpen clock by −2, −1, +1 and +2 h. OOS PF ranged from 0.66 to 0.95, so a clock offset in the TwelveData file does not explain cycle 1's PF 1.75. The likeliest cause is that the edge exists only in 2024–26 (and 2013–16).

## Cycle-2 tests (each compared with the baseline; all REJECTED, because at least one OOS year has PF < 1)
| Test | OOS n | WR% | PF | avg pts | max DD | OOS PF per year | IS PF | EXT PF |
|---|---|---|---|---|---|---|---|---|
| Baseline | 135 | 49.6 | 0.71 | −24.6 | 4,316 | .78/.49/.93/.77 | 2.90 | 0.99 |
| 1. Split exit (half at 21, half at 22) | 135 | 49.6 | 0.70 | −26.2 | 4,492 | .84/.50/.77/.82 | 2.85 | 0.91 |
| 2a. Breakeven stop after +0.5×ATR | 135 | 35.6 | 0.79 | −14.3 | 2,932 | .85/.42/1.54/.75 | 2.55 | 1.12 |
| 2b. Catastrophic stop 2.5×ATR | 135 | 49.6 | 0.77 | −18.4 | 3,649 | .84/.61/.80/.88 | 2.70 | 0.94 |
| 2c. Breakeven + catastrophic | 135 | 35.6 | **0.84** | −10.2 | **2,574** | .93/.57/1.02/.87 | 2.33 | 1.01 |
| 2d. Skip when the bar before entry has range > 1.5×ATR | 108 | 48.1 | 0.59 | −33.0 | 4,086 | .86/.34/.63/.81 | 2.00 | 1.08 |
| 2e. Skip CPI Fridays | 134 | 50.0 | 0.72 | −24.4 | 4,255 | .80/.49/.93/.77 | 2.92 | 1.01 |
| 2f. Skip Fridays in FOMC weeks | 132 | 49.2 | 0.71 | −24.9 | 4,577 | .91/.45/.93/.74 | 2.81 | 0.98 |
| 2g. Skip holiday-adjacent days | 106 | 46.2 | 0.62 | −36.6 | 4,426 | .71/.58/.84/.44 | 2.50 | 0.93 |
| 2h. Skip CPI + FOMC + holiday days | 103 | 46.6 | 0.63 | −35.8 | 4,532 | .91/.53/.84/.44 | 2.52 | 0.90 |
| 3. G11 threshold 0.25 / 0.35 / 0.40 | 135 | 49.6 | 0.71 | −24.6 | 4,316 | same | 2.90 | 0.98–0.99 |
| 4a. Size by ATR percentile tiers (1.25 / 1 / 0.75) | 135 | 49.6 | 0.72 | −24.2 | 4,520 | .77/.49/.94/.81 | 2.90 (DD 652) | 1.01 |
| 4b. Half size when ATR percentile > 0.8 | 135 | 49.6 | 0.73 | −22.0 | 4,332 | .70/.53/.86/.95 | 2.90 (DD 657) | 0.96 |
| 4c. Inverse-ATR size, clipped 0.5–1.5 | 135 | 49.6 | 0.70 | −25.8 | 4,700 | .61/.51/1.04/.82 | 2.95 (DD 582) | 1.03 |

Notes:
- **Test 3:** the threshold doesn't matter. In 2020–23 there are only 0–3 Fridays with a day move between 0.25 and 0.4×ATR, and MMR and Gate A filter them out anyway. G11 behaves identically at every threshold tested.
- **Test 2c:** this is the only change that helps in every segment (OOS PF +0.13, OOS max DD −40%, EXT 0.99 → 1.01). It costs IS PF (2.90 → 2.33) and still fails the rule.
- **Test 4:** sizing by volatility lowers IS max DD by 12–21% but does nothing for OOS.
- The CPI and FOMC dates are typed in from memory and are approximate; check them against an official calendar before relying on them.

## 5. Rolling 12-month PF of Stack v2 (FXOpen 2011–2026, monthly steps, 179 windows)
- Minimum 0.41 (window ending 2019-12). Median **0.85**. **55% of windows are below PF 1.0** and 59% are below 1.3.
- Pattern by period:
  - 2013-01 to 2014-12: about 1.7–4.7 (good)
  - 2015-H1: under 1
  - 2016: about 1.7–2.8 (good)
  - **2017-03 to 2023-12: under 1 the whole time (about 7 years)**
  - 2024-03 to now: about 1.8–5.4 (good)
- Latest windows: 2026-08 = 1.91, 2026-09 = 1.79, 2026-10 = 2.11. The good run is fading from its 2025-09 peak of 5.42.
- Monthly series saved to `data\eurusd_cycle2_rolling12m.csv`.

## Verdict
- **Nothing beat the baseline in a way that passes the rules. This is a plateau, and more than that: the baseline itself fails on FXOpen 2020–23 and is flat on 2011–19.**
- Stack v2 works in some regimes and not others. It switched on in 2024 and was switched off from 2017 to 2023.
- Cycle 1's TwelveData OOS pass (PF 1.75) is not confirmed on broker data. Before any MT4 run of Stack v2 or Stack A, I'd treat the TwelveData result as unverified.
- MT4 (nomem6_026, 029 and 033, run on the same FXOpen history) should show the same 2020–23 losses. Use it as a cross-check, not as an approval.

## New theory ideas (not tested yet)
1. **Regime switch:** run the stack only when its own trailing 12-month PF is above 1.3, or when the SMA2400 regime is in favour (that regime lead beat the base 4/4 in unseen years). Test this walk-forward on 2011–2026 with no lookahead. This is the most promising idea, because the rolling-PF series has long stretches in one state.
2. **Find what 2013–14, 2016 and 2024–26 have in common.** Compare EUR/USD trend direction, ECB vs Fed rate spread, realised vol and Hurst (ChaosRegime.mqh) between the good windows and the bad 2017–23 window. If one variable separates them, use it as the gate.
3. **Mirror the stack in 2017–23:** take the opposite side of G11-3 (WR 35% OOS). Only worth doing if the regime variable from idea 2 predicts when to flip; otherwise it's curve-fitting.
4. **Keep breakeven + catastrophic stop (2c) as a module that only lowers drawdown.** It was the only change that helped in all three segments. Re-test it on top of whatever regime gate survives.
5. **Data hygiene:** put the TwelveData file on this PC (or in data\import) and diff its 2020–23 Fridays against FXOpen bar by bar, to find why the two sources disagree.

## Files (local)
- Engine: `data\eurusd_cycle2_engine.py`
- Raw output: `data\eurusd_cycle2_output.txt`
- Rolling 12-month PF: `data\eurusd_cycle2_rolling12m.csv`
- Text copy of this report: `backups\eurusd_cycle2_20261020.txt`
- Text copy of the engine: `backups\eurusd_cycle2_engine_20261020.txt`
