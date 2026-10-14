# SURVIVORS (daily, hold 3, net of costs+tax)
Run: 2026-10-14 | 10 symbols, 10y daily history (Yahoo Finance, ~2016–2026)
Cost model: spread 4 bps/side + slippage 2 bps/side + reg fee 0.3 bps sell = **0.083% round-trip**
Hold: 3 days | Tax: 24% short-term on gains only | Group: stock
Data source: Yahoo Finance (via fetch_history.py). Large-cap only — survivor-biased. Not advice.

---

## Survival criteria (CLAUDE.md)
✓ n ≥ 30 in each period tested
✓ avg after-tax > 0 in ≥ 2 of 3 periods (2015-19, 2020-22, 2023-26)
✗ Periods missing = automatic rejection

---

## Full results

| rule | period | n | win% net | avg net% | avg after-tax% | dd_avg | dd_max | pass? |
|---|---|---|---|---|---|---|---|---|
| BASE | 2015-19 | 7263 | 54.7 | 0.098 | -0.075 | 14.1 | 240.8 | — |
| BASE | 2020-22 | 6804 | 52.8 | 0.069 | -0.219 | 40.1 | 257.5 | — |
| BASE | 2023-26 | 9170 | 54.0 | 0.116 | -0.126 | 22.0 | 755.9 | — |
| S1 RSI<30 & below BB | 2015-19 | 87 | 58.6 | 0.263 | **+0.028** | 2.3 | 13.0 | ✓ |
| S1 RSI<30 & below BB | 2020-22 | 115 | 58.3 | 0.208 | **-0.199** | 4.2 | 18.2 | ✗ |
| S1 RSI<30 & below BB | 2023-26 | 140 | 56.4 | 0.589 | **+0.222** | 2.7 | 17.6 | ✓ |
| S2 RSI<25 | 2015-19 | 83 | 49.4 | 0.200 | -0.032 | 2.9 | 13.1 | ✗ |
| S2 RSI<25 | 2020-22 | 108 | 53.7 | 0.193 | -0.178 | 5.5 | 24.2 | ✗ |
| S2 RSI<25 | 2023-26 | 147 | 56.5 | 0.624 | +0.238 | 3.3 | 14.5 | ✓ |
| S3 3d-5% & 10d-10% | 2015-19 | 10 | 50.0 | 1.640 | +0.963 | 4.6 | 8.8 | n<30 ✗ |
| S3 3d-5% & 10d-10% | 2020-22 | 66 | 51.5 | -0.756 | **-1.259** | 9.7 | 33.2 | ✗ |
| S3 3d-5% & 10d-10% | 2023-26 | 33 | 54.5 | 0.690 | +0.038 | 6.3 | 25.2 | ✓ |
| S4 below BB & Stoch<10 uptrend | 2015-19 | 11 | 63.6 | 0.352 | +0.150 | 1.3 | 2.5 | n<30 ✗ |
| S4 below BB & Stoch<10 uptrend | 2020-22 | 12 | 41.7 | -0.039 | -0.251 | 2.2 | 3.1 | n<30 ✗ |
| S4 below BB & Stoch<10 uptrend | 2023-26 | 14 | 71.4 | 1.439 | +1.024 | 0.9 | 1.4 | n<30 ✗ |

---

## Verdict: NO SURVIVORS (yet)

### S1 "RSI<30 & below BB" — closest to surviving
- ✓ 2015-19: n=87, after-tax +0.028% (marginal positive)
- ✗ 2020-22: n=115, after-tax **-0.199%** (COVID crash period killed it — deep RSI signals followed by further drops)
- ✓ 2023-26: n=140, after-tax +0.222%
- **Fails: only 2 of 3 periods positive.** 2020-22 is the exception period.
- Action: test with longer hold (5d, 10d) to give recovery time in crash regimes.

### S2 "RSI<25" — similar story
- Fails in all pre-2023 periods after tax. Tighter RSI threshold = fewer but lower-quality entries in downtrends.

### S3 "3d-5% & 10d-10% drawdown" — fails 2020-22 badly (-1.26% after-tax)
- Best gross returns in 2015-19 (n=10, too few) but catastrophic in COVID vol. Not actionable.

### S4 "below BB & Stoch<10 in uptrend" — best signal quality, terrible sample size
- n<30 in every period. This rule fires too rarely on 10 symbols × 10y to prove anything.
- Action: expand to 50+ symbols to get sufficient n.

---

## Key blocking issues

1. **Tax at 24% is the main edge-killer.** Net after costs is positive for S1 in 2015-19 and 2023-26 but tax wipes +0.028% to nearly zero and turns +0.208% into -0.199%.
   - Implication: these rules need an account structure that defers/avoids short-term tax (IRA/401k/ISA), OR longer holds that grow the gross sufficiently.
2. **2020-22 is consistently the worst period** for every rule — COVID and rate-hike volatility punished mean-reversion entries.
3. **S4 is the highest-quality signal but needs 50+ symbols** to get n≥30 per period.

---

## Recommended next actions

1. **Re-run S1 with hold=5 and hold=10** to see if longer hold rescues the 2020-22 period.
2. **Expand universe to 50 symbols** (add S&P 500 top 50 by volume) to give S4 enough trades.
3. **Apply tax-exempt filter** — report "net before tax" as primary metric; after-tax as secondary. Edge survives before tax in S1.
4. **Commit history_full/ to git** as the canonical dataset.
