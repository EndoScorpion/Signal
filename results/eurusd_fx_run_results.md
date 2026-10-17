# EURUSD H1 FX Backtest Results
**Engine:** w2_node_fx.js | **Data:** FXOpen ECN, 2024-12 to 2026-10 (22 months) | **Run:** 2026-10-17

## Summary
**0 winners** from 6,714 backtests across H1/M120/H4 timeframes. No strategy passes all 6 `passes()` criteria.

### passes() filter
`t>=10 && wp>=55 && a>0 && ht>=3 && hwp>=50 && ha>=0`

## Near-miss Table (top Gen A signals, EURUSD H1)
| Signal | t | wp% | a (net%) | ht | hwp% | ha | Blocking |
|--------|---|-----|----------|----|------|----|----------|
| RSI(7,25→55) | 193 | 62.7 | −0.141 | 87 | 65.5 | −1.901 | a<0, ha<0 |
| RSI(14,30→70) | 53 | 62.3 | +0.053 | 16 | 50.0 | −5.336 | ha<0 |
| T3 hold=6h | 216 | 52.8 | −6.062 | 83 | 50.6 | −0.576 | wp<55, a<0 |
| STD(5,3,20→75) | 378 | 64.3 | −6.902 | 168 | 59.5 | −4.291 | a<0, ha<0 |

## Root Causes
1. **Data window too short**: 22 months → hold-out ~7 months → ha<0 for all strategies (insufficient OOS data)
2. **ECN costs absorb edge**: RT cost ≈ 0.009% per trade vs typical H1 moves; only high-WR systems survive
3. **T3 (London divergence) not viable 2024–2026**: tops out at ~53% WR in this data window
4. **T7 (ATR breakout)**: 0 qualifying entries — ATR compression + breakout rarely co-occur at 13–17 UTC in this period

## Signals Tested
- RSI (n=7,10,14,21; lo=25-35, hi=55-70)
- CCI (n=10,14; lo=80-100)
- STD (n=5,8; s=3; lo=20-22, hi=75)
- T3 (London session divergence, n=1-3, dow variants, hold=4/8)
- T7 (ATR compression breakout, atr_pct=70-90%, rk_n=20-30, brk_n=5-20)
- All standard BASE/BASE2/BASE3/BASE4 seeds + MIX/EXITS/REGS

## Costs Applied (FXOpen ECN, forex class)
`{comm:0.004%, spread:0.001%, swap:0.0001%, tax:24%}`

## Engine Status
- w2_node_fx.js: fully operational (eval-scope injection fix applied)
- T3 signal: 479 H1 entries generated correctly
- T7 signal: 0 entries (condition too restrictive for this data)
- Generation: A→B→C→D complete, 6,714 total backtests

## Recommendation
EURUSD H1 null result is a valid finding. To proceed:
1. Extend data window to 3-5 years (need FXOpen tick/bar export via RC or broker API)
2. Test M15/M30 timeframes (more trades, higher signal frequency)
3. Apply confounding-factor filters (COT, session timing, news exclusion) per [[confounding-factors]]
4. Consider longer hold periods (H4/D1) to reduce cost drag

*Past results are not advice.*
