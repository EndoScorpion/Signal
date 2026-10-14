# Gate pass rates (M15, clean history EURUSD15.hst, Point=1e-05)

Computed at the last closed bar (shift 1) of each M15 bar. NaN/undefined counts as FAIL. Verdict: INERT >97% or <3%, TIGHT <15%, USEFUL 15-85%, LOOSE >85%.
Script: gate_pass_rates.py (same folder). ADX = Wilder smoothing (MT4 iADX near-identical). Lyapunov sampled every 10th bar.

## Katz FD (64)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% FdMax 1.5 |
|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 1.324 | 1.494 | 1.673 | 1.902 | 2.32 | 26.0 |
| 2013 | 24592 | 1.315 | 1.505 | 1.692 | 1.927 | 2.34 | 24.2 |
| 2014 | 24586 | 1.322 | 1.488 | 1.672 | 1.915 | 2.355 | 26.8 |
| 2015 | 24776 | 1.318 | 1.497 | 1.679 | 1.904 | 2.301 | 25.5 |
| 2016 | 24898 | 1.327 | 1.518 | 1.711 | 1.959 | 2.349 | 22.7 |
| 2018 | 24844 | 1.336 | 1.497 | 1.67 | 1.901 | 2.294 | 25.5 |
| 2023 | 24826 | 1.3 | 1.486 | 1.673 | 1.917 | 2.337 | 26.7 |
| 2024 | 24952 | 1.317 | 1.495 | 1.681 | 1.906 | 2.299 | 25.8 |
| ALL | 198193 | 1.32 | 1.497 | 1.681 | 1.917 | 2.324 | 25.4 |

Verdicts:

- FdMax 1.5: pooled 25.4% -> **USEFUL**; per-year 22.7..26.8%

## Lyapunov (every 10th bar)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% LyapMax 0.15 |
|---|---|---|---|---|---|---|---|
| 2010 | 2472 | 0.2403 | 0.2734 | 0.2955 | 0.3173 | 0.3466 | 0.0 |
| 2013 | 2460 | 0.2377 | 0.2701 | 0.2914 | 0.3136 | 0.345 | 0.0 |
| 2014 | 2459 | 0.2362 | 0.2678 | 0.2909 | 0.3119 | 0.341 | 0.0 |
| 2015 | 2478 | 0.2379 | 0.2714 | 0.2952 | 0.3176 | 0.3483 | 0.0 |
| 2016 | 2490 | 0.2303 | 0.2676 | 0.291 | 0.3117 | 0.3419 | 0.0 |
| 2018 | 2485 | 0.236 | 0.2679 | 0.2903 | 0.3107 | 0.3397 | 0.0 |
| 2023 | 2483 | 0.2285 | 0.2647 | 0.2878 | 0.3091 | 0.3401 | 0.0 |
| 2024 | 2496 | 0.2294 | 0.2654 | 0.2898 | 0.312 | 0.343 | 0.0 |
| ALL | 19823 | 0.2348 | 0.2685 | 0.2914 | 0.313 | 0.344 | 0.0 |

Verdicts:

- LyapMax 0.15: pooled 0.0% -> **INERT**; per-year 0.0..0.0%

## Hurst R/S 128

| year | n | p5 | p25 | p50 | p75 | p95 | pass% HurstMax 0.5 |
|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 0.4685 | 0.5441 | 0.5945 | 0.6398 | 0.7039 | 11.0 |
| 2013 | 24592 | 0.4617 | 0.5314 | 0.5804 | 0.6288 | 0.6948 | 13.7 |
| 2014 | 24586 | 0.4572 | 0.5302 | 0.5763 | 0.6235 | 0.6891 | 13.5 |
| 2015 | 24776 | 0.4731 | 0.5406 | 0.5865 | 0.6326 | 0.6951 | 10.1 |
| 2016 | 24898 | 0.4452 | 0.5222 | 0.5766 | 0.6291 | 0.7035 | 17.2 |
| 2018 | 24844 | 0.4628 | 0.5395 | 0.5897 | 0.6382 | 0.7014 | 11.6 |
| 2023 | 24826 | 0.4492 | 0.5273 | 0.5846 | 0.6412 | 0.7192 | 15.8 |
| 2024 | 24952 | 0.4654 | 0.5358 | 0.5886 | 0.6385 | 0.7144 | 12.7 |
| ALL | 198193 | 0.4597 | 0.5339 | 0.5847 | 0.634 | 0.7032 | 13.2 |

