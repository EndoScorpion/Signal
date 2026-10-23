# Anomaly research (cheap pass, 15 Oct 2026) - sources: BIS Triennial 2025, NY Fed FX volume survey Apr 2026, CME/MacroMicro (Nikkei-USDJPY), ECB Econ Bulletin Apr 2026 (oil geopolitics), SSGA (Iran war/energy). ADVISORY ONLY - leads, not proof.
- Volume by place: UK 38%, US 19%, Singapore 11.8% (rising), HK 7%, Tokyo/Sydney smaller. USD on 89% of trades, EUR 29%. => Asia hours are thin for EURUSD, driven by Singapore/HK/Tokyo flows (USDJPY, AUD) not EUR flows. Fits our hour 05 strength / hour 11 weakness (London mid-morning, news-heavy) ideas to test.
- Nikkei <-> USDJPY positively correlated (risk-on: USDJPY up with equities). Reaches EURUSD only through USD leg; test Asia-hour EURUSD z-fade vs USDJPY/Nikkei move (no Nikkei/USDJPY M1 data locally yet - need data).
- Spot volumes fell 9% y/y (NY Fed Apr 2026); EURUSD all-instrument volume -$47.6bn y/y => thinner market, mean reversion may differ vs old years.
- War/oil: oil-geopolitical shocks -> oil +~30%, USD appreciates (safe haven + terms of trade), euro pressured by energy import dependence (ECB, SSGA). Oil ~ $120 peak in 2026 Mideast war. => sells (EURUSD down) aligned with war-escalation days; our sell-only logic may profit from this regime but fades could be stopped out on trend days. Test: flag trades on days oil futures +/-3% (need WTI/Brent daily; Alpha Vantage WTI/BRENT endpoints exist, key private).
- Politics that move forex (checklist to tag in news calendar): tariffs/trade announcements (Apr 2025 spike), elections (US, France, Germany, Italy), central-bank independence/appointments, fiscal/debt-ceiling and budget fights, sanctions/energy deals, EU summits, government shutdown. Add as an event-tag column; compare trade P/L on tagged days.
- Weekend/Sunday-open gaps: thin liquidity, wide spreads; our hours 02-22 exclude them.
NEXT (cloud, cheap): (1) tag high-impact political days in news_calendar_ff.csv titles (Speaks/Summit/Election/Tariff), test P/L; (2) get WTI/Brent daily (public CSV) and test sell P/L on oil +/-3% days; (3) Asia-hour (00-07 server) P/L split by weekday incl. Fri/Sun adjacency.

## Global economic stressors (added, no new search; checklist to tag and test)
- Risk-off / funding stress: VIX spikes, credit spreads (HY OAS), bank failures (Mar 2023), repo/liquidity squeezes -> USD up, EURUSD down; fades against the move get stopped.
- Rate shocks: Fed/ECB surprise, yield-curve inversion/steepening, 2y-10y moves, rate-differential (US-Bund 2y) swings = main EURUSD driver.
- Inflation/energy: oil and gas spikes, Europe energy dependence, CPI surprises.
- Growth scares: PMI/GDP/NFP misses, recession signals, China slowdown, PBoC/yuan devaluation.
- Sovereign/fiscal stress: Euro-area spreads (Italy, France), US debt ceiling/shutdown, downgrades.
- Pandemic/war/sanction shocks and tariffs/trade war; commodity crashes (gold, copper); crypto/dollar-liquidity events.
- Tag days where VIX >30 or daily EURUSD range >2x ATR: compare strategy P/L (our daily range gate b31 already partly does this).
Cheap cloud task: pull public daily series (VIX, HY spread, US2y, Bund2y, WTI) and split sell-logic P/L by stress terciles; report only if a tercile differs >30 pts/trade over >=100 trades.

## Crisis / supply shock / real estate (added)
- Crisis windows to tag: 2008 GFC (Lehman Sep 2008; our history starts 2009), euro debt crisis 2010-12, Covid Feb-Jun 2020 (USD funding squeeze), 2021-22 supply chains + inflation, 2022 Ukraine/energy, 2023 SVB/Credit Suisse, 2025 tariffs. Real-estate stress: US housing/subprime (2007-09), China property (Evergrande 2021+, Country Garden), US housing starts/new+existing home sales, mortgage rates, euro-area construction/PMI, ECB/Fed housing commentary. New Home Sales already showed avg -37 on 15 trades (news test).
- Cloud: tag these windows + housing releases (New/Existing Home Sales, Housing Starts, Case-Shiller, Building Permits) in the calendar and compare P/L; report only if >=100 trades and >30 pts/trade difference.

