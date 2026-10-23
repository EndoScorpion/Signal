# Smoothness vs volatility (auto-generated)

ER20 = smoothness (0 choppy, 1 smooth trend). ATR14 = volatility in points. Pts = profit / 0.16 lot.

| Year | ER20 | ATR14 pts | ATR sd | Base pts |
|---|---|---|---|---|
| 2010 | 0.227 | 131.4 | 52.4 | -3757 |
| 2011 | 0.226 | 143.9 | 61.3 |  |
| 2012 | 0.228 | 94.1 | 42.3 |  |
| 2013 | 0.221 | 80.9 | 41.1 | -13803 |
| 2014 | 0.212 | 60.8 | 32.5 | -3734 |
| 2015 | 0.222 | 107.8 | 63.3 | -9061 |
| 2016 | 0.215 | 80.3 | 50.2 | -39658 |
| 2017 | 0.219 | 69.1 | 31.2 |  |
| 2018 | 0.221 | 77.2 | 33.3 | -27231 |
| 2019 | 0.218 | 47.2 | 24.8 |  |
| 2020 | 0.225 | 69.2 | 35.1 |  |
| 2021 | 0.226 | 54.6 | 26.6 |  |
| 2022 | 0.226 | 90.0 | 46.0 |  |
| 2023 | 0.231 | 66.0 | 34.6 | -23435 |
| 2024 | 0.228 | 52.2 | 29.6 | -12022 |
| 2025 | 0.223 | 76.5 | 42.3 |  |
| 2026 | 0.224 | 57.4 | 28.5 |  |

Base vs smoothness corr: 0.13482614416577948
Base vs volatility corr: 0.26918854746495796

## Candidates (pts per year; corr with smoothness / volatility across tested years)

| Candidate | years | total pts | corr ER | corr ATR |
|---|---|---|---|---|
| u_regime_2400 | 8 | -66307 | 0.15 | 0.07 |
| k_hurst_trend | 8 | -58929 | 0.38 | -0.20 |
| l_dailydd | 8 | -124672 | 0.23 | 0.28 |