Verdicts:

- HurstMax 0.5: pooled 13.2% -> **TIGHT**; per-year 10.1..17.2%

## Vol-of-vol

| year | n | p5 | p25 | p50 | p75 | p95 | pass% VovMax 0.35 |
|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 0.01943 | 0.0437 | 0.07562 | 0.1263 | 0.2507 | 98.5 |
| 2013 | 24592 | 0.01797 | 0.04613 | 0.08621 | 0.1524 | 0.2996 | 97.1 |
| 2014 | 24586 | 0.01871 | 0.04654 | 0.0867 | 0.1569 | 0.3199 | 96.2 |
| 2015 | 24776 | 0.01878 | 0.0455 | 0.07985 | 0.1417 | 0.2848 | 97.5 |
| 2016 | 24898 | 0.01815 | 0.04437 | 0.07965 | 0.1373 | 0.2794 | 97.7 |
| 2018 | 24844 | 0.01995 | 0.04609 | 0.08087 | 0.1421 | 0.2712 | 98.0 |
| 2023 | 24826 | 0.01871 | 0.04645 | 0.08604 | 0.1514 | 0.2861 | 97.5 |
| 2024 | 24952 | 0.01861 | 0.0459 | 0.08315 | 0.1475 | 0.2985 | 96.9 |
| ALL | 198193 | 0.01879 | 0.04554 | 0.08203 | 0.1442 | 0.2869 | 97.4 |

Verdicts:

- VovMax 0.35: pooled 97.4% -> **INERT**; per-year 96.2..98.5%

## ADX(14)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% AdxMax 25 (<=) | pass% AdxMin 20 (>=) |
|---|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 12.18 | 17.85 | 24.07 | 32.39 | 47.16 | 53.7 | 65.9 |
| 2013 | 24592 | 11.94 | 18.05 | 23.63 | 31.16 | 46.01 | 55.6 | 66.4 |
| 2014 | 24586 | 11.25 | 17.41 | 23.39 | 31.36 | 46.71 | 55.9 | 64.2 |
| 2015 | 24776 | 11.9 | 17.66 | 23.29 | 31.43 | 46.43 | 56.4 | 64.1 |
| 2016 | 24898 | 11.24 | 16.72 | 22.36 | 30.62 | 45.31 | 59.5 | 59.5 |
| 2018 | 24844 | 12.43 | 17.97 | 24.16 | 31.47 | 44.71 | 53.3 | 66.6 |
| 2023 | 24826 | 11.65 | 17.38 | 23.05 | 31.29 | 46.24 | 57.4 | 63.3 |
| 2024 | 24952 | 11.77 | 16.91 | 22.44 | 30.07 | 43.49 | 60.2 | 60.8 |
| ALL | 198193 | 11.77 | 17.46 | 23.3 | 31.21 | 45.82 | 56.5 | 63.8 |

Verdicts:

- AdxMax 25 (<=): pooled 56.5% -> **USEFUL**; per-year 53.3..60.2%
- AdxMin 20 (>=): pooled 63.8% -> **USEFUL**; per-year 59.5..66.6%

## ER20

| year | n | p5 | p25 | p50 | p75 | p95 | pass% ErMax 0.25 (<=) | pass% ErMin 0.30 (>=) | pass% ErMin 0.30 and ErMax 0.25 together |
|---|---|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 0.01874 | 0.09346 | 0.1985 | 0.3333 | 0.5294 | 60.6 | 30.6 | 0.0 |
| 2013 | 24592 | 0.01802 | 0.09091 | 0.189 | 0.3166 | 0.5222 | 62.9 | 27.8 | 0.0 |
| 2014 | 24586 | 0.01782 | 0.0897 | 0.1885 | 0.3226 | 0.5207 | 62.6 | 28.6 | 0.0 |
| 2015 | 24776 | 0.01904 | 0.09517 | 0.1973 | 0.326 | 0.5228 | 61.3 | 29.3 | 0.0 |
| 2016 | 24898 | 0.01769 | 0.08768 | 0.1848 | 0.3085 | 0.5223 | 64.3 | 26.4 | 0.0 |
| 2018 | 24844 | 0.019 | 0.09427 | 0.1977 | 0.3293 | 0.528 | 61.2 | 29.7 | 0.0 |
| 2023 | 24826 | 0.01919 | 0.09638 | 0.2009 | 0.3342 | 0.5511 | 60.1 | 30.7 | 0.0 |
| 2024 | 24952 | 0.01845 | 0.09455 | 0.1976 | 0.3292 | 0.544 | 61.2 | 29.6 | 0.0 |
| ALL | 198193 | 0.01852 | 0.0927 | 0.1941 | 0.3251 | 0.5297 | 61.8 | 29.1 | 0.0 |

