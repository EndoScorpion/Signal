# Weekly-dividend capture study (Webull US, $0 commission) - 14 Oct 2026
OFFLINE BACKTEST RESEARCH ONLY. Not investment advice, NOT approval to trade (CLAUDE.md: backtests are never live approval). No orders, accounts or trading tools used.
Sources/dates: Yahoo chart API (unofficial; split-adjusted daily OHLC + ex-dates), 2 years to 13 Oct 2026, read 14 Oct 2026; earlier pass used Twelve Data + Alpha Vantage (matched). Universe lists: stockanalysis.com weekly-dividend ETF list (166 listed, top 100 by yield read) + 49 non-weekly payers. Script: data\nav_erosion_update.py (reproducible). Dividend amounts, fund launch dates and tax character UNVERIFIED against issuers.
Biases: survivors only (still-listed funds), many funds launched during the window (few events), all weekly funds share the same Wednesday/market shocks so the 100 funds are NOT independent samples, one 2024-26 regime. Treat every number as a lead, not a result.

## 1. Weekly payers ranked by trailing 12-month yield (top 25 of 101; full list in data\nav_erosion_tracker.csv)
Window = last 365 days (or since launch). TR = price change + distributions (no reinvestment). exOpen/+2d = mean net bps per event at 20 bps round-trip cost.
| # | Sym | Yield %/yr | Price chg % | Distrib % of start | TR % | Events | exOpen net20 | +2d net20 |
|---|---|---|---|---|---|---|---|---|
| 1 | COYY | 292 | -85.1 | 43.5 | -41.6 | 62 | -14 | -101 |
| 2 | MAAY | 258 | -81.9 | 46.7 | -35.2 | 48 | -21 | -99 |
| 3 | IOYY | 250 | -78.1 | 54.7 | -23.5 | 48 | -17 | -28 |
| 4 | HOYY | 244 | -80.7 | 47.2 | -33.5 | 53 | +5 | -57 |
| 5 | MST | 242 | -93.5 | 15.8 | -77.7 | 72 | +81 | -166 |
| 6 | SMYY | 228 | -78.3 | 49.6 | -28.6 | 53 | +6 | -49 |
| 7 | RGYY | 227 | -79.3 | 47.0 | -32.3 | 45 | -30 | -77 |
| 8 | MTYY | 221 | -85.8 | 31.3 | -54.6 | 54 | +3 | -117 |
| 9 | MARO | 213 | -83.5 | 35.1 | -48.4 | 62 | +23 | -30 |
| 10 | QBY | 208 | -77.2 | 47.3 | -29.9 | 44 | -14 | -90 |
| 11 | RTYY | 191 | -71.2 | 55.1 | -16.1 | 44 | -3 | -51 |
| 12 | TSYY | 173 | -68.4 | 54.8 | -13.6 | 76 | -2 | -42 |
| 13 | WNTR | 170 | -49.2 | 86.6 | +37.4 | 57 | -39 | -108 |
| 14 | CRCO | 167 | -73.6 | 44.1 | -29.6 | 51 | -28 | +48 |
| 15 | HMYY | 166 | -77.8 | 36.8 | -41.0 | 44 | -15 | -109 |
| 16 | MSTW | 158 | -84.1 | 25.1 | -59.0 | 62 | -25 | -185 |
| 17 | SEMY | 151 | -51.5 | 73.5 | +22.0 | 46 | -14 | +15 |
| 18 | HIYY | 150 | -75.7 | 36.5 | -39.2 | 51 | +21 | +51 |
| 19 | MSTY | 148 | -76.9 | 34.3 | -42.6 | 64 | +6 | +78 |
| 20 | ULTI | 145 | -77.2 | 33.1 | -44.0 | 47 | +48 | -84 |
| 21 | COIW | 144 | -80.2 | 28.6 | -51.6 | 84 | +13 | +47 |
| 22 | RDYY | 141 | -64.5 | 50.0 | -14.5 | 52 | -27 | +11 |
| 23 | RBLY | 141 | -80.2 | 27.9 | -52.3 | 53 | -74 | -155 |
| 24 | PLYY | 138 | -65.7 | 47.2 | -18.4 | 54 | -12 | -4 |
| 25 | SMCY | 134 | -70.0 | 40.1 | -30.0 | 64 | -1 | +37 |
Ranking pattern: the higher the headline yield, the bigger the NAV loss. Of 98 weekly funds with a full 365-day window, 66% had total return below zero; average price change -46%, average distributions +41%, average TR -5%, median -9% (SPY price +17% over the same year). 74 of 150 tracked symbols are flagged "price fell more than distributions" (all weekly except O, OBDC, PSEC, BXMT, T, IBM, NVO).

