# Feature definitions (laptop session b59d44, kept in sync automatically; 5-digit ECN points, 1 pt = 0.00001)
All on CLOSED bars of the tested timeframe (bar 1 = last closed). Clock: MT4 server time UTC+2 winter / UTC+3 US DST (aligned v2 history, see README_CLOCK_STATUS.txt).

- **Z-gate (z)**: z = (close[1] - mean(close[1..N])) / population_std(close[1..N]); parent N = 12 on M15, sell when z >= 2.812.
- **MMR**: d_k = close[k] - close[k+1] for k = 1..12 (points); mx = max(d), mn = min(d); MMR = mn/mx if mx > 0 else -9. Negative; near -1 = balanced moves, below -1 = down-moves dwarf up-moves, -9 = no up-moves. (b31 BrFeat; windows 6/12/24/48 also tested.)
- **slope**: s0 = EMA20[1] - EMA20[2] (points per bar); **accel** = s0 - s1; **ROA (rate of acceleration / jerk)** = accel - (s1 - s2); **SARA** = slope + accel + ROA; **slopeavg** = mean of the last 6 slopes. (SMA(pd) versions for pd 1, 2, 5, 10, 15 in sara_corr_map.py.)
- **PRV**: range + volRel*10 + (K - D) + K/10, with range = (high-low) in points, volRel = tick volume / average of the previous 20, K, D = Stochastic(14,3,1). **SARA/PRV** = SARA / PRV (old b31 Branch A level: >= 0.22).
- **Smoothness**: Kaufman ER_N = |close[1]-close[N+1]| / sum|close[k]-close[k+1]|; ER20 default. Also |net|/(ATR14*sqrt(N)).
- **Height / position**: (close - SMA(pd)) / ATR14. **Slope convergence**: std of ATR-normalised slopes of SMA(2,5,10,15); low = converging.
- **ADX/RSI/CCI/Williams %R/MACD**: standard (Wilder smoothing; MACD 12,26,9 histogram; CCI typical price; %R = -100*(HH-close)/(HH-LL)).
- **Hurst**: R/S over N bars (64/128/256). **Katz FD**, **perm entropy** (order 3, 62 bars), **VR(q)** variance ratio, **OU half-life** (regression of dx on x over 100 bars), **Lyapunov-like** (nearest-neighbour divergence).
- **Fractals** (Bill Williams): 5-bar highs/lows confirmed 2 bars later; features = bars since up/down fractal. **Alligator**: SMMA(13) shifted 8 = jaw, SMMA(8) shifted 5 = teeth, SMMA(5) shifted 3 = lips on median price; width = |lips-jaw|/ATR14.
- **Regime**: parent regime = H1 close[1] < SMA(H1 close, 3000).
- Costs: first rounds max 5 pts round trip or lowest commission (FIRST_sp2+3.45comm = 5.45 pts total), USD, lev 500 max; 6pt/8pt later. Results always in points.