Verdicts:

- ErMax 0.25 (<=): pooled 61.8% -> **USEFUL**; per-year 60.1..64.3%
- ErMin 0.30 (>=): pooled 29.1% -> **USEFUL**; per-year 26.4..30.7%
- ErMin 0.30 and ErMax 0.25 together: pooled 0.0% -> **INERT**; per-year 0.0..0.0%

## Slope-stack SD (pts/bar)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% SlopeStackSdMax 3 |
|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 3.272 | 6.037 | 9.147 | 13.91 | 25.03 | 3.7 |
| 2013 | 24592 | 1.884 | 3.581 | 5.461 | 8.48 | 16.84 | 16.8 |
| 2014 | 24586 | 1.239 | 2.481 | 4.07 | 6.612 | 13.36 | 33.7 |
| 2015 | 24776 | 2.309 | 4.484 | 7.074 | 11.15 | 21.62 | 10.3 |
| 2016 | 24898 | 1.69 | 3.137 | 4.944 | 7.813 | 15.84 | 22.9 |
| 2018 | 24844 | 1.805 | 3.313 | 5.044 | 7.663 | 13.71 | 20.3 |
| 2023 | 24826 | 1.596 | 2.959 | 4.466 | 6.886 | 13.43 | 25.8 |
| 2024 | 24952 | 1.186 | 2.199 | 3.453 | 5.46 | 10.94 | 42.0 |
| ALL | 198193 | 1.61 | 3.223 | 5.223 | 8.528 | 17.52 | 21.9 |

Verdicts:

- SlopeStackSdMax 3: pooled 21.9% -> **USEFUL**; per-year 3.7..42.0%

## SMA20 slope SD 20 bars (pts/bar)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% SlopeSdMax 12 |
|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 3.944 | 6.453 | 9.426 | 13.46 | 22.6 | 67.2 |
| 2013 | 24592 | 2.163 | 3.753 | 5.583 | 8.426 | 16.26 | 89.1 |
| 2014 | 24586 | 1.335 | 2.607 | 4.181 | 6.611 | 12.6 | 94.3 |
| 2015 | 24776 | 2.761 | 4.739 | 7.201 | 10.97 | 20.53 | 79.4 |
| 2016 | 24898 | 1.978 | 3.402 | 5.112 | 7.619 | 14.78 | 91.5 |
| 2018 | 24844 | 2.011 | 3.619 | 5.219 | 7.609 | 12.73 | 93.7 |
| 2023 | 24826 | 1.764 | 2.999 | 4.471 | 6.686 | 12.46 | 94.4 |
| 2024 | 24952 | 1.348 | 2.309 | 3.456 | 5.498 | 10.32 | 96.8 |
| ALL | 198193 | 1.796 | 3.409 | 5.35 | 8.434 | 16.49 | 88.3 |

Verdicts:

- SlopeSdMax 12: pooled 88.3% -> **LOOSE**; per-year 67.2..96.8%

## SSR slope(SMA20)/slope(SMA200)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% inside 0.2..5 (SsrMode1) | pass% outside band (SsrMode2; NaN fails) |
|---|---|---|---|---|---|---|---|---|
| 2010 | 24719 | -10 | -1.627 | 0.6223 | 3.376 | 10 | 38.1 | 61.2 |
| 2013 | 24592 | -10 | -1.616 | 0.5082 | 3.427 | 10 | 35.2 | 63.8 |
| 2014 | 24586 | -10 | -1.483 | 0.5489 | 3.561 | 10 | 35.4 | 63.0 |
| 2015 | 24776 | -10 | -1.44 | 0.6462 | 3.333 | 10 | 38.1 | 61.2 |
| 2016 | 24898 | -10 | -1.604 | 0.6231 | 3.387 | 10 | 37.0 | 62.0 |
| 2018 | 24844 | -10 | -1.569 | 0.6864 | 3.192 | 10 | 39.2 | 59.7 |
| 2023 | 24826 | -10 | -1.745 | 0.4701 | 3.3 | 10 | 35.6 | 63.2 |
| 2024 | 24952 | -10 | -1.639 | 0.6061 | 3.524 | 10 | 35.2 | 63.5 |
| ALL | 198193 | -10 | -1.589 | 0.5873 | 3.376 | 10 | 36.7 | 62.2 |

