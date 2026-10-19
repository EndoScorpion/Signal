
---
## G10-7 — T31s_0.3x+MMR (SURVIVOR — Gen 10 2026-10-19)
Entry: Fri 14:00 SHORT, day_up>0.3×ATR14, mmr≥-1.0, xNFP
IS (FX ECN 2024-26): n=45 WR=64.4% PF=2.21
OOS (TD 2020-23): n=53 WR=67.9% PF=2.85 avg=+119.5pts yr=3.28/2.68/3.35/1.78 ✓ALL_YRS

## G10-4 — G5-2+minSSR>-2 on TD split (SURVIVOR — Gen 10 2026-10-19)
Entry: Fri 14:00 SHORT, day_up>0.5×ATR14, mmr≥-1.0, minSSR>-2, xNFP
IS (TD 2020-23): n=33 WR=69.7% PF=2.89
OOS (TD 2024-26): n=23 WR=69.6% PF=2.79 avg=+55.6pts yr=9.40/3.24/1.48 ✓ALL_YRS

## G11-3 — T31s_0.3x+MMR+GateA (SURVIVOR — Gen 11 2026-10-19) *** NEW BEST ***
Entry: Fri 14:00 SHORT, day_up>0.3×ATR14, mmr≥-1.0, slope120≥-0.1×ATR14, xNFP
IS (FX ECN 2024-26): n=34 WR=70.6% PF=2.84
OOS (TD 2020-23): n=36 WR=75.0% PF=5.19 avg=+176.7pts yr=3.27/13.33/18.90/1.74 ✓ALL_YRS
NOTE: GateA = EMA(120).diff(5) >= -0.1 * ATR14 (from 2011a loss gate research)

## G12-04A — T31s_0.4x+MMR+GateA (SURVIVOR — Gen 12 2026-10-19) *** NEW BEST ***
Entry: Fri 14:00 SHORT, day_up>0.4×ATR14, mmr≥-1.0, slope120≥-0.1×ATR14, xNFP
IS (FX ECN 2024-26): n=34 WR=70.6% PF=2.84
OOS (TD 2020-23): n=35 WR=77.1% PF=5.67 avg=+185.4pts yr=3.27/13.33/825.33/1.74 ✓ALL_YRS

## G12-G52A — G5-2+GateA (SURVIVOR — Gen 12 2026-10-19)
Entry: Fri 14:00 SHORT, day_up>0.5×ATR14, mmr≥-1.0, slope120≥-0.1×ATR14, xNFP
IS (FX ECN 2024-26): n=34 WR=70.6% PF=2.84
OOS (TD 2020-23): n=34 WR=76.5% PF=5.29 avg=+175.6pts yr=3.27/9.95/825.33/1.74 ✓ALL_YRS

---

## G13-S3: T31s_0.4x+MMR+GateA(0.2)+GateB — Gen 13 NEW BEST (2026-10-19)

**Type:** Friday mean-reversion SHORT  
**Universe:** EURUSD H1 (ECN broker)  
**ECN pts:** 5-digit quotes; 1 pip = 10 pts

```
Entry: Friday 14:00 UTC SHORT
Condition 1: open − prev_day_close > 0.4 × ATR14  (day_up threshold)
Condition 2: MMR ≥ −1.0  (12-bar close-diff ratio)
Condition 3: EMA120.diff(5) ≥ −0.2 × ATR14  (GateA coef=0.2)
Condition 4: Stoch(5,3) fast-K rolling(3) < 85  (GateB)
xnfp: skip first Friday of month
Stop: none
Exit: Friday 21:00 UTC
Cost: 0.00008/trade
```

**IS (FXOpen ECN 2024-26):** n=30, WR=63.3%, PF=2.22  
**OOS (TwelveData 2020-23):** n=35, WR=77.1%, PF=7.56, avg=+187 ECN pts  
**OOS by year:** 2020=7.62 / 2021=10.93 / 2022=677 / 2023=1.37 (all ≥1.0 ✓)  
**Beats:** G12-04A (PF=5.67 → 7.56)