## Financial-market news tags (added; "sdc" read as USDC)
- Crypto: Bitcoin big moves/ETF flows/halving, exchange failures (FTX Nov 2022, Terra May 2022), stablecoin depegs (USDC Mar 2023 SVB, USDT), stablecoin regulation (GENIUS Act, MiCA), dollar-liquidity/Treasury demand from stablecoins. Link to EURUSD: risk sentiment + USD liquidity; test days BTC daily move >|7%|.
- AI/tech: Nasdaq/megacap earnings (NVDA etc.), AI capex waves, "AI bubble" selloffs (Jan 2025 DeepSeek day) -> risk-on/off, USD flows to US equities; test days Nasdaq daily move >|2.5%|.
- Stocks: S&P/Nasdaq/Nikkei/DAX gaps, VIX spikes, earnings-season weeks, quad-witching/index rebalances.
- Cloud tasks (cheap, public daily CSV only): BTC, S&P500, Nasdaq, VIX, USDC peg; split sell-logic P/L on big-move days vs rest; report only if >=100 trades and >30 pts/trade gap. No local data yet; nothing run locally.

## Commercial / industrial and precious metals / mining tags (added)
- Commercial & industrial: PMIs (ISM, S&P Global, German/French flash), factory orders, durable goods, industrial production, capacity utilization, ifo/ZEW, corporate earnings/guidance, bankruptcies, strikes/supply disruptions, shipping/freight (Suez, Red Sea). Already seen: German ifo avg -42 (18 tr), French Flash Services PMI -98 (15 tr), Durable Goods +167 (17 tr) in the news test.
- Precious metals / mining: gold and silver spikes (safe haven, USD inverse), central-bank gold buying, copper (China growth proxy), mine strikes/disruptions, platinum/palladium supply, miner earnings. Link: gold up often = USD down = EURUSD up (against our sells); test days gold daily move >|1.5%| and copper >|3%|.
- Cloud (cheap, public daily CSV): XAUUSD, XAGUSD, copper, plus PMI/ifo release days from the calendar; split sell-logic P/L; report only if >=100 trades and >30 pts/trade gap. Alpha Vantage GOLD_SILVER_HISTORY and COPPER endpoints exist (key private, not shared).

## Manufacturing / steel / gas / diesel tags (added)
- Manufacturing: ISM/Caixin/HCOB manufacturing PMI, German industrial production and factory orders (euro-area growth read), US durable goods, auto and chip output. Weak German manufacturing = EUR negative (aligns with our sells).
- Steel: steel/iron-ore prices, EU tariffs/CBAM, US steel tariffs (trade-war link), China output curbs.
- Gas: TTF/Henry Hub natural gas, EU storage levels, Russian pipeline/LNG news. TTF spikes hit euro terms of trade (2022 energy crisis = our strongest sell window, +105 pts/trade). Alpha Vantage NATURAL_GAS (Henry Hub) exists; TTF needs a public CSV.
- Diesel/refined products: diesel cracks, heating oil, freight/transport costs; Europe is diesel-short, so diesel spikes feed euro-area inflation and EUR weakness.
- Cloud (cheap): TTF, Henry Hub, Brent, diesel/ULSD daily; split sell-logic P/L on energy-spike days (>|5%| gas, >|3%| oil); report only if >=100 trades and >30 pts/trade gap.

## Retail / consumer, shipping / warehouse / logistics, transportation tags (added)
- Retail & consumer: US retail sales, UoM and Conference Board confidence, GfK/EU consumer confidence, CPI/PCE, personal spending, Black Friday/holiday sales, big-box earnings (WMT, AMZN, TGT). US consumer strength = USD positive.
- Shipping/warehouse/logistics: Baltic Dry Index, container rates (Drewry/SCFI), port congestion and strikes, Suez/Red Sea/Panama disruptions, warehouse vacancy, supply-chain pressure index (NY Fed GSCPI), UPS/FedEx guidance. Ties to the 2021-22 supply-shock window (+103 pts/trade sells).
- Transportation: rail/trucking volumes (Cass freight, ATA), airline traffic and fuel, auto sales, EV news, strikes. Transport weakness = early growth-slowdown signal.
- Cloud (cheap, public daily/monthly series): GSCPI, Baltic Dry, retail sales/confidence release days from calendar; split sell-logic P/L on release days and stress terciles; report only if >=100 trades and >30 pts/trade gap.