Verdicts:

- inside 0.2..5 (SsrMode1): pooled 36.7% -> **USEFUL**; per-year 35.2..39.2%
- outside band (SsrMode2; NaN fails): pooled 62.2% -> **USEFUL**; per-year 59.7..63.8%

## OU half-life (bars; 9999 = no reversion)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% 4..40 | pass% 2..20 |
|---|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 4.439 | 8.958 | 16.17 | 35.41 | 9999 | 74.2 | 57.5 |
| 2013 | 24592 | 3.295 | 7.258 | 12.84 | 26.28 | 304 | 75.9 | 66.4 |
| 2014 | 24586 | 3.405 | 6.997 | 13.17 | 29.03 | 284.7 | 74.3 | 63.9 |
| 2015 | 24776 | 4.168 | 7.99 | 13.64 | 28.36 | 374 | 78.2 | 64.8 |
| 2016 | 24898 | 3.271 | 6.697 | 12.65 | 26.25 | 705.1 | 75.0 | 65.6 |
| 2018 | 24844 | 4.222 | 8.531 | 15.12 | 30.57 | 353.6 | 77.3 | 61.1 |
| 2023 | 24826 | 3.54 | 7.704 | 14.38 | 31.16 | 9999 | 73.0 | 61.9 |
| 2024 | 24952 | 3.909 | 7.345 | 13.07 | 26.95 | 340.9 | 77.8 | 66.4 |
| ALL | 198193 | 3.759 | 7.64 | 13.82 | 29.17 | 530.1 | 75.7 | 63.5 |

Verdicts:

- 4..40: pooled 75.7% -> **USEFUL**; per-year 73.0..78.2%
- 2..20: pooled 63.5% -> **USEFUL**; per-year 57.5..66.4%

## Lag-1 autocorr 60 returns

| year | n | p5 | p25 | p50 | p75 | p95 | pass% AcMax 0 as queued (EA: guard is >0, so gate OFF) | pass% hypothetical ac<=0 |
|---|---|---|---|---|---|---|---|---|
| 2010 | 24719 | -0.2547 | -0.1116 | -0.02169 | 0.07794 | 0.2282 | 100.0 | 56.0 |
| 2013 | 24592 | -0.2922 | -0.1495 | -0.04378 | 0.07179 | 0.2369 | 100.0 | 60.3 |
| 2014 | 24586 | -0.3067 | -0.1351 | -0.02684 | 0.07229 | 0.23 | 100.0 | 57.0 |
| 2015 | 24776 | -0.2802 | -0.1325 | -0.03715 | 0.06631 | 0.2006 | 100.0 | 59.9 |
| 2016 | 24898 | -0.3199 | -0.1576 | -0.04885 | 0.06069 | 0.2427 | 100.0 | 61.9 |
| 2018 | 24844 | -0.2708 | -0.121 | -0.02347 | 0.06843 | 0.2057 | 100.0 | 56.5 |
| 2023 | 24826 | -0.3141 | -0.1457 | -0.0313 | 0.08396 | 0.2332 | 100.0 | 57.2 |
| 2024 | 24952 | -0.2675 | -0.1256 | -0.02253 | 0.08587 | 0.241 | 100.0 | 55.6 |
| ALL | 198193 | -0.289 | -0.1346 | -0.0316 | 0.07315 | 0.2284 | 100.0 | 58.0 |

Verdicts:

- AcMax 0 as queued (EA: guard is >0, so gate OFF): pooled 100.0% -> **INERT**; per-year 100.0..100.0%
- hypothetical ac<=0: pooled 58.0% -> **USEFUL**; per-year 55.6..61.9%

