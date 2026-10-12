# Commission error and fix (12 Oct 2026)

## Final rule
- **EURUSD, FXOpen ECN/STP 5-digit: 6 points max per trade (round trip), charged once.**
- Point = 0.00001, so 6 pts = 0.00006. Flat, regardless of balance or margin.
- Spread 2 pts, swap 0, tax 0, other fees 0, leverage 1:500.
- Non-forex (stocks, perps, crypto, Bloxwap): commission is "unknown" unless sourced (Webull, Kraken Pro, IBKR, old live data). Never invented.
- Every report shows commission points and $ per trade and per lot.

## What went wrong
1. **Double counting.** MT4 tester reports already deduct about $0.08 per 0.01 lot. Early re-pricing subtracted commission again from the report profit column, so results were too low.
2. **8 points.** The first rule (11 Oct) was "8 points max". It was replaced by his later 6-point rule (typed 10+ times on 11 Oct). Reading 8 points as 8 pips (10x too high) also happened once in another thread.
3. **7 / 7.7 points.** Taken from the FXOpen tier page (EUR 3.50 per side per lot, about 7.7 pts at EURUSD 1.10). That page is in EUR, uses balance tiers, and was never stated to replace the flat rule. A second pasted source (5 EUR round trip = 5.5 to 6.0 pts) agrees with 6.
4. **Stale rules relayed between threads**, which cost accuracy.

## How it was fixed
- Double count removed: re-price from raw open/close prices (`fx/commission.py`, mql repo).
- 8 and 7.7 marked superseded in project memory; 6 pts is the rule.
- Win Logic build 049 uses cost class `fx` (pts 6, spread 2); non-forex left unknown.
- Full-history 6-pt runs: `results/COMMISSION_6PT_FULL_20261011.md`, `results/EA_6PT_FULL_TABLE_20261012.xlsx` (6-pt net = 8-pt net + 2 pts x trades).

## How to avoid it again
- Check project memory and `results/COMMISSION_STATEMENTS_NASIF_20261011.md` before any cost run.
- Never subtract commission from an MT4 report profit; re-price from raw prices.
- If the owner says otherwise, ask before changing.
