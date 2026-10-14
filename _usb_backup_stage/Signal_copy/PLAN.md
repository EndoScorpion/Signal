# Plan for the agent
1. Build universe.txt from the app (Settings: slcMD lists) or ask the user to paste symbols.
2. Fetch history in chunks of 3, resumable. Log failures to results/fetch_log.txt, auto-fallback per symbol.
3. Run cost-aware backtests (backtest_costs.py). Compare each rule to the all-days baseline net of the same costs.
4. Walk-forward: tune on oldest 60%, validate on next 20%, final test last 20% untouched.
5. Write SURVIVORS.md with n, win%, avg net, after-tax avg, per-period table.
6. Patch app rules, rebuild, run Playwright smoke tests, publish.
Stop and ask the user before: anything touching accounts, orders, or credentials.
