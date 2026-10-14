# Validation report: leader g2_AtrCapPts_90 (14 Oct 2026, read-only analysis, clean history, "real" cost reports)
Years 2010 2013 2014 2015 2016 2018 2023 2024. Parsed 203 trades (not 216), total +18,132 pts, avg +89.3 pts/trade, win rate 49.8%, median trade -2.7 pts.
Per year (trades, pts): 2010 11, +1158 | 2013 8, -128 | 2014 40, +1200 | 2015 20, +5390 | 2016 35, +2065 | 2018 45, +5746 | 2023 13, -918 | 2024 31, +3620. 6 of 8 years positive.

## 1. Deflated Sharpe (per-trade SR 0.187, skew 0.48, kurt 3.49; SR variance across scored candidates 0.00515)
Trial counts: loop_state 16 + loop_state_clean 15 (28 distinct names), quarantine README 11 names, TEST_LOG 14 Oct distinct tags 60; union = 66. Only 11 candidates have >=30 trades in clean reports (dsr_check.py's own N).
| N | SR0 | DSR |
|---|---|---|
| 11 (scored, dsr_check style) | 0.116 | 0.851 |
| 66 (honest union, loop candidate count) | 0.171 | 0.595 |
| 198 (3x union) | 0.198 | 0.436 |
| 33 (3x scored) | 0.152 | 0.700 |
Reference: N=100 gives 0.533, N=1000 gives 0.247. DSR needs >=0.95. Fails at every N, including the most generous. Caveat: SR variance comes from only 11 candidates and the leader's variants are correlated, so true effective N is somewhat lower; also the formula is from memory (see dsr_check.py).

## 2. Bootstrap (5000 resamples)
- By trade: total pts 5th pct +6,733 (median +18,007); avg/trade 5th pct +33.2; P(total<=0) = 0.28%.
- By year blocks (8 years resampled): total 5th pct +7,623; avg/trade 5th pct +43.8; P(total<=0) = 0.10%.
Resampling only measures noise within this sample. It does NOT account for selection from many tries.

## 3. Concentration
- Best year 2018 = +5,746 = 31.7% of profit; without it +12,386. 2015 (+5,390) and 2018 together = 61%.
- Best 10 trades = +12,331 = 68.0% of profit; without them +5,801 (avg +30/trade). Best single trade +1,768.
- Median trade is negative: profit is a few large winners (fat right tail), typical of mean reversion with capped losses (worst trade -759).
- Sign by year: + + + + + + (2010, 2014, 2015, 2016, 2018, 2024), - (2013 -128, 2023 -918). 2013 and 2023 have only 8 and 13 trades.

## 4. Cost robustness (extra pts per trade, 203 trades)
| extra | total pts | avg/trade | positive years |
|---|---|---|---|
| 0 | 18,132 | 89.3 | 6 |
| 3 | 17,523 | 86.3 | 6 |
| 5 | 17,117 | 84.3 | 6 |
| 8 | 16,508 | 81.3 | 6 |
| 12 | 15,696 | 77.3 | 6 |
Costs are not the weakness (average edge is large vs cost). Slippage/spread on stop and fast-move fills is not modelled by a flat add-on.

## 5. Parity check: b57 engine vs leader (b57 files exist, sp5 only; compared to leader sp5 and real)
| year | b57 trades / pts | leader sp5 trades / pts | leader real trades / pts |
|---|---|---|---|
| 2010 | 12 / +1745 | 11 / +1182 | 11 / +1158 |
| 2013 | 7 / -691 | 8 / -110 | 8 / -128 |
| 2014 | 44 / +51 | 40 / +1311 | 40 / +1200 |
| 2015 | 20 / +2276 | 20 / +5444 | 20 / +5390 |
| 2016 | 36 / -1509 | 35 / +2161 | 35 / +2065 |
| 2018 | 50 / +681 | 45 / +5878 | 45 / +5746 |
| 2023 | 13 / +963 | 13 / -894 | 13 / -918 |
| 2024 | 28 / +591 | 31 / +3651 | 31 / +3620 |
b57 total about +4,107 vs leader sp5 about +18,6xx: the b57 engine does NOT reproduce the leader. Trade counts differ in 5 of 8 years, per-year sign differs in 2016 and 2023, and the best years (2018, 2024) shrink by 85%+. The leader's result depends on the engine/expert version (b51-era expert vs b57) or on set contents, so it is not a robust property of the strategy idea. (Cause not investigated: could be a set mismatch such as missing inputs, which should be checked first.)

## 6. Verdict: UNPROVEN (leaning LIKELY LUCK until parity is explained)
Two biggest weaknesses:
1. Selection: DSR 0.60 at the honest N=66 and 0.44 at 3x; never reaches 0.95. 68% of profit sits in 10 trades out of 203, so the result is fragile to which tails were hit.
2. Reproduction: the b57 re-run of the same leader gives +4.1k instead of +18k with different trade counts and flipped years, so the number is engine-specific.
Next two tests:
1. Find why b57 differs (diff the .set inputs and expert version; rerun the leader on the original expert/set with a fresh tester run to confirm trade-for-trade identity), then if equal on the same engine, rerun both on b57-compatible set.
2. True fresh out-of-sample: years never used in selection (e.g. 2011, 2012, 2017, 2019-2022, 2025-26, with the 8-period rule) at spread 5 and 8, frozen parameters, no further tuning; need DSR >= 0.95 on the combined new trades, with N counting all tries.
