# H4 Bearish Bar Gate — Research Summary (16 Oct 2026)

## G-Script Finding (cloud_G_h4bar_v1.py + h4thresh_v1_G.py)
- Dataset: parent.csv (full backtest, gross, base WR=50.0%)
- H4 bearish (close<open): N=86, WR=67.4%, +17.4pp
- H4 bullish: N=68, WR=27.9%, -22.1pp
- close_pos Spearman r = -0.369 (strongest signal in research)
- Per-year: 7/8 years consistent (2015 exception, small N)
- Optimal threshold: cp<=0.50 (bearish = close in lower half of range)
- Body% filter: ADDS NOTHING. Drop it.

## Clone C Cross-Validation (HOLD set, base WR ~68%)
- H4bear alone: N=69, WR=65.2% (delta +~-3pp vs G, consistent given higher base)
- H4bear + cp<=0.50: N=57, WR=63.2% — cp DROPS WR, confirmed useless
- H4bear + CI-16: N=36, WR=69.4%
- H4bear + h08-09: N=10, WR=60.0% — thin, h09 weak in C's data
- H4bear + cp0.50 + CI-16: N=32, WR=68.8%
- Best C combo: H4bear + CI-16 at 69.4% — not P1-worthy standalone

## Hour Divergence (real, not clock artifact — clock confirmed same UTC+2/+3)
- G: h08-09 best (+6.4pp, N=55)
- C: h03 best (71.4%, N=21)
- Likely explained by different years/regimes in each dataset

## Conclusions
1. H4 bearish bar = VALID MT4 FILTER (not standalone P1 gate)
2. cp<=0.50 adds nothing beyond close<open boolean — use boolean
3. CI-16 is C's anchor; H4bear is G's filter — complementary
4. MT4 test (h4anchor_on) will proxy-test H4 alignment via UseH4TrendAnchor=1 (MA-based, not exact)
5. True H4 bar gate needs new EA parameter for exact close<open logic

## Status
- MT4 skip_h16h19: QUEUED (evolve loop holding lock)
- MT4 h4anchor_on: QUEUED after skip_h16h19
- Clone C's best gate: P1 = conv+CI-16+TueThu (HOLD 89.5%, TRAIN 77.8%, DSR=0.677, 3/4 periods)