## Piracy, weather crises, natural disasters tags (added)
- Piracy / maritime security: Red Sea/Houthi attacks, Gulf of Aden, Strait of Hormuz, Black Sea shipping -> freight and oil spikes, euro energy-import costs (ties to war/oil section).
- Weather: hurricanes (Gulf of Mexico oil/gas output), droughts (Rhine low water = German industry, EU power prices), heat waves/cold snaps (gas demand), floods, El Nino/La Nina (commodity and AUD/NZD effects).
- Natural disasters: earthquakes/tsunamis (Japan Mar 2011: yen spike and G7 intervention, hits USDJPY and risk), volcanic ash (Apr 2010 air closure), wildfires, major insurance-loss events (reinsurer repatriation flows can lift JPY/CHF).
- Test: tag known event dates (Tohoku 2011-03-11, Hurricane Katrina not in sample, Sandy 2012-10, Harvey 2017-08, Ukraine grain/Black Sea, Red Sea attacks from 2023-11, Rhine low water 2018/2022) and compare sell-logic P/L +-1 day. Event list is from memory, verify dates; samples will be tiny, so treat as anecdotal.
- Cloud (cheap): build the dated event list from public sources (NOAA billion-dollar disasters, USGS M7+), split sell P/L; report only if >=100 trades and >30 pts/trade gap, otherwise log as noise.

## Riots / social stress / civil strife, poverty measures tags (added)
- Unrest: riots, mass protests, general strikes (France pension/yellow-vests 2018-19, UK 2011/2024, US 2020, Hong Kong 2019), coups/regime stress, migration crises. Mostly local-currency and euro-area political-risk effects; EUR hit when unrest is in France/Germany/Italy (OAT-Bund and BTP-Bund spreads).
- Social-stress gauges: unemployment and youth unemployment, jobless claims, consumer-confidence lows, inequality (Gini), food/energy inflation (CPI food), cost-of-living indices.
- Poverty measures: World Bank poverty headcount, Eurostat AROPE (at risk of poverty/social exclusion), US Census poverty rate, SNAP/food-bank demand. These are annual and slow, so they are context for regime/long-cycle, not intraday timing; use only as a yearly covariate.
- Cloud (cheap): tag known unrest dates + jobless claims spikes + BTP/OAT-Bund spread widenings; split sell P/L; report only if >=100 trades and >30 pts/trade gap. Annual poverty series: just record as yearly regime labels, no trade-level test.

## Spending cuts / taxes / fiscal tags (added)
- Fiscal: US budget, debt-ceiling and shutdown fights, tax bills (TCJA Dec 2017, 2025 tax law), euro-area budget rules/deficit procedures (France, Italy), German debt-brake reform (Mar 2025 = strong EUR/Bund-yield rally), austerity packages (Greece 2010-15), UK mini-budget (Sep 2022, GBP crash). Fiscal expansion in Germany = EUR positive (against our sells).

## Greed/fear, insider leaks, corruption tags (added)
- Greed/fear gauges: VIX/VSTOXX, CNN Fear & Greed, AAII bull-bear, put/call ratio, CFTC COT (EUR futures speculator net position, extreme = contrarian), retail broker long/short ratios (contrarian). Test: sell-logic P/L by COT/VIX extremes.
- Insider leaks: pre-announcement drift (price moves before a release in the direction of the later surprise), leaked central-bank decisions (ECB/SNB/BoE press leaks), unusual option/FX flows ahead of policy. Local test below: does EURUSD move in the 60 min BEFORE high-impact USD/EUR events predict the 60 min AFTER (continuation = informed flow; reversal = noise)?
- Corruption/scandal: bank scandals (Libor/FX fixing 2012-15), sanctions evasion, sovereign-fraud (Greek stats 2009), political scandals; regulatory fines. Tag dates; mostly EUR-specific risk premia.

