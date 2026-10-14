# Yield-parking plan for idle cash (stablecoin savings, e.g. Coinstancy) - DRAFT 2026-10-14
Status: PLAN ONLY. Nothing deposited, no account opened, not investment advice. All claims below about Coinstancy come from text Nasif pasted (which cites only coinstancy.com itself) and are UNVERIFIED by us.

## Claimed terms (from pasted text, unverified)
- Product: "Dollar Savings" on USDC, advertised fixed 7.50% APY, "subject to revision", accrues per second, auto-compounds.
- Minimum 10 USDC; no deposit/yield/withdrawal fees (network fees apply); withdrawals at any time, normally settled within 48 calendar hours.
- Custody: deposits go first into a multisignature wallet operated by the company, then are deployed into on-chain strategies.

## Why 7.5% needs scrutiny (risk checklist before any deposit)
1. Source of yield: a fixed rate far above US T-bill / money-market rates implies credit, smart-contract, or leverage risk. Ask: which strategies, which protocols, what leverage, who bears losses?
2. Counterparty/custody: company-operated multisig = you hold an unsecured claim on the company, not your coins. No deposit insurance (not FDIC/SIPC) unless proven otherwise.
3. Legal/regulatory: which entity, jurisdiction, licence/registration, whether it is available to Nasif's residence; terms of service, bankruptcy treatment of customer assets, rehypothecation clause.
4. Track record: age, audits (smart contracts + proof of reserves), team identity, incident history, independent reviews; search for complaints and withdrawal-delay reports.
5. Stablecoin risk: USDC depeg risk, issuer, redemption path; "fixed APY" can be revised at will.
6. Liquidity: 48h withdrawal window; stress behaviour (gates, queues) unknown.
7. Operational: network fees, on/off-ramp cost and delay (USD -> USDC and back), tax treatment (interest is likely taxable income when accrued/received - confirm with a tax professional).
8. Concentration: never size so that a total loss changes your plans; keep trading capital, FXOpen margin and required monthly-trade balance separate.

## How to compare it (cost/yield model fields)
yield_quoted, yield_is_fixed, compounding, fees_in/out, withdrawal_delay_days, custody_type, insured (Y/N, by whom), regulatory_status, strategy_description, audits, track_record_years, tax_treatment, on/off-ramp cost, depeg_risk.
Alternatives to benchmark against (rates to be fetched and dated before comparing, none assumed here): broker cash sweep / money-market fund at IBKR or Webull, US T-bills, Kraken staking/earn products (restrictions by region, check), high-yield savings.

## Plan (offline, in this order)
1. Due diligence report (research agent, public sources only): entity, licence, audits, reviews, strategy disclosures, terms of service, withdrawal history; mark UNVERIFIED items.
2. Build the comparison table above with dated rates for at least 4 alternatives.
3. Expected-value sketch: yield minus (probability of loss x severity) at several loss assumptions (1%, 5%, 20% yearly total-loss probability) to show how little risk the 7.5% pays for versus T-bills.
4. Position-size rule proposal: small test amount only, after steps 1-3, only by Nasif's own decision and action; Claude never moves funds or enters credentials.
5. Review monthly: check rate revisions, withdrawal tests (small withdrawal test), news.

## Link to trading projects
Yield on idle balance does not change strategy edge; it only lowers the opportunity cost of waiting. Keep the FXOpen balance tier (commission schedule) and the one-trade-per-month requirement in mind when deciding what to move where.
Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>.

Estimator: data\yield_estimator.py (python -E -P yield_estimator.py principal apy_pct days loss_prob_pct loss_severity_pct). Example: 7% APY per-second compounding, 30 days = +0.558% ($5.58 per $1,000); 7.5% = +0.596% ($5.96).

## Side-by-side on $20,000, one month (2026-10-14, rough; weekly-div numbers from the 2-fund Apr-Oct 2026 study, n=26, UNVERIFIED/unstable)
- Stablecoin savings 7.0-7.5% APY: +$112 to +$119 gross; ~+$29 expected if 5%/yr chance of total loss.
- Weekly capture (buy before ex-date, sell ex-open), ~4.3 events: +$60 to +$112 at 4 bps round-trip cost, but -$26 to -$77 at 20 bps; per-event st.dev ~$500 (monthly ~$1,000), worst single trade -$940 to -$1,460.
- Hold the weekly fund through ex-dates (YMAX/ULTY Apr-Oct 2026 price+distributions, not a forecast): about +3.5%/mo (YMAX) and +2%/mo (ULTY) = ~$700 / ~$400 per month on $20k, with full market and NAV-erosion risk; payouts shrinking.

**CORRECTION (broad study, 101 weekly ETFs + 49 control, Yahoo data, 2 yrs to 13 Oct 2026, survivors only):** the 2-fund hold figures above (YMAX +3.5%/mo, ULTY +2%/mo) are NOT typical. Of 98 weekly funds with a full year, 66% had negative total return, median -9% (price avg -46%, distributions avg +41%) vs SPY +17%. Weekly capture pooled at ex-open: +5.7 bps/event at 4 bps cost, -10.3 bps at 20 bps cost; only 10/101 funds positive in both halves (chance level). See docs\WEBULL_WEEKLY_DIV_CAPTURE_STUDY_14Oct2026.md and data\nav_erosion_tracker.csv.