## Rolling return SD 20 (pts)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% RvolNow<=29.6 | pass% RvolNow<=45.6 |
|---|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 39.11 | 59.18 | 80.54 | 106.4 | 156.5 | 1.0 | 10.0 |
| 2013 | 24592 | 21.28 | 33.34 | 48.3 | 70.64 | 115.5 | 17.8 | 46.1 |
| 2014 | 24586 | 13.32 | 23.14 | 35.29 | 53.74 | 93.92 | 39.2 | 66.4 |
| 2015 | 24776 | 26.11 | 41.98 | 61.46 | 87.74 | 141.9 | 8.1 | 29.7 |
| 2016 | 24898 | 20.25 | 31.46 | 44.27 | 64.03 | 109.2 | 20.9 | 52.4 |
| 2018 | 24844 | 18.89 | 30.91 | 45.47 | 61.75 | 93.12 | 22.0 | 50.2 |
| 2023 | 24826 | 17.05 | 25.95 | 38.01 | 53.99 | 94.24 | 33.5 | 63.2 |
| 2024 | 24952 | 12.93 | 19.69 | 29.23 | 43.06 | 75.89 | 50.9 | 77.8 |
| ALL | 198193 | 17.09 | 30.07 | 45.95 | 69.08 | 120.3 | 24.2 | 49.5 |

Verdicts:

- RvolNow<=29.6: pooled 24.2% -> **USEFUL**; per-year 1.0..50.9%
- RvolNow<=45.6: pooled 49.5% -> **USEFUL**; per-year 10.0..77.8%

## ATR14 (pts)

| year | n | p5 | p25 | p50 | p75 | p95 | pass% cap 48 | pass% cap 60 | pass% cap 90 | pass% cap 120 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2010 | 24719 | 61.43 | 89.57 | 124 | 162.1 | 231.3 | 0.9 | 4.3 | 25.3 | 47.2 |
| 2013 | 24592 | 35.07 | 51.71 | 73.64 | 106.9 | 162.6 | 19.7 | 35.7 | 64.2 | 82.1 |
| 2014 | 24586 | 20.86 | 35.57 | 54.64 | 80.21 | 134.4 | 41.9 | 55.9 | 80.8 | 92.6 |
| 2015 | 24776 | 41 | 63.21 | 95.21 | 137 | 210.5 | 10.1 | 22.0 | 46.0 | 65.8 |
| 2016 | 24898 | 34 | 50.21 | 70.57 | 99.07 | 160.9 | 22.0 | 37.7 | 68.7 | 85.9 |
| 2018 | 24844 | 33 | 48.21 | 73.14 | 97.93 | 136.9 | 24.7 | 37.6 | 67.0 | 89.8 |
| 2023 | 24826 | 26 | 39.71 | 58.79 | 84.43 | 128.9 | 38.1 | 51.2 | 79.1 | 93.0 |
| 2024 | 24952 | 20.14 | 30.5 | 45.21 | 66.21 | 108.2 | 54.0 | 69.2 | 90.1 | 96.8 |
| ALL | 198193 | 27.07 | 46.64 | 71.36 | 105.6 | 176.5 | 26.5 | 39.2 | 65.2 | 81.7 |

Verdicts:

- cap 48: pooled 26.5% -> **USEFUL**; per-year 0.9..54.0%
- cap 60: pooled 39.2% -> **USEFUL**; per-year 4.3..69.2%
- cap 90: pooled 65.2% -> **USEFUL**; per-year 25.3..90.1%
- cap 120: pooled 81.7% -> **USEFUL**; per-year 47.2..96.8%

# Recommended thresholds (target 30-60% pass, EA input units)

- **Katz FD (64)**: <= 1.643 (~45% pass); per-year pass 42..46%
- **Lyapunov (every 10th bar)**: <= 0.2872 (~45% pass); per-year pass 41..49%
- **Hurst R/S 128**: <= 0.5752 (~45% pass); per-year pass 39..49%
- **Vol-of-vol**: <= 0.07354 (~45% pass); per-year pass 43..49%
- **ADX(14)**: AdxMax 22.1 (~45% pass) ; AdxMin 24.6 (~45% pass)
- **ER20**: ErMax 0.172 (~45% pass) ; ErMin 0.217 (~45% pass); keep ErMin < ErMax
- **Slope-stack SD (pts/bar)**: <= 4.769 (~45% pass); per-year pass 15..68%
- **SMA20 slope SD 20 bars (pts/bar)**: <= 4.912 (~45% pass); per-year pass 12..70%
- **SSR slope(SMA20)/slope(SMA200)**: band 0.2..5 -> 36.7% pass
- **SSR slope(SMA20)/slope(SMA200)**: band 0.2..8 -> 43.4% pass
- **SSR slope(SMA20)/slope(SMA200)**: band 0.2..10 -> 54.7% pass
- **SSR slope(SMA20)/slope(SMA200)**: share undefined (|slope SMA200|<0.05 pts/bar, fails): 1.1%
- **OU half-life (bars; 9999 = no reversion)**: 4..40 -> 75.7% pass
- **OU half-life (bars; 9999 = no reversion)**: 2..20 -> 63.5% pass
- **OU half-life (bars; 9999 = no reversion)**: 3..60 -> 85.1% pass
- **OU half-life (bars; 9999 = no reversion)**: 2..100 -> 91.1% pass
- **OU half-life (bars; 9999 = no reversion)**: 2..200 -> 93.4% pass
- **OU half-life (bars; 9999 = no reversion)**: share with no reversion (9999): 4.4%
- **Lag-1 autocorr 60 returns**: AcMax is inactive unless >0 (code line 271); with the guard fixed use AcMax -0.051 (~45% pass); per-year pass 41..50%
- **Rolling return SD 20 (pts)**: CalmRvolMax 42.5 (~45%); 30%: 33.1; 60%: 53.8; per-year pass 7..74%
- **ATR14 (pts)**: AtrCapPts 66.0 (~45%); 30%: 51.1; 60%: 83.1; per-year pass 8..75%