## Big equity news; govt contracts / corruption / bribes (added)
- Big equity: mega-cap earnings (AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA; EU: ASML, SAP, LVMH), index gaps (S&P/Nasdaq/DAX/Stoxx50 > |2%|), IPO/M&A megadeals (cross-border M&A = FX conversion flows), buyback/dividend season (euro repatriation), delistings/bankruptcies, index rebalances and quad-witching.
- Forex-linked govt contracts: defense/energy/infrastructure contracts (EU rearmament, LNG deals, US-EU trade deals), sovereign bond mega-issuance (EU joint bonds, German Bund supply), reconstruction funds, central-bank swap lines, government FX intervention (Japan, Swiss), sovereign-wealth moves. Large contract/M&A settlements can create one-sided EUR/USD flow.
- Corruption/bribery/sanctions tags: FIFA/Petrobras/1MDB-type scandals, bank fines and FX-fixing rigging (2013-15), sanction listings (Russia 2014/2022), export-control and tariff exemptions, lobbying/ethics probes of central bankers or finance ministers (e.g. trading-by-officials scandals). Track as dated event flags; effect on EURUSD is indirect (risk premia, EUR-bank stress).
- Data source plan (cheap, public): SEC/ESMA enforcement releases, DOJ FCPA actions, OFAC/EU sanctions lists, GDELT event counts for 'corruption'/'bribery'/'contract' (free daily counts), Alpha Vantage NEWS_SENTIMENT (key private). Build a daily count series, split sell-logic P/L by top-decile days; report only if >=100 trades and >30 pts/trade gap, else log as noise.
- Caution: leak/insider claims are unverified allegations; use dated public enforcement facts only, no named individuals.

## US-EU-GBP trade news; London / UK news (added)
- Trade: US-EU tariff talks and deals (steel/aluminium, autos, digital taxes), US-UK deal, EU-UK TCA/Brexit trade rows, WTO rulings, trade-balance releases (US, EZ, UK). Tariff announcements = sudden-shock class (Apr 2025: sells lost -166 avg on 8 trades).
- London/UK: BoE decisions and MPC votes, UK CPI/GDP/jobs/retail sales, gilt moves (Sep 2022 mini-budget), UK politics (Brexit 2016, snap elections), City/LSE news, FCA enforcement. London is the biggest FX hub (38% of turnover), so London-open (server ~09-10) and fixing (16:00 London = server 18:00) hours carry the largest flows; GBP news moves EURUSD via EURGBP and USD legs.
- Test below: sell-logic P/L when a high-impact GBP event spans the trade.

## GBP / EUR / AUD / EU / Germany / France news (added)
- Local calendar (news_calendar_ff.csv) holds ONLY USD and EUR events (0 GBP, 0 AUD). GBP/AUD/NZD need a new ForexFactory scrape (cloud task). Germany/France events are inside EUR by title (ifo, ZEW, German/French PMI, Bundesbank).
- EU: ECB decisions + pressers, Eurogroup/ECOFIN, EU summits, budget-rule procedures, Commission trade actions. Germany: ifo, ZEW, factory orders, industrial production, debt-brake/fiscal moves, coalition politics. France: PMI, budget/no-confidence votes (OAT-Bund spread), strikes. AUD: RBA, China data (iron ore), Asia-open flows, employment; AUD/NZD move first in the Asia session so they matter for our hour 02-07 trades.
- Cloud task: scrape GBP + AUD + NZD high-impact events (same columns), then split sell P/L on spanning events; report only >=100 trades and >30 pts/trade gap.

## Italy, Belgium, Greece shocks, EU Parliament and member-state news (added)
- Italy: BTP-Bund spread, elections (2013, 2018, 2022), budget clashes with Brussels (2018), bank stress (MPS), Draghi/Meloni government changes. Spanish/Italian spread widenings hit EUR.
- Belgium: Brussels = EU/NATO seat; Belgian govt formation deadlocks (2010-11, 2019-20), Dexia bank rescue (Oct 2011), Euroclear and frozen-Russian-asset decisions (2024-26 sanctions/asset-use rulings = EUR risk premium).
- Greece: 2010-12 bailouts and PSI haircut, 2015 Syriza/referendum/capital controls (Jan-Jul 2015), IMF arrears, Grexit headlines. Local sell P/L: 2010-12 euro-crisis window +1 avg (100 tr); 2015 window +108 avg (47 tr, 74% win) - slow grinding EUR stress helped sells, flat when whipsawed by rescue headlines.
- EU Parliament / members: EP elections (May 2014/2019, Jun 2024), Commission appointments, MFF budget, Next-Gen EU / joint-debt votes, rule-of-law fights (Hungary, Poland), Dutch/Austrian/Nordic fiscal-hawk positions, Eurogroup and EU summit outcomes. Calendar has no Eurogroup/summit rows (0 events) - add via scrape.
- Cloud task: dated list of these events (Wikipedia/ECB timeline), then split sell P/L on +-1 day; report only if >=100 trades and >30 pts/trade gap, else log as noise.

