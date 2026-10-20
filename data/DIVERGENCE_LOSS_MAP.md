# Divergence / convergence loss map (auto-generated)

Base trades mapped: 3479, total -97872 pts, average -28.1 pts/trade (pts = profit / lots). Negative avg = loss bucket; skipping it is a loss-prevention rule candidate.

## ssr

| state | trades | win % | avg pts | total pts |
|---|---|---|---|---|
| opposite | 1666 | 46.1 | -31.9 | -53184 |
| extreme | 531 | 43.7 | -46.6 | -24727 |
| aligned | 1242 | 48.3 | -18.7 | -23196 |
| n/a | 40 | 65.0 | 80.9 | 3234 |

## stack

| state | trades | win % | avg pts | total pts |
|---|---|---|---|---|
| stack_diverging | 1671 | 44.6 | -40.7 | -67962 |
| stack_converging | 1808 | 48.7 | -16.5 | -29911 |

## gap

| state | trades | win % | avg pts | total pts |
|---|---|---|---|---|
| gap_diverging | 1675 | 43.3 | -48.5 | -81159 |
| gap_converging | 1804 | 49.9 | -9.3 | -16714 |

## flat

| state | trades | win % | avg pts | total pts |
|---|---|---|---|---|
| moving_fast | 2839 | 46.8 | -27.7 | -78612 |
| flat_fast | 640 | 46.4 | -30.1 | -19260 |

## stack_change

| state | trades | win % | avg pts | total pts |
|---|---|---|---|---|
| stack_sd_rising>10% | 1269 | 43.8 | -45.7 | -57989 |
| stack_sd_falling>10% | 1645 | 48.3 | -18.6 | -30606 |
| stack_sd_steady | 565 | 48.7 | -16.4 | -9278 |

## stack_level

| state | trades | win % | avg pts | total pts |
|---|---|---|---|---|
| stack_sd_mid | 1977 | 46.4 | -30.2 | -59750 |
| stack_sd_high | 1033 | 46.0 | -32.7 | -33768 |
| stack_sd_low | 469 | 49.9 | -9.3 | -4354 |

## combo

| state | trades | win % | avg pts | total pts |
|---|---|---|---|---|
| opposite|stack_diverging | 835 | 42.2 | -55.6 | -46404 |
| extreme|stack_converging | 284 | 43.3 | -48.8 | -13852 |
| aligned|stack_diverging | 573 | 48.0 | -20.5 | -11740 |
| aligned|stack_converging | 669 | 48.6 | -17.1 | -11456 |
| extreme|stack_diverging | 247 | 44.1 | -44.0 | -10875 |
| opposite|stack_converging | 831 | 50.1 | -8.2 | -6780 |
| n/a|stack_diverging | 16 | 62.5 | 66.1 | 1058 |
| n/a|stack_converging | 24 | 66.7 | 90.7 | 2177 |

## Biggest loss buckets (n >= 100)

- gap = gap_diverging: 1675 trades, -81159 pts
- flat = moving_fast: 2839 trades, -78612 pts
- stack = stack_diverging: 1671 trades, -67962 pts
- stack_level = stack_sd_mid: 1977 trades, -59750 pts
- stack_change = stack_sd_rising>10%: 1269 trades, -57989 pts
