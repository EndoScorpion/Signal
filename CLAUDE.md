# Signal Live Companion v0.01d (build 039) - Claude Code handoff

GOAL: use autonomous agent + planning mode to (1) pull sandbox/real daily history for every symbol, (2) re-test all win rules NET OF COSTS, (3) feed the surviving rules back into the HTML app.

## Hard rules
- NEVER place orders. No broker write tools. Research and files only.
- Every result must be net of costs: spread, slippage, regulatory fees, commission, swap/financing, taxes. Use cost_model.json - one source of truth (mirrors window.slcCost in app_addons/addon29.html).
- Safe chunks: <=3 symbols per request, 120 ms pause, stop at 75% memory. Resume from data/history/*.csv (skip symbols already present).
- Report win% AND avg net %/trade AND n AND per-period (2015-19, 2020-22, 2023-26). Reject rules with n<30 or inconsistent periods. Past results are not advice.
- Do not trust survivor-only data (Shibui) for edge claims; flag it.

## Data sources (try in this order, auto-fallback, log which worked)
1. Webull MCP get_stock_bars (symbols<=3, timespan D, count up to 1000)
2. Shibui Finance MCP (call get_database_schema + get_query_patterns first; shibui. prefix; LIMIT<=200; DuckDB)
3. fetch_history.py (Yahoo chart -> yfinance (pip install yfinance) -> Stooq -> Alpha Vantage with ALPHAVANTAGE_KEY env var). Run: python3 fetch_history.py SPY QQQ ULTY
4. Files the user drops in data/import/ (CSV symbol,date,open,high,low,close,volume)

## Workflow
1. Enter plan mode. Read PLAN.md. Propose the run before executing.
2. python3 fetch_history.py --universe universe.txt --out data/history
3. python3 backtest_costs.py --data data/history --hold 3 --cost cost_model.json  -> results/rules_net.csv
4. Keep only rules positive net of costs and tax in >=2 of 3 periods; write results/SURVIVORS.md
5. Update app_addons/addon37.html RULES / addon36.html RULES from survivors, then: cd app_addons && python3 gen_kit.py && python3 build.py (needs base HTML; ask user for companion_v0.01d_build038.html base if missing)
6. Back up key code as .txt (user preference) into backups/.

## Known findings so far (gross unless stated)
- Crypto H1 dip-rebound BUY R1-R4: hold 4 bars, hard stop 1.5%; unseen coins n=859 win 58% avg +0.33% at 0.04% cost, +0.25% at 0.12% cost. Re-check with full cost model.
- Daily stocks/ETFs/metals: no consistent edge yet; weak lead = below Bollinger & Stoch<10 in uptrend, 3d hold, blue chips.
- Dividend capture is zero-sum pre-cost (price drops ~ dividend). Only pays if price recovers; costs+tax usually eat it.