## Hedge funds / big US bank trading, venture capital, mergers and trade talks, antitrust (added)
- Hedge funds & big-bank trading: quarter/month-end rebalancing and WM/Reuters 4pm London fix flows (server 18:00), CTA trend-follower positioning (COT), prime-broker deleveraging (Archegos Mar 2021, LTCM-type), bank trading-revenue prints at earnings (JPM, GS, MS, C - mid Jan/Apr/Jul/Oct, weeks of strong FX volume), SNB/BoJ intervention rumours, stop-hunt clusters near round numbers.
- Venture capital: VC/AI funding rounds and unicorn IPOs = USD risk appetite; funding droughts (2022) and bank-run (SVB 2023). Weak link to EURUSD, context only.
- Mergers & trade talks: cross-border M&A (EUR/USD conversion flows when the acquirer is US buying EU or reverse), megadeal announcements, US-EU / US-UK trade negotiations, tariff deadlines (already a sudden-shock class).
- Antitrust: EU Commission fines on US tech (Google, Apple, Meta, DMA/DSA), US DOJ/FTC suits, merger blocks. EU-vs-US tech fights feed trade-war risk and EUR headlines; fines are announced mostly in London hours.
- Cloud task (cheap): tag month/quarter-end days + 4pm fix hour, bank-earnings weeks, and dated EU antitrust/mega-M&A announcements; split sell P/L; report only if >=100 trades and >30 pts/trade gap. Month-end/fix split can be done from price history alone (no outside data) - do first.

## Monopoly news, FX liquidity news (added)
- Monopoly/market power: dominant-platform and bank-concentration rulings, EU DMA gatekeeper fines, exchange/FX-venue consolidation (EBS/Refinitiv), prime-broker concentration. Indirect; log as dated flags with antitrust.
- FX liquidity: thin-market events (Swiss franc unpeg 15 Jan 2015, GBP flash crash 7 Oct 2016, JPY flash crash 3 Jan 2019, Sunday-open gaps), spread widening at rollover and holidays (US Thanksgiving/Christmas/New Year, UK bank holidays), year/quarter-end funding squeeze (cross-currency basis), Fed repo/swap-line stress, ECB/Fed balance-sheet runoff, NY Fed FX volume falls (spot -9% y/y Apr 2026 = thinner market). Our ATR cap 90 and hours 02-22 exclude the worst thin periods; the tester uses fixed spread, so thin-market cost is NOT modelled (see rollover hour-23 artifact).

## Liquidity-provider / crypto-hack / FX-broker event check (15 Oct, dates from memory - verify)
- 15 crypto-hack + liquidity-provider crises (Mt.Gox, Bitfinex, Coincheck, Binance, Terra, Celsius, FTX, SVB/USDC, Bybit, MF Global, Knight, Archegos, SNB unpeg, FX-fix fines): only the traditional-finance/central-bank shocks moved EURUSD (MF Global day 3.7x range, SNB unpeg 2.4x). Crypto hacks mostly 0.4-1.4x normal range = no link. Sell trades near these dates: 5 total (+614 pts), too few to conclude.
- Broker mergers/crashes/regulation: see report; samples tiny. Real cost risk is broker-side (spreads/leverage caps), not price.

## CFTC / FINRA / regulator restrictions; broker-ownership politics (added)
- Regulators: CFTC/NFA (retail FX leverage 50:1 since Oct 2010, FIFO rule 2009, position-limit and COT rules), FINRA (broker-dealer conduct, pattern-day-trader rule), SEC, ESMA/FCA (CFD leverage caps 2018, bans on crypto derivatives), ASIC/FMA. Tag dated rule announcements; effect on EURUSD price is small (see broker-event check: only the SNB shock moved price), but they change cost/leverage, which our cost model tracks separately (FXOpen leverage-by-balance table still pending).
- Broker ownership/geopolitics: brokers with China-linked ownership (e.g. Webull, per reports; verify) can face US-China political/regulatory risk (listing, data-security, sanctions rules). Treat as DATA-SOURCE risk only: we use Webull MCP for stock bars at most, never for orders (CLAUDE.md: no broker write tools). Prefer sources without such dependency for EURUSD (FXOpen files, public CSVs).