## 2. Per-event capture (buy prior close, exit at ex-open etc.), all 101 weekly funds vs non-weekly
Net bps per event after 20 bps round trip (4 bps RT adds +16). Symbols need >= 8 events.
| Group | Symbols | Yield %/yr | Div %/event | Ex-date drop %/event | exOpen net20 | +2d net20 | Symbols positive in BOTH halves (exOpen / +2d) |
|---|---|---|---|---|---|---|---|
| Weekly | 101 | 98.8 | 1.49 | 1.54 | -10.4 | -16.0 | 10 / 13 |
| Monthly | 17 | 10.3 | 0.79 | 0.75 | -10.8 | +3.8 | 0 / 4 |
| Quarterly (8 events each) | 23 | 5.4 | 1.30 | 1.46 | -22.9 | -16.7 | 0 / 5 |
Pooled weekly baseline (6,175 events): ex-open net +5.7 bps at 4 bps RT, -10.3 at 20 bps (win 45%, worst -1,909 bps); ex-close -6/-22; +1d -12/-28; +2d +5/-11; +3d +4/-12; +4d -16/-32. Ex-date drop is about equal to (slightly above for weekly/quarterly) the dividend, so capture is zero-sum before costs; costs make it negative.
Non-weekly answers: (a) Per event, a few non-weekly payers pay MORE (BXMT 2.7%, NLY 3.4%, ARCC 2.3%, PBR 2.3%, PFE 1.7%), but the average quarterly payer (1.30%) is below the weekly average (1.49%). Per year, no non-weekly payer matches high-yield weekly funds (PSEC 29%, BXMT 17.5%, AGNC 17% vs weekly 40-290%). (b) Fewer events means fewer cost hits, but the ex-date drop also matches the larger dividend (quarterly drop 1.46% vs div 1.30%, often MORE than the dividend), so edge per event does not rise. Capture does not work better there: no non-weekly group is positive at 20 bps, none is stable. Best non-weekly ex-open net20: BXMT +13, MAIN +12, QQQI +4, ARCC +3, SPYI +2 (n = 8-31 each, halves disagree for most: BXMT -12/+38, MAIN +27/-3).
Best weekly ex-open net20 (halves in brackets): MST +81 (68/94), AMDW +75 (118/31), SNOY +54, ULTI +48 (75/23), CHPY +43 (57/29), HOOW +25, MARO +23 (35/10), USOY +21 (17/26). Only 10 of 101 weekly and 0 of 40 non-weekly symbols are positive in both halves at ex-open. With ~140 symbols tested, 10 such survivors is about what chance gives.

Ranking by net result AND stability (20 bps, both-halves-positive filter; n = events): 1. MST (72, +81, both halves +), 2. AMDW (62, +75), 3. ULTI (47, +48), 4. CHPY (78, +43), 5. MARO (62, +23), 6. USOY (76, +21), 7. HIYY (51, +21), 8. ARMW (49, +21; halves 0/+42). Everything else fails a half or is negative. Low confidence: tail trades -2,000 to -4,000 bps exist in the weekly set and MST is a leveraged -93% fund whose half results hinge on a few weeks.

