# TP250/SL400 MT4 confirmation plan (cloud scorer signal-8c; read-only, no EA/queue edits)
## 1. Sanity check of 2021 OOS numbers (data/tpsl_oos_2021.md, stats_8pt_2021_g1a.md)
- Arithmetic OK @8pt: win +242 / loss -408 pts, break-even 408/650 = 62.8%; observed 68.3% (cushion 5.5 pts). Recomputed PF 1.278, net 0.36 $/trade x 568 = $204.5 (file: 204.56). DD $182.78 = 1.8% of $10k (0.9% if the report deposit is $20k; use the report's deposit).
- Weak evidence: day-block p=0.176 (85 days), runs z=-19.6 (legs cluster, so effective n ~ days not 568); misses Bonferroni 0.0024. Baseline g1a is PF 1.05, p=0.43.
- Selection bias: TP250/SL400 was picked as best of a 16-21 combo grid on 2019 and 2021 fills, so 2021 is NOT clean OOS for this choice. Only 2012 and 2011 are untouched.
- Win% rises by construction (wider SL); entries held fixed (EA ladder/hedge entries may shift). Sep +$118 is over half of net; Aug -$105; 2021-05 has no row (check gap vs no trades).
## 2. Exact input changes (source: data/Strong2010b_claude_g2a.mq4; queue lines carry no inputs, so builder makes 2 new EAs)
- SellStopTP=300->250, SellStopSL=300->400 (sell stops and the 3-leg ladder use these, lines ~1803/1838); HedgeTP=300->250, HedgeSL=300->400 (hedge sell, line ~1834). Leave tp=7, UseLotSim, LadderMode=0 as-is; UseRiskGuard stays 0 so only TP/SL changes (g2e is a separate test).
- Verify in the g1a source (b20legs_g1a) that no other sell-side leg (LadderTP/SL, BracketTP/SL, RoundTP/SL) is active; I only read the g2a copy.
- New EA names (suggested): Strong2010b_claude_b20legs_g1a_tp250sl400 and Strong2010b_claude_g2a_tp250sl400.
## Queue lines to add (EA|Period|From|To|Spread; date format as used in tpsl_oos 2021.03.19, confirm vs run_queue.ps1)
Strong2010b_claude_b20legs_g1a_tp250sl400|M1|2021.03.19|2022.01.01|3
Strong2010b_claude_g2a_tp250sl400|M1|2021.03.19|2022.01.01|3
Strong2010b_claude_b20legs_g1a_tp250sl400|M15|2012.01.01|2012.12.31|<copy spread from existing 2012 g1a line>
Strong2010b_claude_g2a_tp250sl400|M15|2012.01.01|2012.12.31|<same>   (same two lines again for 2011.01.01|2011.12.31)
Pair each with the baseline g1a/g2a run on the same window (queue jobs 5-6, 11-12) so the comparison is like-for-like.
## 3. Pass criteria (raw prices, 8pt charged once, per window)
- PF@8 >= 1.10 AND max DD < 5% of the report deposit AND win% > 62.8% break-even AND PF above the same-window baseline, in 2012 AND 2011 (fresh) and no worse than PF 1.10 in 2021 MT4.
- Day-block p(net<=0) <= 0.05 on 2012+2011 pooled (single pre-registered candidate; 0.0024 only applies to the grid search). Trade-level p-values are not valid. M15 same-bar TP+SL counts as SL, so M15 is pessimistic.
- Fail or pause if any window has PF<1.10, DD>=5%, or >50% of net comes from one month.
