# Deep EURUSD Research — Macro, Structural & Cross-Market Factors
*Generated: 2026-10-17 | Strategies: RVL-3, STRK, ZSCO, CRB, GAP variants, PAV, LYA-1, MTF-4*

---

## 1. Economic Shocks — Gap-Fill Performance

- **COVID Mar 2020:** USD surged then reversed fast under central bank action. Gap-fill strategies (GAP/PAV) would have worked post-shock V-shape recovery. Initial direction was AGAINST mean-reversion.
- **Ukraine Feb 2022:** EUR fell ~20% over ~7 months. Sustained directional regime. Gap-fill long-bias trades would have **repeatedly failed** — gaps opened with trend, not against it.
- **SVB/Credit Suisse Mar 2023:** Short EUR spike; vol expanded briefly then normalized. Mixed — fast-mean-reversion strategies (short hold) likely caught the recovery spike.

**Verdict:** Shock regimes with sustained direction (Ukraine-type) THREATEN GAP/PAV/CRB. V-shape recoveries (COVID) STRENGTHEN them.

---

## 2. NFP / Labor Shocks

- Large NFP miss (forecast 978k, actual 266k, Jun 2021): EUR/USD moved ~+0.7% mean-reversion of prior dollar strength.
- BUT: macro trend context dominated — in a dollar bull regime, the reversal was smaller and shorter-lived.
- **Key finding:** NFP misses in a ranging/weak-trend environment support RVL-3/CRB mean-reversion. In a strong-trend environment, they fail.

---

## 3. EURUSD Mean-Reverting vs. Trending Regime

- Hurst exponent study (38-yr daily EUR/USD): short horizons H≈0.5 (random), long horizons H≈0.33 (mean-reverting).
- H1 estimate (widely cited, unverified in academic literature): ~55–65% mean-reverting, ~35–45% trending.
- **ADX filter implication:** ADX(14) >25 identifies the trending 35–45% — filtering out these entries for CRB/PAV/GAP could materially improve WR.

---

## 4. Academic Structural Edge Evidence

- **Caporale & Plastun (2020, J. Economic Studies):** Statistically significant intraday hourly return differences on overreaction days; next-day reversal pattern profitable — but **not net of costs**.
- **Bargigli (Florence, 2025 working paper):** Endogenous feedback trading amplifies EUR/USD moves by ≥46% on average. Structural overshoots exist — supports short-duration mean-reversion (RVL/ZSCO).
- **Gap:** No post-2018 out-of-sample confirmation found; cost-adjusted results absent.

---

## 5. Cross-Asset Signals

### Copper → EUR
- Indirect channel: copper weakness → dollar strength → EUR weakness (DXY 57% EUR/USD weight).
- Correlation broke positive in March 2020 — **not reliable as lead indicator**. Use as context only.

### Gold / Bonds (Risk-Off) → EURUSD
- **Critical finding:** In 3 of 6 major crises (2011 euro crisis, Apr 2024 Middle East, early 2026), gold rallied AND EUR fell AND dollar rose simultaneously — **breaking the typical gold/dollar inverse.**
- This means: gold up ≠ EUR strength. In crisis regimes, risk-off hits EUR specifically (European tail risk premium).
- **CRB THREATENED:** Any reversion strategy that treats gold-up as EUR-buy signal will fail in these windows.

### Metals / Industrial / Steel
- Copper/industrial weakness signals global growth slowdown → risk-off → EUR tends to weaken vs USD (safe haven flows).
- Steel/iron ore weakness is a China growth proxy; EUR has export exposure to China. Weak industrial metals = mild EUR headwind.
- **Not a precise entry signal** but useful as regime filter: avoid long-EUR mean-reversion in risk-off metal environments.

---

## 6. Geopolitical / Political Instability

- **Russia-Ukraine 2022:** EUR structurally weakened due to energy dependence. Long-bias mean-reversion strategies failed for ~7 months.
- **Macron snap election Jun 2024:** EUR fell ~1.8% in 2 days; then partially recovered. Short-duration reversion (hold <3 bars) would have been caught short.
- **Italian bond crisis (BTP-Bund spreads):** EUR/USD correlation with EU political risk is real but episodic; mean-reversion strategies face gap-down-then-trend scenarios.

---

## 7. COT — Institutional Positioning

- Large speculators (CTAs/hedge funds) are trend-followers. Extreme net longs (>90th pct) = crowded positioning = **contrarian** (mean-reversion strengthener, not trend confirmation).
- Feb 2026: Record gross EUR longs on COT data (current state).
- **GAP/PAV/CRB:** Extreme speculator net long = mild STRENGTHENING for mean-reversion — crowded unwind adds momentum back toward fair value.
- **Caveat:** No backtested hit-rate; commentary only.

---

## 8. Institutional vs. Retail Order Flow

- Academic evidence (equities): retail-driven overshoots partially reverse when institutional counter-flow arrives.
- EUR/USD ~80% institutional volume (commonly cited, peer-review absent).
- **GAP/PAV/CRB STRENGTHENING** if initial gap is retail-driven (common at news releases).
- **THREATENING** if the move is institutional-led — then mean-reversion thesis fails (institution knows something retail doesn't).

---

## Strategy Risk Matrix

| Strategy | Primary Threat | Primary Strength | Net Verdict |
|---|---|---|---|
| **GAP/PAV** | Sustained directional shock (Ukraine-type); institutional-led gaps | Post-shock V-recoveries; crowded COT + retail-driven gaps | CONDITIONAL — filter by ADX + regime |
| **CRB** | Risk-off episodes where EUR and gold both weaken (2011, 2024); carry unwind = EUR sell when model says buy | Ranging, low-ADR environments; extreme COT positioning | HIGH RISK in crises |
| **RVL-3/LYA-1** | Trend reversal with no pullback (ECB surprise + NFP miss in trend) | Sustained trend regimes (2022 EUR decline) | RELIABLE in trend; needs trend filter |
| **STRK/ZSCO** | Vol expansion without trend (whipsaw); 2021-type inflation regime | Post-crisis vol expansion (COVID, SVB) | TIMING-DEPENDENT |
| **MTF-4** | All timeframes aligning bearishly simultaneously (COVID/Ukraine shocks) | Regime detection across timeframes catches trend switches | MOST ROBUST |

---

## Unexplained / Novel Findings

1. **Cross-asset decoupling in crises:** Gold up + EUR down + USD up simultaneously occurred in 3 of last 6 major crises. This is the #1 unmodeled risk for any EUR long-reversion strategy.
2. **Endogenous feedback amplification (≥46%):** Structural overshoots exist in EUR/USD (Bargigli 2025) — supports short-duration reversion thesis but means timing matters more than direction.
3. **COT Feb 2026 extreme longs:** Current environment has record EUR gross longs — contrarian setup that could support a mean-reversion short or post-exhaustion recovery.
4. **No copper/industrial lead confirmed** — treat as regime context, not entry signal.

---

## Recommended Filters (not yet in backtest)

- **ADX(14) < 20:** Required for GAP/PAV/CRB entries to avoid trending regime failures
- **CCI(14) extreme (>100 or <-100):** Check direction agreement with entry
- **ATR14 percentile:** Track whether wins cluster in low/medium/high vol — to be tested
- **Dynamic spread:** FXOpen ECN spreads during Asian thin session likely 2x — model separately
- **COT extreme positioning:** Flag entries when speculator net position >90th pct against trade direction
