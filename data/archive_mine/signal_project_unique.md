# Unique trading-logic ideas mined from Signal project transcripts

Source: six transcripts (c41bfc55, ee50d20a, 63a1d9ef, d5a8df61, 844c8c11, 706dd7a3), Oct 12-14 2026. Skipped d9ad0f50 and c4362a85 (current sessions). Known families excluded from "unique": LINEAGE_DNA.md, RED_ZONES.md, g2_ZTrigger and b50-b52 regime family. Scripts: `_sent.py` (sentence extractor, reproducible). All numbers are as stated in the transcripts; most are in-sample or replay-only unless marked.

Cost basis in transcripts: 8 pts/trade (house rule), 6 pts (FXOpen small-balance tier), 5 pts (lab), realistic = 5 + yearly mean spread.

| # | Rule idea | Exact parameters | Evidence (numbers, session, date) | Status |
|---|---|---|---|---|
| 1 | ADX trend block on the stochastic/slope entry | BlockADX 28 -> 24 (g7a) | g7a PF 1.953, 134 trades, DD 21.84 in-sample (706dd7a3 Oct 12; 844c8c11 Oct 12). Author flags it as tuned on the same window (overfit). ADX sweep 20-26 rejected under pre-set rule (706dd7a3 Oct 12); ADX 20 PF 1.586 (g7b) | tested-failed as robust gate; in-sample only |
| 2 | Hour and weekday gate: Thursday + hours 6/8/19 block | g4b "hour-thu-filter" | OOS gate PASS: PF 1.46, DD 0.34%, 182 trades (706dd7a3 and 844c8c11 Oct 12; commit 4addc85). Weak hours in 844c8c11 data: 4h, 6h, 13h, 14h, 19h-22h at 39-51% win rate. Mon/Fri ~69% win rate (844c8c11 Oct 12) | proven on one OOS window only; 2023-24 showed 0 trades, so validity across years unclear |
| 3 | Bollinger+ADX+CCI sized bracket (mean-reversion fade in chop) | margin = (0.10 + 0.01 x ADX_over_15) x bandwidth; stop = 0.6 x bandwidth; h1b/h1c blend weights ADX 1.0 / ATR 1.0 / tick volume 0.5 | h1c win 66.8%, DD 0.25% but PF below 1.10 (706dd7a3 Oct 12). h1d (SLK 0.35, SLATRK 1.00, TPFadeFrac 1.00) win 37.8%, PF down. Round 2: none of 6 bracket variants reached PF 1.10 on 2016 | tested-failed |
| 4 | Stop/target geometry: raise TP:SL ratio to cut break-even win rate | Current 1:1 at 300/300; test TP 450 and TP 600 vs 300 | At 5 pts cost 1:1 needs ~52% win rate; TP 450 needs ~42%, TP 600 ~37% (706dd7a3 Oct 14). Sells currently win 37-47% with avg winner +46.7 vs avg loser -49.3 | untested (queued as r_tp450, r_tp600) |
| 5 | Trailing stop for winners | Start 100 pts, trail 150 behind (also tested: 100/50, 200/100, ATR version; b50 versions start 150, held 250 behind) | Tighter trail captured ~55% of the move vs 38% for the time exit (706dd7a3 Oct 14, offline) | untested (queued) |
| 6 | Daily drawdown freeze | Stop new entries after 2% daily drawdown (l_dailydd) | None yet (706dd7a3 Oct 14) | untested (queued) |
| 7 | Calm/orderly tape gate for sells | Sell only in low-volatility, low-entropy markets (m5_sell_calm) | Offline scan +16 to +26 pts/trade in all 5 years, but scan used the judged years. m5_sell_calm took only ~31 trades (706dd7a3 Oct 14) | untested OOS; too few trades |
| 8 | Hurst-trend candidate (k_hurst) | Hurst-based trend gate, exact threshold not stated in transcript | Passed 2023, then tested 2018. Only profitable year with real trade count: 2024 +$1,134 (706dd7a3 Oct 14). Single-feature Hurst judged weak on its own | in progress; unclear |
| 9 | Cost-aware mutation scoring | Add real spread by hour (~17 pts at server hour 21) as a cost term | Proposed design only (706dd7a3 Oct 14) | untested |
| 10 | Cost gate on entry (break-even win-rate check) | InpCommissionPts = 6; InpMinRR = 1.5; skip if win rate below break-even at 8 pts (~51%) | c41bfc55 Oct 12 (Strong2010b fix proposal); ee50d20a Oct 12 (break-even ~51% at 8 pts) | proposed; no test result |
| 11 | Williams %R overbought block for sells | Block sells when Williams %R > -41 (overbought third) | Sells worse than year average in 4 of 5 years (706dd7a3 Oct 14, offline) | untested as gate |
| 12 | Fractal support block for sells | Block sells below last down-fractal | Worse in 4 of 5 years (706dd7a3 Oct 14, offline) | untested as gate |
| 13 | CCI extreme entry (Strong2010b variant) | Sells need CCI >= +50; buys need CCI <= -50 | Stated rule in a Strong2010b variant (706dd7a3 Oct 12); no result found in transcripts | unclear |
| 14 | TP/SL replay on 2021 fills | TP 250 / SL 400: win 68.3%, PF 1.28, +$204.56, DD $182.78, p = 0.176; TP 250 / SL 500: win 72.9%, PF 1.28, p = 0.173 | ee50d20a Oct 12 (offline, entries fixed). Not statistically significant | tested offline, not significant |
| 15 | Wide-stop "win-rate illusion" check | High win rate with small TP (15) vs large SL (290) hides losses | ee50d20a Oct 12 (g2a analysis) | tested-failed (g2 family, listed for the check rule) |
| 16 | Sell-only mean-reversion fade with ATR cap | z >= 2.5, lookback 10, hold 48 bars, ATR14 < 60 pts; b51 + ATR cap 60 = +5,109 pts PF 1.26; 174 trades | 706dd7a3 Oct 14. Offline ~+35 pts/trade 2010-17, +33 2018-26. Regime 2400 variant -22,341 pts | b50-b52 family (excluded as known). ATR cap overlaps RED_ZONES "High ATR14 tercile" |
| 17 | Support/resistance distance feature | Two nearest fractal levels above and below price, distances in pts | Feature list only (706dd7a3 Oct 14) | untested |
| 18 | Neural-net meta-label on rule triggers | MLP or LSTM outputs P(hit TP before SL); trade only if P > 0.65; exported via ONNX | Design request only, no results (706dd7a3 Oct 14). Author warns of overfit on small trade counts | untested |
| 19 | Look-ahead MFE study | Price move 4, 16 and 96 bars after each bar, in pts | Research method only (706dd7a3 Oct 14) | untested |
| 20 | Ex-date exit (other market: US funds) | Exit 1 to 4 days after ex-date; net +11 to +71 bps at 20 bps cost; ex-date close -14 to -19 bps gross | 706dd7a3 Oct 14. Every hold variant lost to SPY by 100+ bps. Not FX | other market; no FX test |
| 21 | Pullback-to-range entry (other market: funds) | Bottom 25% or 33% of 5/10/20-day range after 2-3 day pullback, or below short MA | Design list (706dd7a3 Oct 14) | other market; untested |
| 22 | Spread and calm-tape time window | Spread <= 2 pts, calm M15 tape, server hours 10-18, Mon-Thu | 706dd7a3 Oct 14; context unclear (not stated for EURUSD EA) | unclear |

## Notes
- Unique rule count: 22 rows. Excluded as known: ER, MMR, regime SMA 1200/2400, ZGate, daily range, stochastic K14 > 80, rollover hours 20-22, NFP, ATR tercile, g2 and b50-b52 families.
- Process findings (not rules): 2023 and 2024 show 0 trades under ZGate + DailyRange; 2013-14 sell regime blocks almost all sells (5-7 trades). Treat g4b and b31 results as conditional on that.
- Overfit flags the transcripts raised themselves: g7a (BlockADX 24) and calm-tape scan (same years judged).

## Top 5 untested ideas (for the loop)
1. Exit ratio test: TP 450 and TP 600 vs 300 on the b31 base (row 4). Break-even win rate falls from ~52% to ~42% or ~37%.
2. Trailing stop 100 start / 150 behind (row 5). Offline capture 55% vs 38% for time exit.
3. Daily drawdown freeze at 2% (row 6).
4. Calm-tape sell gate, but only after a clean out-of-sample run (row 7). Trade count is too small yet.
5. Williams %R > -41 and below-fractal sell blocks (rows 11-12). Both are negative in 4 of 5 years offline.
