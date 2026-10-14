# Bridge note: commission test plan (cloud fork a4rtsd, 2026-10-14)
For any session that cannot take direct messages (phone chat, Project docs). Read AGENT_RULES_READ_FIRST.md first.
Backtest only. No orders. One MT4 test at a time, via the single loop or Nasif. Never overwrite files.

## Run order (label every number with its cost)
1. 5pt  : 5 pts round trip + avg spread/2 (current loop scoring)
2. 6pt  : 6 pts max (sp6), stress case. Never mix with 5pt results.
3. tiered: FXOpen published ECN FX commission at sim balances, SimDeposit with UseLotSim=1, leverage cap 500:1.

## Test 3 grid (published per side per lot; round trip assumes USD, 1 pt = $1/lot)
| Bracket       | Per side | RT pts (USD) | Cushion (+10%) | Edge   |
|---------------|----------|--------------|----------------|--------|
| < $1k         | 3.50     | 7.0          | none           | none   |
| $1k - $25k    | 2.50     | 5.0          | ~$1.1k         | $1k    |
| $25k - $250k  | 1.80     | 3.6          | ~$27.5k        | $25k   |
| > $250k       | 1.50     | 3.0          | ~$275k         | $250k  |
Run label: tier<pts>@<balance>.

## OPEN DECISION (Nasif): USD or EUR?
FXOpen's trading-accounts page says commission on pairs with a non-USD base is charged in the base currency, so EURUSD = EUR 3.50/2.50/1.80/1.50 per side. At ~1.17 that is ~8.2/5.9/4.2/3.5 pts round trip (rate is an estimate). Nothing is queued until Nasif picks.
Rate also depends on 30-day traded volume (support article). Leverage rule: unverified, left out.

## Shadow ledger (post-processing, no extra MT4 runs)
Keep tester fixed cost AND a per-trade fxopen_real_cost column from a cost model file (balance, account type, swap, brackets). New file per test, e.g. data/fxopen_shadow_<test>.csv. Report net after real cost.

## Visual
Artifact "Commission Test Plan": https://claude.ai/artifact/Pk9BqQAkL9d46w6Q3kXohQ (private, owner only)
