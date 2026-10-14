# EURUSD M15 mean-reversion: research notes (14 Oct 2026)

Scope: published ideas for a z-score fade strategy (sell stretches against a long MA regime) aiming at higher win rate, smaller drawdown and cost robustness. Read-only research; nothing run on the trading setup. Formulas are standard textbook forms written from memory of the cited sources; the search snippets did not expose full paper text, so verify constants against the full PDFs before coding. Default values are suggestions to test as optional gates, not approved settings. Cost basis: score per Nasif's rules (8 pts/trade unless he states otherwise).

Ranked by expected benefit / effort (highest first).

---

## 1. Deflated Sharpe Ratio (validation)
Two lines: Corrects an observed Sharpe for the number of trials, skew and kurtosis. The right test for "best of many variants" results like ours.
Formula: DSR = Phi( (SR - SR*) * sqrt(T-1) / sqrt(1 - g3*SR + ((g4-1)/4)*SR^2) ), where SR* = sqrt(Var[SR_trials]) * ((1-gamma)*Phi^-1(1-1/N) + gamma*Phi^-1(1-1/(N*e))), gamma = Euler-Mascheroni constant (~0.5772), N = number of variants tested, T = observations, g3/g4 = skew/kurtosis of returns.
Default for EURUSD M15: N = true count of every variant logged in TEST_LOG.txt (do not undercount); report DSR and require p > 0.95.
Source: https://papers.ssrn.com/abstract=2460551 (Bailey and Lopez de Prado, JPM 2014, DOI 10.3905/jpm.2014.40.5.094)
MQL4 use: offline only (Python over TEST_LOG.txt). No EA change.

## 2. Harvey-Liu Sharpe haircut for multiple testing (validation)
Two lines: Converts a reported Sharpe to a t-ratio and adjusts its p-value for the number of prior tests; the haircut is nonlinear, so weak Sharpes get cut hardest.
Rule: t = SR * sqrt(T/252) (annual SR); p_adj = f(p_raw, N_tests) via Bonferroni/Holm/BHY; require p_adj < 0.05 (Holm is a reasonable default).
Default: N = same as above; apply Holm across all variants.
Source: https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF (Harvey and Liu, "Backtesting", JPM 2015)
MQL4 use: offline only.

## 3. Session / time-of-day gate (entry filter)
Two lines: Intraday FX volatility is U-shaped; London/New York overlap is most active, Sydney/Tokyo quietest. Stretches in the quiet session may be noise that does not revert, or spreads may eat the edge.
Rule: allow entries only when hour(server time) in [H_start, H_end]; or skip hours where the average M15 range < k * daily average.
Default: test blocking 00:00-07:00 server time (UTC+2/+3 per your notes; label the clock) and a variant blocking only 00:00-03:00. Keep the existing 8-pt cost in the scoring.
Source: https://causalclaims.trfetzer.com/paper/w12413.html (Ito and Hashimoto, NBER w12413, "Intraday Seasonality in Activities of the Foreign Exchange Markets"); EURUSD-specific: https://dr.lib.sjp.ac.lk/items/04f21dd4-fbb1-4886-84cb-3ea1ce9ce5f5 (short record, check full PDF).
MQL4 use: optional bool input `UseSessionGate`; `if(UseSessionGate && !InSession(TimeHour(TimeCurrent()))) return;` before the z entry.

## 4. OU half-life gate (regime)
Two lines: Estimates how fast the spread reverts. Fast reversion supports the fade; slow or non-reverting regimes (half-life long or negative beta) are skipped.
Rule: regress d(x_t) = a + b * x_{t-1} + e on the price (or z) series over a window W; phi = 1 + b; half-life (bars) = -ln(2)/ln(phi); valid only if b < 0.
Default: W = 500 M15 bars; enter only if 4 <= half-life <= 40 bars; compare with the time stop in idea 6.
Source: https://www.quantstart.com/articles/Basics-of-Statistical-Mean-Reversion-Testing (QuantStart; search returned the URL, content not fully read). Cross-check: OU/AR(1) theory (continuous form, half-life = ln2/theta).
MQL4 use: compute on closed bars only in OnTimer-free code path (once per new bar); `if(hl < HLMin || hl > HLMax) return;`. Watch small-sample bias (OLS can understate speed at short windows).

