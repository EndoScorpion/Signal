# Win Logic Branch Naming Convention (adopted 2026-10-18)

Format: `[entry_type]-[trigger]-[session]-[code]+[filters]`

## Keys
- Entry type: `MKT` = market order, `SS` = sell stop, `LMT` = limit
- Trigger: `07/08/14/20` = entry hour UTC, `PT` = patient trigger, `MOM3H` = 3-bar momentum
- Session: `LO` = London Open, `NY` = NY session, `LN` = London→NY boundary
- Filters: `NG` = no_gap_up, `XQ2` = exclude Q2

## Current branch names
| Code | Full name |
|------|-----------|
| v2.3 baseline | MKT-07-LO-v23 |
| v2.3 + RSI14<50 | MKT-07-LO-v23+RSI14<50 |
| v2.3 + RSI5<60 | MKT-07-LO-v23+RSI5<60 |
| C64b | MKT-07-LO-C64b |
| C64b excl Q2 | MKT-07-LO-C64b-XQ2 |
| RSI14+no_gap | MKT-07-LO-v23+RSI14+NG |
| v2.4 candidate | MKT-08-LO-v24 |
| E7 base | SS-PT-ATR14-LO-E7 |
| E7 + no_gap (C67 candidate) | SS-PT-ATR14-LO-E7+NG |
| E7 + RSI5<60 | SS-PT-ATR14-LO-E7+RSI5<60 |
| E7 + RSI14<50 | SS-PT-ATR14-LO-E7+RSI14<50 |
| E7 + C64b | SS-PT-ATR14-LO-E7+C64b |
| E7 + C64b excl Q2 | SS-PT-ATR14-LO-E7+C64b-XQ2 |
| E7 + RSI5+NG | SS-PT-ATR14-LO-E7+RSI5+NG |
| E7 + RSI14+NG | SS-PT-ATR14-LO-E7+RSI14+NG |

## C67 candidate (new 2026-10-18)
SS-PT-ATR14-LO-E7+NG: n=30, WR=56.7%, PF=7.54, avg=+0.212%, consistent 2024/25/26 (5.62/11.08/8.24)
Sell-stop entry at 07:00_open minus 0.10xATR14, only on days with no overnight gap up.
First sell-stop variant hitting n>=30 with WR>51%. Needs OOS validation before adoption.

## CLI instructions
- Use these names in all new result files and TEST_LOG entries
- New variants: follow the format above, append +[FILTER] for each additional filter
- Save results to /mnt/project-files/results/ using the branch name in the filename
