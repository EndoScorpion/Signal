# Notes
- MetaTrader 4 Experts folder (user's PC, not reachable from the cloud session):
  C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\MQL4\Experts

## Shared handoff for all threads (updated 11 Oct 2026)
Repos: Signal (this one: daily data, costs, paper bot, FX sim) and MQL (other session: app builds 04x, intraday winners). Contract between them: `results/winners.csv`
(symbol,timeframe,rule,entry_condition,hold_bars,n,win_net_pct,avg_net_pct,periods_ok) + identical `cost_model.json`. Merge by copying files; no code merge.
Hard rules: NO live orders from any automated session (Webull and FXOpen accounts are LIVE). Paper/local simulation only. Never put API keys in chat or files.
Findings so far (all in-sample, small n, no proven edge):
- Daily RSI/Bollinger rules S1/S2: positive in 2023-26 only; need 2015-19 data (yfinance on user PC) + 60/20/20 walk-forward.
- MetaQuotes sample EAs (Star/Doji x4 confirms, Hammer/Hanging Man): nothing qualifies (tiny n, shorts lose). Head&Shoulders: inverse H&S buy looks good at k=5/8, flat at k=3 (fragile); top H&S sells lose.
- User's MQ4 EURUSD scalpers: TP 8 / SL 290 pts. With FXOpen ECN commission (<$1000: EUR 3.50/side ~7.7 pts RT; $1k-25k: 2.50/side ~5.5 pts) break-even win rate is 99.9% / 99.2%, above the claimed 98%. See results/mq4_scalper_analysis.md.
- FXOpen: min deposit $100, 0.01 lot, leverage up to 1:500 (INT entity) but FXOpen EU/UK retail = 1:30 (user's MT4 folder says FXOpenEU-ECN: verify). Islamic account = extra commission equal to swap.
Pending / next:
1. User converts MT4 EURUSD1.hst with `py hst_to_csv.py ... --from 2023-01-01 --split-year --zip` and attaches the zip; then run `fx_scalp_sim.py <csv> --comm 7.7` (and 5.5), compare fixed vs trailing vs rollover-flat exits, use per-bar spread column.
2. User runs fetch_history.py with yfinance for 2015-19 daily data; rerun backtests + walk-forward.
3. MQL session exports winners.csv in the contract format; run its rules through the same split.
Tools in repo: backtest_costs.py, paper_bot.py (--winners), signal_paper_lab.html (offline), hs_pattern.py, test_mq5_family.py, fx_scalp_sim.py, hst_to_csv.py. All have .txt copies in backups/.

## Session links (remembered 11 Oct 2026)
- This session (Signal, "Resume from handoff"): https://claude.ai/code/session_01QiXsPubSeJzFboiisYu8tD
- MQL session ("Planning mode and win logic", MQL repo, branch claudeai/friendly-heisenberg-bfo0sc, PR #1): https://claude.ai/code/session_01EGmAMAxLXRAU9ypfciCQ6w
- Signal draft PR: https://github.com/EndoScorpion/Signal/pull/3
- 11 Oct 2026: a note about the winners.csv contract and the live-account no-orders rule was posted into the MQL session at the user's request.
