# Tier-4 Family Autopsy — Build 049
*Date: 2026-10-17 | Thread: acmtztn*

## VWD — VWAP Deviation (0 winners)
**Condition:** close < vwapN(b,n) × (1 - d/1000) AND bullish bar AND ADX(14)>15
**Seeds:** d=3,5,7 (0.3/0.5/0.7% threshold)
**Root cause:** VWAP proxy is a rolling typical-price SMA with no volume weighting; on noisy M15/H2 bars it tracks close too tightly — deviations of >0.3% AND a bullish close AND ADX>15 almost never co-occur in the same bar. The triple condition eliminates ~100% of candidates.
**Next fix:** Drop ADX gate (or lower to >10); use deviation alone + bullish close. Alternatively use a longer rolling window (n=50+) so the proxy diverges more.

## PAV — Price Action V-bottom (0 winners)
**Condition:** 3-bar V: bar[i-2]<bar[i-3] AND bar[i-1]>bar[i-2] AND bar[i]>bar[i-1] AND shr∈[0.3,3] AND RSI<50
**Seeds:** shr range [0.3,3], RSI<50
**Root cause:** ATR share ratio pvShr = (b[i].c-b[i-2].c)/atr requires exact ATR magnitude alignment. The RSI<50 requirement rejects trending up-moves. Combined, passes ≈ 0 on every series tested.
**Next fix:** Remove RSI filter entirely; test shr range [0,10] to confirm the 3-bar pattern itself has any edge. If 0 still — the 3-bar consecutive filter is simply too rare.

## HUR — Hurst Exponent Entry (0 winners)
**Condition:** hurstN(b,n)[i] > sp.h/100 (e.g. H>0.55) AND close > EMA20
**Seeds:** n=20,30; h=60,55 (H>0.6, H>0.55)
**Root cause:** Hurst R/S on 20-bar windows is extremely noisy — values swing between 0.2 and 0.9 within a single session. The threshold H>0.55 fires as often as random, and EMA20 cross adds a conflicting filter. The combination never builds a stable exit.
**Next fix:** Use n≥50 (need longer series for R/S stability); or replace with a simpler persistence check (3 consecutive positive log-returns).
