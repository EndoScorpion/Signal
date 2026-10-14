# Leaderboard (6 pts commission, charged once = $0.06/0.01 lot = $6.00/1.00 lot; spread 2 (2018) / 3 (2019); swap 0; deposit per report ($20,000 default, $5,000 jobs flagged by dep5000 in filename), 0.01 lot; leverage = MT4 tester account leverage, 1:500 cannot be set in the backtest copy, so it only affects margin, not P/L)

Pass bar: PF >= 1.10 after commission in BOTH 2018 M15 and 2019 M1, and max DD < 5% ($1,000). DD = closed-trade peak-to-trough.

| rank | variant | test | trades | win % | PF | net $ | max DD $ | pass |
|---|---|---|---|---|---|---|---|---|
| 1 | b12_ladder12_g1b | 2018_M15 | 588 | 52.0 | 1.05 | 51 | 319 | no |
| 1 | b12_ladder12_g1b | 2019_M1 | 1053 | 51.9 | 1.04 | 77 | 416 | no |
| 2 | b20legs_g1b | 2018_M15 | - | - | - | - | - | missing |
| 2 | b20legs_g1b | 2019_M1 | 670 | 52.7 | 1.08 | 89 | 271 | no |
| 3 | b12_bracketreg_g1b | 2018_M15 | 380 | 51.8 | 1.04 | 28 | 203 | no |
| 3 | b12_bracketreg_g1b | 2019_M1 | 704 | 51.7 | 1.04 | 44 | 282 | no |
| 4 | b20legs_g1a | 2018_M15 | 365 | 48.2 | 0.89 | -61 | 215 | no |
| 4 | b20legs_g1a | 2019_M1 | 670 | 54.0 | 1.13 | 122 | 187 | no |
| 5 | b12_bracketreg_g1a | 2018_M15 | 380 | 47.6 | 0.87 | -77 | 164 | no |
| 5 | b12_bracketreg_g1a | 2019_M1 | 704 | 53.8 | 1.12 | 120 | 198 | no |
| 6 | b12_ladder12_g1a | 2018_M15 | 588 | 48.1 | 0.89 | -101 | 259 | no |
| 6 | b12_ladder12_g1a | 2019_M1 | 1053 | 53.3 | 1.10 | 144 | 324 | no |

## Single-test results (new naming)
| variant | period | deposit | spread | trades | win % | PF | net $ | max DD $ (%) | note |
|---|---|---|---|---|---|---|---|---|---|
| g2a | 2019 M1 (in-sample) | 10,000 (tester default, NOT the $5,000 job) | 3 | 403 | 57.1 | 1.28 | +147 | 104 (1.0%) | 6 pts once, 0.01 lot; the $5,000 job (b20legs_g1a 2019) is still queued last |

## Data caveats (from hub endos-29)
- EURUSD M1 hole 2021-02-16 to 2021-03-18: 2021 out-of-sample tests run 2021-03-19 to 2022-01-01 (g2a-g2d and b20legs_g1a baseline over the same window).
- 2011 M15 is missing ~3.5 weeks (incl. Aug 8-24); 2012 M15 missing ~2 weeks; 2019 M1 missing Jan 3-11.
- No history Sep 28 2022 - Aug 28 2025.
- g2a 2019 score independently confirmed from raw prices: +$146.82 over 403 trades.