# MQL4 formula review (MR_RegimeSwitch_b61.mq4)

- Line 271 (AcMax): guard is `if(AcMax>0 ...)`, so the queued AcMax 0 (and any negative value) is a no-op; the useful region is negative (median ac -0.03). Change guard to a separate bool or an EMPTY sentinel.
- Lines 43-44/248 (ER): queued ErMin 0.30 with ErMax 0.25 is an empty band (0% pass). Not a formula error but a threshold conflict.
- Line 223-228 (LyapNow): not wrong per Rosenstein, but the mean of ln(d_K/d_0)/K is structurally positive (0.23..0.34 on every bar tested, p5 0.235) because the nearest neighbour is by definition the closest, so LyapMax 0.15 blocks 100% of bars. Also the loop uses x[0..n+K-2], so the newest close (shift 1, x[n+K-1]) is never used (off by one; window is effectively shifts 2..105). No regression over several K steps; single-step horizon is noisy. Gate needs ~0.29 to pass 45%.
- Line 200-209 (HurstNow): R/S is computed on price differences, correct form, but plain R/S is biased high for short n (Anis-Lloyd): a random walk gives ~0.55-0.60 over scales 8..64, so HurstMax 0.5 passes only 13%. Compare to ~0.575 (median 0.585). Min/max start at 0 (includes 0, correct for cumulative deviations).
- Line 220-222 (KatzFd): formula matches Katz (n = steps = 63, d = max distance from first point, L = path length in points). Note the result is ln-sensitive to the max-distance choice; values run 1.3..2.3 (the textbook 1..2 range is exceeded because d/L < 1/n is possible with n=63 when path is much longer than diameter; standard Katz also exceeds 2 in that case). FdMax 1.5 is therefore a trend filter passing 25%.
- Line 199 / 198 (VovNow/RvolAt): correct (population std of 20-bar std over 10 overlapping windows), but overlapping windows make cv small (median 0.08, p95 0.29), so VovMax 0.35 is inert (97% pass).
- Line 197 (ErNow): correct Kaufman ER (net over path, 20 bars).
- Line 229 (SlopeStack): correct, but the SD across slopes in pts/bar is dominated by the fast SMA10/SMA20 slopes; value is volatility-dependent (per-year pass 3.7%..42% at SlopeStackSdMax 3), i.e. it is a volatility gate in disguise. Consider dividing by ATR.
- Line 230 (SsrNow): fine; returns EMPTY (gate fails) when |slope SMA200| < 0.05 pts/bar (1.1% of bars). Sign matters: band 0.2..5 rejects all opposite-slope cases.
- Line 317-319 (OuHalfLife): regression and half-life formula -ln2/ln(1+b) are standard. Window is 100 closes (101 used). Regression on non-demeaned x/Point (~1e5) loses precision slightly but ok in double. b>=0 or b<=-1 returns 9999 (fails both bounds), 4.4% of bars. Dickey-Fuller small-sample bias makes b too negative, so half-lives are biased short; 4..40 passes 76% (LOOSE), 2..20 passes 64%.
- Line 175 (SlopePts) / 195 (SmaSlope) fine. ADX uses MT4 iADX (not reimplemented identically; Wilder used here, differences small).
