# MQ4 EURUSD scalper family: structure and break-even (from the 4 distinct uploaded EAs)
Files: High_Vol_98 (the ssr_ copy is byte-identical), Strong_2010b, Strong_2012a, strong_2011b. UTF-16 source, ~1.5k-3.2k lines each, buy-only, 0.01 lot.

## Common structure
- Entry: BUY at Ask. Hundreds of stacked filters; common core: spread <= 8 pts; M1 SMA(2) slope >= 2 pts (price rising);
  M15 Stoch(10,3,3) at shift 2 <= 80; slope/stoch ratios (SP) between ~0.33 and 5 across M1/M5/M15; no entries Fri after 19h,
  none after 22h (swap avoidance). Variants differ in extra slope/ratio/range filters.
- Exit: TP = +8 points, SL = -290 points. Commission noted in code as 6 points (May 2019). SwapHelp raises TP to cover swap if held over rollover.
- Account lock: AccountNumber()!=892151 -> EA does nothing (fine for you; remove only on your own account).

## Break-even win rate (TP 8, SL 290, per trade, points)
| commission pts | win | loss | break-even win% |
|--|--|--|--|
| 0 | +8 | -290 | 97.32% |
| 3 | +5 | -293 | 98.32% |
| 6 | +2 | -296 | 99.33% |
| 9 | +-1 | -299 | 100.34% |

Headers claim 98.05-98.60% wins on 215-374 trades, i.e. only ~3-7 losing trades. At 6 pts commission break-even is 99.33%, so the
claimed win rates are NEGATIVE expectancy (about -2.8 pts/trade at 98.4%). They only clear break-even if real commission is ~3 pts or less.
Tiny loss counts make the win% statistically meaningless: one extra stop-out flips the result.

## Not validated
No M1/tick EURUSD data here (proxy blocks FX sources; Alpha Vantage free tier has no long intraday). Need MT4 History Center export (M1, FXOpen ECN).


## FXOpen ECN commission (user-supplied, secondary sources, verify at support.fxopen.com)
Base EUR 3.50/side = EUR 7.00 round turn per 1.00 lot; scales linearly (0.01 lot = EUR 0.07), so in POINTS it is lot-size independent.
1 point (0.00001) on 1 lot = about USD 1, so EUR 7.00 at EURUSD ~1.1 is about 7.7 points round turn.
| tier | commission pts | win (TP 8) | loss (SL 290) | break-even win% |
|--|--|--|--|--|
| EUR 7.00 round-turn (base tier) | 7.7 | +0.3 | -297.7 | 99.90% |
| EUR 5.00 round-turn | 5.5 | +2.5 | -295.5 | 99.16% |
| EUR 3.00 round-turn (best tier, $1.50/side) | 3.3 | +4.7 | -293.3 | 98.42% |
At the base tier an 8-point target nets about 0.3 pts per win, so no realistic win rate pays. Best tier needs large volume. Use --comm 7.7 in fx_scalp_sim.py.


## CORRECTION: official FXOpen ECN FX commission (user pasted fxopen.com page, 9 Oct 2026)
Per side per 1.00 lot, in BASE currency (EUR for EURUSD): below $1,000 = 3.50; $1,000-$25,000 = 2.50; $25k-$250k = 1.80; over $250k = 1.50.
Tier depends on account balance (and 30-day volume for discounts). TickTrader limit orders are cheaper ($2.00 at $1k-25k). Swap: see MT4 Specification (swap long/short).
Round turn in points (1 pt ~ USD 1 per lot; EURUSD ~1.1 assumed):
| tier | round turn | points | net per win (TP 8) | break-even win% (SL 290) |
|--|--|--|--|--|
| Below $1,000: 3.50/side | EUR 7.00 | 7.7 | +0.3 | 99.90% |
| $1,000-$25,000: 2.50/side | EUR 5.00 | 5.5 | +2.5 | 99.16% |
| $25k-$250k: 1.80/side | EUR 3.60 | 4.0 | +4.0 | 98.64% |
| TickTrader limit orders, $1k-25k: 2.00/side | EUR 4.00 | 4.4 | +3.6 | 98.79% |
