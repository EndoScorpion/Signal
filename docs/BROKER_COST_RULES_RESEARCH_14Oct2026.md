# Broker cost and rules research (for backtest cost models)
Written 14 Oct 2026. Facts only, not investment advice. "Verified" = page read on 14 Oct 2026 via web scrape/search. UNVERIFIED = not confirmed from a primary source; check before relying on it.
Scope note: only public marketing/docs pages were read; account-specific terms (client agreements) were NOT read.

## 1. FXOpen (ECN, EURUSD, MT4)

### 1.1 Entities and regulators (verified 14 Oct 2026)
- FXOpen EU Ltd: CySEC licence 194/13 (https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/37576/ ; https://fxopen.com/en-cy/why-us/).
- FXOpen UK: FCA authorised (third-party: https://www.daytrading.com/fxopen). Sites: fxopen.com/en-gb, /en-hk, /en-ae/professional.
- FXOpen INT (international, fxopen.com/en): leverage up to 1:500, 0.01 lot min (https://fxopen.com/en/).
- Mauritius / Malta / Mauritania recollection: NOT found in any source read. UNVERIFIED. Do not derive a time zone from it; use the server-time evidence below.
- Entity migrations (clients moved between UK/EU/INT): no source found. UNVERIFIED. The entity of Nasif's account determines commission table and leverage.

### 1.2 Server time (MT4), verified 14 Oct 2026
- GMT+2 in winter, GMT+3 in summer, switching on the US-style DST dates (spring Sunday: 9 Mar 2025, 8 Mar 2026).
  - https://fxopen.com/en/news/fxopen-to-switch-to-daylight-saving-time-on-march-9th-2025/
  - https://fxopen.com/en-hk/news/fxopen-to-switch-to-daylight-saving-time-on-march-8th-2026/
  - https://fxopen.com/en-gb/news/fxopen-mt4-server-time-is-changing-to-gmt-3/
  - https://fxopen.com/en-hk/news/fxopen-uk-server-time-changes-to-gmt-2/ (31 Oct 2016: FXOpen UK servers revert to GMT+2 from Mon 7 Nov 2016; open orders unaffected; advises adjusting indicator/EA time settings)
  - Support FAQ https://support.fxopen.com/portal/en/kb/articles/faq-terminal-metatrader-4 (MT4 cannot show local time; spring = GMT+3). Only the snippet was read.
- Sept 2026 holiday notices still quote GMT+3 (https://fxopen.com/en/news/trading-hours-schedule-for-us-labor-day/), consistent with summer time. Autumn 2026 switch-back date: not read, UNVERIFIED (expected around first Sunday of Nov by the US rule; verify).
- Pre-2016 offsets, years where EU vs US DST dates differed, any one-off changes: UNVERIFIED. Matches memory note "UTC+2/+3 US DST". Label clocks in every dataset.
- Backtest fields: server_offset by date (with exact switch dates), session open/close in server time, holiday short days.

### 1.3 Commissions (verified 14 Oct 2026; https://fxopen.com/en/pricing/ modified 22 Jul 2026; UK/AE variant https://fxopen.com/en-ae/professional/pricing/)
- ECN FX, per 1 standard lot (100k), PER SIDE, by account balance: under $1,000 = 3.50; $1k-25k = 2.50; $25k-250k = 1.80; over $250k = 1.50.
- Volume discount matrix on 30-day traded volume (USD equivalent): under $5M, $5-25M, $25-250M, over $250M. Rate can change monthly with volume and equity at recalculation time.
- For pairs whose base currency is not USD the commission is in BASE CURRENCY units (EUR for EURUSD). Hypothesis (UNVERIFIED): this may explain 5 pts RT (2023-24) vs 8 pts RT (2025-26): EUR 2.50/side x2 = EUR 5 RT (about 5 pts), EUR 3.50/side x2 = EUR 7 RT (about 8 pts at EURUSD ~1.15). Check real deal commissions in account history before fixing the model.
- Jun 2020 news: half-turn commission $3.5/lot for deposits up to 1,000 USD and volume up to 5M (https://fxopen.com/en/news/fxopen-improves-trading-conditions-on-ecn-accounts/). Earlier history: not read, UNVERIFIED.
- Other products: index CFD $0; commodity CFD same table as FX; US shares/ETF 0.1% (min $1/order); crypto CFD 0.1% on MT4/MT5 at low balance. TickTrader has a separate, lower schedule for limit orders.
- Fields: commission_per_lot_per_side, commission currency, tier by balance and 30-day volume, rounding, variable ECN spread, slippage.

### 1.4 Swaps / swap-free
- Swap per instrument in MT4: Market Watch > Specification (swap long / short). Past swap tables are not published; use account statements (verified, pricing page).
- Islamic/swap-free account on request (support@fxopen.com). Instead of swap an additional commission equal to the swap is charged at rollover, so it is not cost-free (verified, same page).
- Triple-swap weekday and rollover time: not read, UNVERIFIED. Spread widening at rollover: not documented in sources read.
- Fields: swap_long, swap_short, triple-swap day, rollover time (server clock), swap-free surcharge.

### 1.5 Platforms
- MT4 and MT5 both offered; MT5 hedging launched on ECN accounts (https://www.metatrader4.com/en/company/479, date not read).
- Minimum builds enforced from 1 Dec 2023: MT4 build 1380, MT5 build 3802; 64-bit installers only (https://fxopen.com/en/news/important-updates-for-mt4-and-mt5/, 28 Nov 2023, verified).
- Any FXOpen announcement retiring MT4: none found. UNVERIFIED. Keep the MT5 port plan.
- TickTrader platform/API also offered.

### 1.6 Not confirmed (all UNVERIFIED; read client agreement/support)
- Leverage by entity: INT shows up to 1:500. EU/UK retail FX is capped at 1:30 by regulation (general knowledge, FXOpen pages not read).
- Margin call and stop-out levels.
- Scalping/EA rules (minimum holding time, EA ban): none found; FXOpen markets itself as true ECN.
- Weekend gaps: real market gaps (close Friday evening, reopen Sunday night); check that history has Sunday bars on the server clock.
- News restrictions: none found.
- Holiday short-day notices published per holiday (times in GMT+3); mostly CFDs/metals.
- UK site risk warning: "60% of retail investor accounts lose money when trading CFDs with this provider" (verified on en-hk page).

### 1.7 History data
- Own MT4 history / broker quotes (patchwork per memory), QuotesDownloader. Other tick sources (Dukascopy etc.) not evaluated here.
- Keep clock labels (GMT+2/+3), commission records per period, spread series.

## 2. Webull (US)

### 2.1 Commissions and fees (verified 14 Oct 2026; https://www.webull.com/pricing, https://www.webull.com/pdt-info)
- US stocks, ETFs, options: $0 commission. Certain index options $0.50/contract; oversized option orders $0.10/contract (https://www.webull.com/help/faq/10954-Day-Trading-Rules, snippet).
- Pass-throughs: SEC fee $0.0000206 x sale value (sells); FINRA TAF shown as $0; CAT fee $0.000003 per share (buys and sells). Rates change; re-read before use.
- Equity algo order types: $0.005/share.
- Futures: "as low as $0.25" per contract plus exchange fees; $500 minimum shown. Crypto fee schedule: not read, UNVERIFIED.
- Revenue lines: payment for order flow, stock lending, cash interest, margin interest. Execution quality vs NBBO is an implicit cost to model.
- Outgoing stock transfer $75; OTC low-priced securities fees (pricing page).

### 2.2 PDT, margin, settlement
- Old PDT rule ended 3 Jun 2026; replaced 4 Jun 2026 by intraday margin rules: no $25k minimum, no day-trade count limit, no PDT flag; margin calls become Intraday Margin Deficit calls (https://www.webull.com/pdt-info, verified). SEC/FINRA rule text not read.
- Margin rates: Standard vs Premium subscription rates; values not read, UNVERIFIED.
- US equity settlement T+1 (since 28 May 2024): general knowledge, UNVERIFIED here. Cash-account good-faith/free-riding rules not read.
- Dividend capture (model items): ex-date price drop about the dividend, dividend on pay date, withholding tax for non-US persons, short positions owe the dividend, qualified-dividend holding period for tax, spread/slippage on both legs.

### 2.3 API and data (verified 14 Oct 2026)
- Webull OpenAPI: market data (real-time quotes, historical candlesticks), trading, futures and crypto support since 13 Dec 2025, sandbox (https://www.webull.com/open-api ; https://developer.webull.com/apis/docs/ ; https://developer.webull.com/apis/docs/changelog/).
- Rate Limits page added 14 Aug 2026, HTTP 429 on excess (https://developer.webull.com/apis/docs/rate-limits; values not read, UNVERIFIED).
- Auth: signed requests (HMAC-SHA1 headers), access token with 2FA. Eligibility and automated-trading terms: not read, UNVERIFIED.
- Futures historical bars: GET /market-data/futures/bars/list (timespan e.g. M1, count 200 in the example); maximum depth UNVERIFIED.
- Paper trading with OpenAPI multi-asset simulation announced (https://www.prnewswire.com/news-releases/webull-unveils-enhanced-paper-trading-experience-with-professional-grade-and-openapi-multi-asset-simulation-302830191.html; date not read).
- 24/5 trading for select stocks/ETFs.
- Fields: commission, per-share regulatory/CAT fees, futures per-contract + exchange fees, margin interest, borrow fee, spread/slippage, session, settlement lag.
- History: Webull API bars (limits unverified) plus independent vendors; adjust for splits/dividends.

## 3. Interactive Brokers (IBKR)

### 3.1 Commissions (verified 14 Oct 2026; https://www.interactivebrokers.com/en/pricing/commissions-home.php)
- Fixed: single rate per share/contract with min/max. Tiered: lower base rate falling with monthly volume, exchange/regulatory/clearing fees passed through (rebates possible). Exact stock rates not read, UNVERIFIED.
- IBKR Lite: $0 on US stocks/ETFs for US residents; IBKR Pro: Fixed/Tiered. Paper trading on both (https://www.interactivebrokers.com/en/general/compare-lite-pro.php).
- Spot FX: commission on trade value, USD 2 minimum per order at lowest tier, falling to 1.50 above 1B, 1.25 above 2B, 1.00 above 5B monthly (third-party https://www.forexbrokers.com/reviews/interactive-brokers; official https://www.interactivebrokers.com/en/pricing/commissions-spot-currencies.php, snippet only). That review measured EURUSD average spread 0.226 pip and all-in 0.626 pip round turn per standard lot ($4 commission): third-party measurement.
- Interest snapshot: USD credit 3.38%, margin loans from 4.38% (changes with benchmark).
- Market data fees: https://www.interactivebrokers.com/en/pricing/market-data-pricing.php (not read).

### 3.2 API (verified 14 Oct 2026)
- TWS API via TWS or IB Gateway; Web API / Client Portal; FIX.
- TWS pacing: about 50 requests/s (market data lines / 2), scales with lines; FIX via Gateway 250 msg/s (https://www.interactivebrokers.com/docs/tws-api/doc/pacing-limitations/introduction).
- Web API: 10 requests/s per username, 429 on excess; one brokerage session per username (https://www.interactivebrokers.com/campus/ibkr-api-page/web-api-trading/).
- Historical data (https://interactivebrokers.github.io/tws-api/historical_limitations.html): max 50 simultaneous requests; identical requests within 15 s, or 6+ requests per contract/exchange/tick type within 2 s are pacing violations; BID_ASK counts twice; bars of 30 s or less only for last 6 months; hard limit for 1-min+ bars lifted but soft throttling remains; expired futures older than 2 years after expiry unavailable; delisted securities unavailable.
- Automated-trading terms (order-to-trade ratios, messaging fees): not read, UNVERIFIED.

### 3.3 PDT / margin / paper
- US PDT replaced by intraday margin industry-wide per Webull (effective 4 Jun 2026). IBKR implementation not read: UNVERIFIED.
- Paper trading fills are simulated and optimistic; plumbing test only, not cost evidence.

### 3.4 MT4/MT5
- IBKR MT4/MT5 availability: not checked, UNVERIFIED (believed not offered; confirm).

### 3.5 Fields
- Commission (fixed/tiered, min/max per order), exchange + regulatory + clearing fees, FX commission with minimum and spread, market-data fees, margin interest by currency, borrow fee, SEC/TAF, withholding, dividends, slippage by order type, session.
- History: IBKR historical API (limits above) plus vendors.

## 4. Kraken Pro

### 4.1 Spot fees (verified 14 Oct 2026; https://www.kraken.com/features/fee-schedule)
- Maker/taker by 30-day USD volume (page scrape): $0+ 0.40/0.80; $2.5K+ 0.30/0.60; $10K+ 0.22/0.38; $25K+ 0.20/0.35; $50K+ 0.15/0.30; $100K+ 0.12/0.25; $250K+ 0.10/0.22; $500K+ 0.08/0.20; $1M+ 0.06/0.18; $2.5M+ 0.04/0.15; $5M+ 0.02/0.12; $10M+ 0.00/0.10; Pro tiers down to 0/0.05 at $500M+.
- CONFLICT: other pages (https://www.kraken.com/learn/kraken-vs-kraken-pro, bitsgap, bitdegree) give base tier 0.25% maker / 0.40% taker. Open the page in a browser to see which table applies. Base tier UNVERIFIED between 0.25/0.40 and 0.40/0.80.
- Stablecoin/pegged/FX pairs: 0.20% at base, falling to 0/0.001%.
- xStocks (tokenised equities): maker 0%, taker 0.08% at base; region-restricted.
- Futures: maker 0.02% / taker 0.05% under $5M 30-day volume, down to maker rebates (-0.003% to -0.006%) and taker 0.0125% (https://support.kraken.com/articles/360048917612-fee-schedule). Spot volume can also set the futures tier.
- Kraken (simple app) is flat 1% + spread; Pro is maker-taker.

### 4.2 Funding / perpetuals (verified 14 Oct 2026; https://www.kraken.com/learn/futures-trading-funding-rate-strategy, 18 Jun 2026)
- Funding every 8 h for US perpetuals; hourly in EU and other regions (per Kraken). Public historical funding endpoint https://docs.kraken.com/api-reference/historical-funding-rates/historical-funding-rates (example shows 4-hour samples; interval by product UNVERIFIED).
- Leverage: up to 100x on BTC/ETH in ROW, 10x in EU. UK: crypto derivatives for professional clients only; EEA: MiFID II appropriateness; Australia: wholesale only; US via NinjaTrader per the article; others via Payward Digital Solutions Ltd (Bermuda).
- Fields: maker/taker by tier and instrument, funding per interval (sign by side), mark vs last price, liquidation/margin rules, leverage cap by entity.

### 4.3 API and limits (verified 14 Oct 2026)
- REST, WebSocket, FIX (https://www.kraken.com/pro/trading-api); derivatives "not available in the U.S. or to U.S. persons".
- Futures REST: budget 500 per 10 s (send/edit/cancel cost 10, batch 9+size, openorders 2); /history pool 100 tokens refilling 100 per 10 min; WebSocket 100 requests/s (https://docs.kraken.com/exchange/guides/futures/ratelimits). Error apiLimitExceeded.
- Spot REST call-counter and matching-engine limits: https://docs.kraken.com/exchange/guides/rest/ratelimits and https://docs.kraken.com/exchange/guides/general/ratelimits (not read, UNVERIFIED values).
- Spot OHLC depth per call (commonly 720 candles) and full Trades history: UNVERIFIED here.

### 4.4 History
- Kraken public Trades/OHLC endpoints, futures historical funding endpoint; third-party archives not evaluated.

## 5. Common cost-model template
- Instrument: tick size, contract size, min lot, lot step.
- Spread: time-varying (hour, rollover, news); prefer bid/ask history.
- Commission: per side, currency, tier by balance/volume, minimum per order.
- Swap/funding/borrow: sign by side, rollover time, triple days, interval, rate source.
- Slippage: by order type and liquidity.
- Clock: server offset with DST dates.
- Margin: leverage by entity, margin call/stop-out, intraday vs overnight.
- Rules: PDT/intraday margin, settlement, holidays, regional limits, API rate limits.
- Data: bid vs mid, gaps, split/dividend adjustment, survivorship, weekend gaps.

## 6. Open items to verify next
1. FXOpen: real commission currency and amount in deal history 2023-26; autumn 2026 server-time switch date; pre-2016 offsets; entity of Nasif's account.
2. FXOpen client agreement: scalping/EA, stop-out, leverage by entity, MT4 retirement plans.
3. Kraken: resolve base-tier spot fee conflict.
4. IBKR: official Fixed/Tiered and FX pages; automated-trading terms; intraday margin implementation; MT4/MT5.
5. Webull: rate limits, API eligibility/terms, crypto fees.
