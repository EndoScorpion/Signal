# /backtest — Run net-of-costs backtest on local CSV history

Run the Signal backtest engine against MT4 CSV exports in `data/history/`.

## Steps

1. Check disk: `df -h .` — warn if <2GB free.
2. Run: `python3 backtest_costs.py --data data/history --hold 3 --cost cost_model.json --group fx`
3. Write results to `results/cli_backtest_<date>.md`.
4. If `/mnt/project-files` is mounted: `cp results/cli_backtest_*.md /mnt/project-files/results/`
5. Commit: `git add results/ && git commit -m "backtest results <date>"`
6. Push: `git push -u origin claude/project-thread-tvyda9`

## Override args
Pass args after the command to override defaults, e.g.:
`/backtest --hold 5 --group stock`
These are forwarded to `backtest_costs.py`.

## Data prep
If `data/history/` is empty, run first:
`python3 fetch_history.py --universe universe.txt --out data/history`
or drop MT4-exported CSVs (columns: date,open,high,low,close,volume) into `data/history/`.