## 5. Variance ratio gate (regime)
Two lines: Lo-MacKinlay test. VR < 1 means returns reverse over horizon q; VR > 1 means momentum. Use it to skip stretches in trending regimes.
Formula: VR(q) = Var(r_t(q)) / (q * Var(r_t)), where r_t(q) is the q-bar log return; under random walk VR = 1. Heteroskedasticity-robust z-stat per Lo-MacKinlay (1988).
Default: q = 4 (and 8 as a check); window 500 bars; require VR(4) < 1.0 and z < -1.0 to allow fades.
Source: https://www.luxalgo.com/library/concept/stationarity-and-efficiency-tests/ (practitioner summary; the original is Lo and MacKinlay 1988, Review of Financial Studies). Note: sources were thin on FX specifics.
MQL4 use: optional gate computed on closed bars; fast enough to run per bar.

## 6. Time stop (exit)
Two lines: Closes trades that have not reverted within a fixed horizon. Cuts the slow tail that drives drawdown in mean-reversion books.
Rule: exit at market after N bars from entry if not closed by TP/SL; N = k * half-life, or fixed.
Default: N = 2 * half-life, capped 16-24 M15 bars (4-6 h); test N = 12, 24, 48 bars.
Source: no single paper found. Basis: MAE/MFE practice in https://www.luxalgo.com/library/concept/mae-mfe-distributions.md and holding-period analysis in arXiv 2011.02870 (https://arxiv.org/pdf/2011.02870, "Model-free Analysis of Dynamic Trading Strategies").
MQL4 use: store entry bar index per ticket; in the OnTick loop `if(Bars - entryBar >= N) close`. Make it a `UseTimeStop` input; default off until tested.

## 7. Volatility-scaled sizing (money management)
Two lines: Keeps risk per trade constant when volatility changes, which shrinks drawdown from high-vol clusters.
Formula: lots = (RiskFrac * Equity) / (k * ATR(14, M15) * pipValue); with k = 2 for the stop distance in ATR units.
Default: RiskFrac = the current b31 value (do not change without a test); k = 2; cap lots to the existing max.
Source: https://tradingstrategy.ai/glossary/volatility-based-position-sizing (glossary); practitioner backtest on mean reversion (smoother equity, small return change): https://setup4alpha.substack.com/p/how-to-implement-volatility-adjusted (low-quality source; verify).
MQL4 use: replace fixed lot computation with ATR-based lots when `UseVolSizing` is true; keep lot step and min lot checks.

## 8. MAE-based stop placement (exit)
Two lines: Sets the stop from the adverse-excursion distribution of past winners, so stops sit outside normal noise. Caution: tuning tightly to past percentiles is fragile (LuxAlgo warns of this).
Rule: MAE_i = max adverse move from entry in trade i (pips); stop = P_q(MAE of winning trades, in-sample), q = 0.9; in ATR units: stop_ATR = stop / ATR(14).
Default: start with stop = 2.5 * ATR(14) and test q = 0.85-0.95 out-of-sample only.
Source: Sweeney, "Maximum Adverse Excursion" (Wiley, 1997) (book, no URL verified); https://www.luxalgo.com/library/concept/mae-mfe-distributions.md for the percentile method. Note the mean-reversion caveat: high-MAE trades often revert, so tight stops cut winners.
MQL4 use: fixed `StopATRMult` input; the MAE percentile can be computed offline and hard-coded as the ATR multiple, not computed live.

---

## Notes and gaps
- Hurst exponent and rolling variance-ratio sources were thin (TradingView screens and education sites). Hurst is excluded from the top 8 for that reason.
- Quantpedia was not reached by search; no Quantpedia source is cited.
- Idea 2 duplicates idea 1 for multiple testing; use one (DSR preferred) plus Holm as a cross-check.
- All gates must be tested as separate optional inputs on the b22_thu base, logged in TEST_LOG.txt, and scored over the 8 periods per the WIN rule.
