# Build 049 — Tier-4 Results
*Thread: acmtztn | Date: 2026-10-17 | Harness: w2_node.js (BASE5 fix applied)*

## Summary
- Build 048 baseline: **27,656 winners**
- Build 049 total: **34,717 winners** (+7,061 / +25.5%)
- New tier-4 survivors (pure new families): **2,061 winners** across 8 families
- 0-winner families: VWD, PAV, HUR (autopsied in `autopsy.md`)

## Theory Leaderboard (all families, sorted by avg HO win rate)

| Family | Tier | n | Avg HO% | Avg WP% | Avg HA%/trade | Best HO% |
|--------|------|---|---------|---------|---------------|----------|
| PBR* | 4 | 374 | 81.3% | 77.6% | 4.924% | 100% |
| CRB* | 4 | 17 | 81.2% | 83.8% | 1.589% | 100% |
| RSI | 0 | 1,792 | 80.4% | 78.1% | 4.156% | 100% |
| VQZ* | 4 | 673 | 79.9% | 75.9% | 3.721% | 100% |
| ACG* | 4 | 328 | 75.8% | 73.5% | 4.355% | 100% |
| RVL* | 4 | 141 | 75.6% | 68.2% | 2.543% | 100% |
| SWA* | 4 | 9 | 75.4% | 81.2% | 1.613% | 100% |
| KC | 2 | 56 | 74.5% | 62.2% | 4.829% | 100% |
| STD | 2 | 2,634 | 74.4% | 73.1% | 3.691% | 100% |
| CCI | 1 | 3,920 | 74.2% | 75.4% | 3.954% | 100% |
| CNV | 3 | 4,477 | 74.2% | 75.3% | 3.552% | 100% |
| STO | 0 | 3,733 | 73.7% | 75.0% | 3.616% | 100% |
| BB | 1 | 1,349 | 73.3% | 73.5% | 2.457% | 100% |
| MTF* | 4 | 28 | 71.6% | 76.2% | 2.386% | 100% |
| ENV | 2 | 1,512 | 71.2% | 71.5% | 2.069% | 100% |
| GAP* | 4 | 491 | 70.0% | 69.8% | 3.279% | 100% |
| ICH | 2 | 4 | 69.0% | 63.4% | 4.840% | 71.4% |
| AO | 2 | 2 | 67.5% | 66.0% | 4.855% | 75.0% |
| SAR | 1 | 158 | 66.1% | 64.4% | 4.193% | 100% |
| BBO | 1 | 16 | 65.7% | 67.0% | 6.876% | 100% |
| MACD | 1 | 10 | 54.5% | 57.9% | 4.162% | 57.1% |

*\* = new tier-4 families added in build 049*

## New Family Details

**PBR (Price Bounce at EMA)** — 374 winners, 81.3% HO win rate. RSI>50 filter (upper cap removed) was the key fix. Top: KO|M120 wp=100% hwp=100% t=14.

**CRB (Channel Range Bounce)** — 17 winners, 81.2% HO win rate. Small sample but high quality. Best: DIA|H2 wp=100% hwp=100% t=10.

**VQZ (Volatility Squeeze)** — 673 winners, 79.9% HO win rate. BB compression + RSI>50 momentum filter produces clean breakout entries. Best: DIA|H2 wp=100% hwp=100% t=13.

**ACG (Adaptive Cost Gate + BB Bounce)** — 328 winners, 75.8% HO win rate. Dynamic ATR gate at 0.5/1/1.5% filters low-volatility noise effectively. Best: STETHUSD|M120 wp=100% hwp=100% t=12.

**RVL (Range Volume-Like)** — 141 winners, 75.6% HO win rate. HL-range proxy for activity replaces missing volume. Best: USO|H2 wp=100% hwp=86.7% t=15.

**GAP (Exhaustion Bar Reversal)** — 491 winners, 70.0% HO win rate. Redefined from gap-down to large-bear-bar reversal (ATR multiples). Best: KO|H2 wp=91.7% hwp=100% t=12.

**MTF (Multi-Timeframe Confluence)** — 28 winners, 71.6% HO win rate. Small count; Stoch<20 crossup + SMA50 filter. Best: XLF|H2.

**SWA (Swing/Wave)** — 9 winners, 75.4% HO win rate. Tiny n; consecutive-bar pattern. Needs more series coverage.

## 0-Winner Families (see autopsy.md for full diagnosis)
- **VWD**: VWAP proxy too tight-tracking on M15; triple condition (deviation + bullish + ADX>15) near-impossible to satisfy
- **PAV**: ATR share ratio + RSI<50 + 3-bar V-pattern combination produces 0 passes
- **HUR**: Hurst R/S unstable on n=20-30 windows; noisy signal with no stable edge

## Root Cause Fixed (Session Log)
The critical bug was w2_node.js not including BASE5 in Gen A. T5 detection used `typeof BASE4!=='undefined'` (CNV/tier-3) but there was no T6 for BASE5 (tier-4 VQZ et al). Fix: added T6 detection + BASE5 concat across all 8 relevant lines in the harness pipeline (lines 14, 31, 34, 35, 36, 37, 38, 43).

---

## Run 4 — Build 049d: ZSCO / STRK / DOW (2026-10-17)

**Harness:** node tools/w2_node.js | 156 series | 575,952 jobs | 120 s

**New families:**
- **ZSCO** (Z-score mean-reversion): n=267 survivors | train wp=72.5% avg=+5.4% | holdout wp=73.7% avg=+2.7%
- **STRK** (Consecutive-bar streak reversal): n=275 survivors | train wp=70.3% avg=+5.8% | holdout wp=70.2% avg=+3.7%
- **DOW** (Day-of-week bias): 0 winners — autopsy: entry fires every bar of target day, noise; autopsied in autopsy.md

**Top ZSCO entries:**
- ZSCO atp4 asl2 | TSLA | M240 — wp=71% ha=23.6%
- ZSCO | TSLA | M240 — wp=69% ha=23.6%

**Top STRK entries:**
- STRK hold8 | AAPL | M240 — wp=56% ha=24.3%
- STRK hold6 | AAPL | M240 — wp=60% ha=14.6%

**Total unique winners (build 049d): 35,646** (+929 from 049c, +7,990 from build 048 baseline of 27,656)

**Tier-4 leaderboard (holdout avg, top 5):**
1. PBR h_wp=81.3% h_avg=+4.9%
2. ACG h_wp=75.8% h_avg=+4.4%
3. RSI (t4 regime) h_wp=77.9% h_avg=+4.1%
4. CCI (t4 regime) h_wp=71.2% h_avg=+4.0%
5. GAP h_wp=70.0% h_avg=+3.8%

STRK ranks 10th, ZSCO 14th out of 20 t4 families.

All results net of 8-pt commission + spread + swap. Holdout = last 30% of each series.