## Billionaire / mega-company news: SpaceX, Tesla, Amazon (added)
- Why it might matter: megacap moves drive Nasdaq/S&P risk appetite and USD equity-inflow flows; single-person announcements can swing index futures and risk sentiment (indirect to EURUSD, mostly via USD risk-on/off). Tesla/Amazon are in the major indices; SpaceX (private, IPO news would be a mega liquidity event).
- Track as dated flags: Tesla (quarterly deliveries 2nd day of Jan/Apr/Jul/Oct, earnings, CEO announcements, political stances), Amazon (earnings late Jan/Apr/Jul/Oct, AWS, Prime Day/holiday sales, antitrust), SpaceX (launches, funding/IPO news, government contracts = link to govt-contract tag), other billionaire-driven events (large share sales/pledges, buyouts, political donations, Fed/Treasury-linked remarks).
- Test (cloud, cheap): daily |moves| of TSLA, AMZN and Nasdaq; tag top-decile days and earnings dates; split sell P/L; report only if >=100 trades and >30 pts/trade gap. Expect noise: weak link.
- Caution: public dated facts only; no claims about individuals' motives or private information.

## Google / search-trend news related to forex (added)
- Sources: Google News feeds on EURUSD/ECB/Fed/tariffs (RSS, dated headlines), Google Trends search-interest for "euro dollar", "recession", "inflation", "bank run", "war" (weekly/daily index; spikes = retail fear/greed gauge). Alphabet itself (GOOGL earnings, antitrust, AI) is a megacap tag.
- Test: Trends spike weeks vs sell P/L; headline-count per day (GDELT/Google News RSS) top decile vs rest. Report only if >=100 trades and >30 pts/trade gap.

## DIVISION OF LABOR (share the work, report only results that pass the gap rule; silent otherwise)
- Coordinator (baa7b9): merge reports, keep this note and queue, ONE batched message per ~15 min, laptop MT4 queue stays single-loop.
- Clone B (chaos/regime): hour 11 weakness + hour 05/08 pocket; Asia-hour thin-liquidity and Friday edge (+83 vs +28) checks; stress terciles (VIX/HY once series are pulled).
- Clone C (calculus/stats): significance work: DSR/day-block bootstrap on every flagged gap, shuffled-entry control (done locally: 5.8 sd), buy 3-down-closes lead DSR.
- Clone D (exits/session): FOMC-only skip + year split, hour-23 long rollover-spread realism, arc_tp200/tp300 replay, month-end/fix hour (fix hour -23 avg, 24 tr).
- Clone G (entry families): buy pullback survivors, buy_scan2 leads, alternative entries on Asia hours.
- Data pullers (whoever has internet first, save to analysis\macro\*.csv, public sources only): GBP/AUD/NZD high-impact calendar scrape; WTI/Brent, TTF/Henry Hub, gold/silver/copper, VIX, HY spread, US2y/Bund2y, BTC, S&P/Nasdaq, TSLA/AMZN; Google Trends; GDELT counts.
- Rules for all: no orders, no live trading, no credentials shared, points not dollars, cost label on every result, tiny samples are anecdotes.

## LOGICAL SAFE METHOD for all tag tests (Nasif: "logical safe method")
1. Pre-register: list tags and the split rule BEFORE looking at P/L; count every split tried (multiple-testing haircut / DSR with N counted).
2. Public, dated, factual sources only; save raw to analysis\macro with source + fetch date; no credentials, no private info, no allegations about individuals.
3. One change at a time; same base trade list (nr_h222 trail, 5.45 pts) for every split so results are comparable; label clock (server time) and cost.
4. Pass rule: >=100 trades, gap >30 pts/trade, same sign in train (70%) and hold-out (30%), >=60% of years agree, survives day-block bootstrap. Anything less = noise, logged not acted on.
5. Proxy lessons (MACD): validate any new gate on the REAL entry set before building an EA clone.
6. Promotion: only passed gaps become ONE-change MT4 clones in the queue (cheapest cost tier first, then 5/6/8), MT4 multi-period decides; backtest is never live approval.
7. Safety: no orders, no live trading, no pause lifting, no touching other sessions' processes, silent mode (<=1 batched message/15 min), cheapest spend (public CSV, no paid calls).