## 3. Entry-timing ("low buy, high sell") variants, weekly funds, pooled
Pre-registered, not tuned: 9 entry rules (base; close in bottom 25% or 33% of the trailing 5/10/20-day close range; 3-day pullback close[t-1] < close[t-4]; below 10-day SMA) x 7 exits (ex-open, ex-close, +1..+4d, first close >= prior-20-day range midpoint else +4d) = 63 combinations tried; only the ones below are shown. Split at 5 Mar 2026. Net bps per trade, 20 bps RT unless stated.
| Entry | Exit | n | net4 | net20 | win20 % | worst20 | half1 | half2 |
|---|---|---|---|---|---|---|---|---|
| base | ex-open | 6175 | +5.7 | -10.3 | 45 | -1909 | -7 | -14 |
| base | +2d | 6175 | +5.4 | -10.6 | 50 | -3796 | -29 | +8 |
| low5_25 | ex-open | 2195 | +13.1 | -2.9 | 49 | -948 | -4 | -2 |
| low5_25 | +2d | 2195 | +41.3 | +25.3 | 52 | -3796 | +4 | +45 |
| low5_33 | +2d | 2392 | +35.8 | +19.8 | 51 | -3796 | -1 | +39 |
| low10_25 | +2d | 2333 | +32.2 | +16.2 | 52 | -3796 | -28 | +56 |
| pull3 | ex-open | 2804 | +13.9 | -2.1 | 50 | -1909 | -2 | -2 |
| pull3 | +2d | 2804 | +29.0 | +13.0 | 51 | -3796 | -6 | +32 |
| low20_33 | +2d | 3225 | -2.4 | -18.4 | 49 | -3796 | -38 | +1 |
| below_sma10 | +2d | 3425 | +12.8 | -3.2 | 50 | -3796 | -32 | +25 |
| any | range-midpoint exit | 2.2-3.4k | -8 to -38 | -24 to -54 | 48-50 | -3229 to -4146 | negative | mostly + |
Findings: entering after a short-range (5-day) dip and exiting +2d improved the baseline by about +35 bps per trade, positive in both halves only for low5_25 (+4/+45) and with a worst trade -3,796 bps; the 10/20-day-range, SMA and midpoint-exit variants did not help. Ex-open exits stay negative at 20 bps in every variant. Trade counts are large, but events are cross-correlated (same weeks across 100 funds), so effective sample is closer to ~25 weeks than 2,195 trades. One variant of 63 passing is within chance; NOT validated. Improvement is mostly in half 2 (Mar-Oct 2026).

## 4. Buy-and-hold / sell-high variants (weekly funds, non-overlapping trades, close-to-close)
8 pre-registered combinations tried: entry {any day, close in bottom 33% of 20-day range} x exit {20 trading days, 40 days, close in top 33% of 60-day range (max 60d), +5% above entry (max 60d)}. Total return = price change + distributions (no reinvestment), net of 20 bps; costs 4 bps adds +16. SPY = SPY held over the same entry/exit dates.
| Entry | Exit | n | avg days | ex-dates | net20 no-reinv | net20 reinvested | win20 % | avg max DD (bps) | worst DD | SPY same dates | half1 | half2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| any | 20d | 1454 | 20 | 3.6 | +38 | +39 | 51 | -964 | -7181 | +139 | -72 | +175 |
| any | 40d | 705 | 40 | 7.1 | +65 | +68 | 50 | -1558 | -7554 | +296 | -82 | +288 |
| any | top60_33 | 2678 | 10 | 1.8 | +20 | +21 | 57 | -467 | -7969 | +68 | -27 | +80 |
| any | +5% | 797 | 35 | 6.2 | +119 | +122 | 67 | -1451 | -8131 | +239 | -27 | +337 |
| low20_33 | 20d | 1201 | 20 | 3.6 | +11 | +8 | 51 | -937 | -6215 | +145 | -88 | +146 |
| low20_33 | 40d | 629 | 40 | 7.1 | +73 | +74 | 49 | -1567 | -7554 | +266 | -89 | +356 |
| low20_33 | top60_33 | 759 | 31 | 5.5 | +100 | +101 | 65 | -1228 | -7762 | +215 | -2 | +263 |
| low20_33 | +5% | 682 | 34 | 6.0 | +77 | +78 | 66 | -1376 | -7762 | +237 | -40 | +277 |
Full-year buy-and-hold of the same funds: average TR -5%, median -9%, 66% negative, vs SPY +17% price. Findings: every hold variant averages positive per trade but is beaten by SPY over the same dates by 100-200+ bps; first-half (Oct-Mar) results are negative or about zero and the gain is all in the second half (a rising-market rebound); average drawdown inside a hold is 5-16%, worst 62-81%. Win rates of 65-67% for the "+5% / top-of-range" exits are partly built in (exit rule waits for a gain, losers time out at 60 days with big drawdowns, and trades still open at the data end are dropped, a bias in favour of the rule). Longer holds do not do worse than short captures on average here (per-trade net rises with days held because price drift in the second half was positive), but erosion shows up in the full-window hold (median TR -9%, 66% negative) and in max drawdowns; per-event capture is smaller in size and also negative to flat. Neither beats SPY. Small-sample flag: 8 variants, one regime, correlated funds.

