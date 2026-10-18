# /backtest — Run net-of-costs backtest on local MT4 history CSVs

Primary engine: `node tools/w2_node_fx.js` (FX) / `w2_node.js`
Fallback: `python3 backtest_costs.py` (stocks/ETFs)

## Steps

1. Check disk: `df -h .` — warn if <2GB free.
2. Run: `python3 run_backtest.py`
   - Auto-finds CSVs in `C:\Users\endos\Desktop\hst_out\` first, then MT4 history folder, then `data/history/`
   - Calls `node tools/w2_node_fx.js <csv>` per file
   - Writes `results/cli_backtest_<date>.md`
   - Copies to `/mnt/project-files/results/` if mounted
   - Auto-commits and pushes to current branch
3. Done — check `results/cli_backtest_<date>.md`

## Override examples
```
python3 run_backtest.py --csv "C:\Users\endos\Desktop\hst_out\EURUSD*.csv"
python3 run_backtest.py --engine python --hold 5 --group fx
```

## Data prep
- MT4: export HST as CSV (date,open,high,low,close,volume) into `C:\Users\endos\Desktop\hst_out\`
- Or drop files in `data/history/` as fallback
