# Test queue (added 2026-10-14; run AFTER the current clean-history loop finishes; one MT4 test at a time, RAM gate, no pause file)
Current loop (clean history, sp5 = the requested 5 pt max commission) is NOT useless: first valid run on the rebuilt history, so it keeps running.
1. Compile MR_RegimeSwitch_b53 (reject audit) in MetaEditor, add b53 mapping for clean mode, run on clean history, then data\reject_audit.py on MQL4\Files\reject_audit_b53.csv.
2. sp3 optimistic-floor scenario (FXOpen >250k balance: ~3-3.5 pts commission), label 'sp3 floor, UNVERIFIED commission currency', on loop winners only, via auto_loop.py --clean --spread 3.
3. Realistic-cost pass: 5 pts + yearly mean spread (see SPREAD_COMMISSION_RECORDS.md) on winners.
4. Offline meta-label test (logistic / small GBT on reject-audit signals, purged walk-forward by year).

**STANDING RULE (Nasif 2026-10-14): every forex test run includes a T25k round: FXOpen 25k+ tier 1.80/side/lot = 3.6 pts RT USD (~4.1 EUR basis), run at sp4, labelled 'T25k'. Implemented in auto_loop.py (T25K_SP) for the next relaunch; the currently running loop process predates it.**

**UPDATE: T25k round replaced by T3p45 = cheapest FXOpen cost (1.50/side/lot x2 x1.15 = 3.45 pts RT), run at sp3 then -0.45 pt/trade adjustment. Applies to every forex test from the next relaunch.**

LOW-SPREAD rule (2026-10-14): for the cheapest-commission scenario also evaluate 3.45 comm + ~2 pt spread (derived from sp5 runs, -0.45/trade) for every candidate, and run REAL sp2 tests on every promoted candidate/winner, per year, to compare with the other setups.

CLARIFIED: 'spread' = bid/ask spread, separate from commission. Low-spread scenario = 3.45 commission + 2 pt bid/ask = 5.45 total (derived from sp5, exact since cost is linear). The loop's sp-N tester setting carries TOTAL cost in pts, so a real 'sp2' run would omit commission and is NOT used.

MODEL (Nasif 2026-10-14): commission is FLAT per lot by balance tier (RT pts: <1k 8.05, 1k-25k 5.75, 25k-250k 4.14, >250k 3.45), bid/ask spread is separate (1-2 pts typical, yearly mean in SPREAD_COMMISSION_RECORDS.md). Loop stores cost_grid = tier x spread{1,2} per candidate, derived from the sp5 run.

5. MT5 (no login needed, 2026-10-14): build custom symbol EURUSD_CLEAN from the clean raw M1 bid/ask (data\csv_to_mt5.py, UTC->server UTC+2/+3 USDST, label it), compile MR_RegimeSwitch_b50.mq5, run MT5 Strategy Tester (every tick based on real ticks off / M1 OHLC with real variable spread from ask-bid), compare to the MT4 sp5 clean results. Only after the MT4 loop is idle (RAM).

6. Weekly-div capture PRE-MARKET exit (Nasif 2026-10-14: Webull used to allow selling on the ex-date at 4:00 am ET): test sell in 4:00-9:30 ET on ex-date vs 9:30 open, needs minute/extended-hours bars + realistic pre-market spreads; check broker pre-market availability at Webull/IBKR (UNVERIFIED). Study doc: docs\WEBULL_WEEKLY_DIV_CAPTURE_STUDY_14Oct2026.md

7. Yield-parking plan (docs\YIELD_PARKING_PLAN_14Oct2026.md): due-diligence report on the stablecoin 7.5% savings offer + comparison table; plan only, no deposits by Claude.

8. Shifted-bar stress test (idea from MQL5 article 'Does Your EA Depend on Candle Boundaries? A Shifted-Bar Stress Test in MQL5', seen 2026-10-14): re-run winners with the M15 z-score/regime computed on bars shifted by 5 and 10 minutes (build M15 from M1 with an offset); a real edge should survive, an artefact of candle boundaries will not. Also read MQL5 article 'Evolutionary Selection of LLM Agents in MetaTrader 5' for the self-improving clone loop (unverified relevance).

9. NEWS test pair (needs data\news_calendar_ff.csv from the polite-scrape agent; times in MT4 SERVER clock UTC+2/+3 USDST): (a) NEWS-GATE: skip fade entries within X min (10/30/60) before/after High-impact EUR/USD events, test on clean history; (b) NEWS STRADDLE study: offline first - for each High event measure |move| at +1/+5/+15/+60 min vs cost (5 comm + real spread, with spread widening assumed 3-10x at the release); straddle = buy-stop/sell-stop +-D pts placed T-2 min, OCO, SL, TP/trail, time exit; M1-bid sim is optimistic (no slippage, no spread spike) so validate fills on the 2.25 GB tick sample (2020-08-10..2021-08-18, bid/ask, QuotesDownloder.3\ticks.csv); only if net-positive after those costs build EA clone b70 reading events from MQL4\Files CSV and run in the MT4 tester (every-tick, real spread via sp setting, label). Honest prior: straddles are usually eaten by spread widening/slippage/whipsaw.