## 5. Costs and mechanics (Webull; from BROKER_COST_RULES_RESEARCH_14Oct2026.md)
$0 commission; SEC fee $0.0000206 x sell value (~0.2 bps), CAT $0.000003/share, TAF shown $0 (re-check). Real cost is spread/execution: assumed 2 and 10 bps per side. Weekly funds trade at cents-wide spreads on $5-30 prices, so 4-20 bps RT is plausible; not measured. PDT ended 3 Jun 2026 (intraday margin rules from 4 Jun); T+1 settlement and cash-account good-faith rules UNVERIFIED; Webull OpenAPI rate-limit values and automation terms UNVERIFIED (a once-a-week job needs few calls).
Tax (qualitative): a hold of days fails the 61-day qualified-dividend rule, so income is ordinary or return of capital (basis reduction); capital losses on price drop are limited and wash-sale rules apply to weekly re-buying. UNVERIFIED per fund.

## 6. IBKR and Kraken Pro
IBKR (US ETFs, from the broker research doc, verified 14 Oct 2026): IBKR Lite is $0 on US stocks/ETFs for US residents; Pro is Fixed/Tiered with exchange/regulatory fees (stock rates not read, UNVERIFIED), so the cost model is the same: spread dominates, plus regulatory fees. The idea does not change: ex-date drop matches the dividend, so IBKR's extra benefits (better routing, short borrow, API limits 50 req/s TWS, 10 req/s Web API) help execution and automation but cannot create edge. The intraday-margin implementation for IBKR is UNVERIFIED. IBKR spot-FX/credit interest of 3.38% on cash is irrelevant to weekly ETFs. Conclusion same as Webull: not viable as pure capture.
Kraken Pro: crypto spot has no dividends, so there is no ex-date capture. Analogues (UNVERIFIED as strategy, only the mechanics are sourced in the broker doc): perpetual funding paid every 8 h (US) or hourly (EU/other) between longs and shorts, and staking rewards; funding-rate carry means holding spot against a short perp, with costs of 0.02% maker / 0.05% taker on futures plus 0.10-0.40% spot (base tier UNVERIFIED), and derivatives are not available to US persons. Staking terms not researched. Different risk (liquidation, basis); not tested here.

## 7. Conclusion
Weekly dividend capture is not viable: gross edge is about zero (price drops by the dividend), net is negative at realistic costs (-10 bps per event pooled; only 10 of 101 weekly and 0 of 40 non-weekly symbols positive in both halves at ex-open). High yield is paid out of NAV: the higher the headline yield, the worse the total return; two thirds of weekly funds lost money over 12 months. Non-weekly payers pay less per year, about the same per event, and do not capture better. Conditional ideas (5-day dip entry + 2-day exit; hold with top-of-range exit) look better only in the second half of one window, are within multiple-testing noise, and lose to SPY. Before any use: Nasif's explicit approval is required; none is implied.

## 8. Next tests
1. Longer history (2022-26, includes dead/closed funds to remove survivor bias) from a paid or issuer source; measure real bid/ask spreads on ex-dates.
2. Placebo: same entry/exit rules on non-ex weekdays and on SPY, to check the low5_25 +2d result is not just a general short-term rebound.
3. Control for market beta: subtract the underlying stock/SPY return over the same days.
4. Walk-forward on events (fit rule on first half, test untouched second half), with a pre-declared single variant.
5. Re-run nav_erosion_update.py weekly (appends tracker); check issuer notices for ROC characterization and fund closures.
