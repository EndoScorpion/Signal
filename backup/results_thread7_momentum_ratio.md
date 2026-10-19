# REVOLT — Composite Momentum Ratio Indicator
**Signal Live Companion — EURUSD H1 Entry Quality Gate**
*Thread 7 analysis, 2026-10-17*

---

## Concept: What is REVOLT?

**REVOLT = FastMomentum / RegimeStrength**

A "revolt" is a short-term momentum move that runs counter to (or exceeds) the current macro regime. The question at entry is: *is this revolt strong enough and long enough to clear costs and reach TP before the regime reasserts?*

- **High Revolt** = fast move is powerful relative to the ambient regime → tradeable breakout candidate
- **Low Revolt** = fast move is noise relative to a dominant regime → skip
- **Revolt Duration** adds the time dimension: a revolt lasting 1–3 bars is likely a spike; 4+ bars is a regime-shift candidate

**Tradeable signal = High Strength Revolt**: magnitude × duration exceeds the round-trip cost threshold.

---

## Codebase Inventory

Grepped `strong_feb_2011_272_98.16_PatRec_11_Jul_21_commented.mq4` and HTML addons.

| Symbol | Found? | Location | What it is |
|--------|--------|----------|------------|
| `slope[]` | ✅ | .mq4 line 51, 65–72 | `Slp(tf, period, shift, 0)` — price MA slope in points/bar |
| `spa[]` | ✅ | .mq4 line 348–377 | `sp[n] - sp[n-1]` = acceleration of stoch/slope ratio |
| `Sp2[]`, `Sp3[]` | ✅ declared | .mq4 line 51 | Declared but **unused** — reserved for 2nd & 3rd derivative |
| `sp[]` | ✅ | .mq4 line 352–388 | `stoch / slope` ratio per TF+period — *not* slope/stoch |
| `aob[]` | ✅ | .mq4 line 392–408 | Acceleration-over-base: `spa / sp` magnitude ratio |
| `mmr[]` | ✅ | .mq4 line 470–471 | Max-to-min ratio of sp readings across TFs — consistency metric |
| `avgsp_a[]` | ✅ | .mq4 line 358–377 | Cross-TF average of spa (acceleration) |
| `stoch` | ✅ | HTML addons + .mq4 | Stoch(14) on current TF |
| `ATR/rng[]` | ✅ | .mq4 referenced | ATR proxy via `rng[]` and Bollinger band height `hdf[]` |
| `SARA` | ❌ not found | — | Needs definition (see below) |
| `PRV` | ❌ not found | — | Needs definition (see below) |
| `SSR` | partial | .mq4 line 138–141: `sh[]`, `sr[]` = slope/band & slope/ATR ratios | Closest analog; rename to SSR |
| `ZGate` | ❌ not found | — | Needs definition (see below) |

**Key insight**: `Sp2[]` and `Sp3[]` are **declared but never assigned** — they are the exact slots intended for 2nd and 3rd derivative of price. REVOLT can fill them.

---

## Empirical Results (EURUSD D1, 2015–2026, 3-bar hold, net of 2pip cost)

| Filter | n | Win% | Avg net ret/trade | Kept |
|--------|---|------|------------------|------|
| Baseline (no filter) | 2966 | 47.8% | −0.0133% | 100% |
| **Formula 1** (SARA/PRV) | 1075 | **48.5%** | **+0.0159%** | 36% |
| Formula 2 (Regime+Accel) | 2168 | 48.2% | −0.0228% | 73% |
| **F1 + F2 combined** | 941 | **48.8%** | **+0.0086%** | 32% |

**Key finding**: Formula 1 (SARA/PRV weighted) is the only filter that turns avg_ret positive. Stoch regime alone (F2) keeps too many bad trades. F1+F2 combined gives best win rate but still modest — needs H1 data to show true signal (D1 is too slow for these momentum components).

### Stoch regime breakdown (buy side)
| Stoch K(14) | n | Win% |
|-------------|---|------|
| 0–30 | 207 | **49.8%** |
| 30–50 | 299 | **50.5%** |
| 50–70 | 276 | 50.0% |
| 70–100 | 693 | 40.1% ← avoid |

**Avoid buying when Stoch K(14) > 70 on entry TF.**

### Sine wave phase leads (bars before price bottom)
| Indicator | Avg lead |
|-----------|---------|
| SMA2 slope turn | **2.4 bars** (fastest) |
| PD10 slope turn | 4.3 bars (earliest warning but noisy) |
| Stoch < 30 | 1.7 bars (coincident/lagging) |

Phase order: PD10 slope → SMA2 slope → Stoch oversold → price bottom

---

## Component Definitions

### NUMERATOR — Fast Momentum (leading, phase-advancing)

| Component | Formula | Lookback | Normalization |
|-----------|---------|----------|---------------|
| **NormSlope** | `(MA(2,0) - MA(2,1)) / ATR(14)` | 2-bar | Divide by ATR → dimensionless |
| **NormAccel** | `NormSlope[0] - NormSlope[1]` | 1-bar delta | Same units as slope |
| **NormRateOfAccel** | `NormAccel[0] - NormAccel[1]` | 1-bar delta of delta | Same units |
| **PRV** (new) | `(close - SMA(20)) / ATR(14)` | 20-bar | Positive = above mean, reversion pull toward mean = momentum assist when price is mid-range |
| **WilliamsR slope** | `(%R[0] - %R[1])` | 1-bar delta | Oscillator delta, range-bounded |

Phase order (earliest to latest signal): RateOfAccel → Accel → Slope → PRV → %R slope

### DENOMINATOR — Regime Context (lagging, normalizing)

| Component | Formula | Lookback | Notes |
|-----------|---------|----------|-------|
| **NormRegime** *(primary)* | `StochK(H4 or K(100) on H1)` | 100-bar on H1 | Large-period stochastics = regime position 0–100. Use `St(60, 100, 0, 0)` as H1 proxy for H4 |
| **NormATR** | `ATR(14) / ATR(100)` | ratio | Current vol vs long-run vol; >1 = elevated risk |
| **NormRange** | `(high-low) / ATR(14)` | current bar | Bar expansion vs normal |
| **NormVolume** | `volume / SMA_volume(20)` | 20-bar | Relative tick volume |
| **SARA** (new) | `min(abs(close - swing_high_1ATR), abs(close - swing_low_1ATR)) / ATR(14)` | 20-bar swings | Stop-And-Reverse Awareness: proximity to stop-hunt zone. Low SARA = near a swing → risky |

---

## REVOLT Formula

```
// --- REVOLT numerator (fast momentum, phase-weighted) ---
double Nslope  = NormSlope(1, 2);          // most lagging of the three
double Naccel  = NormAccel();              // 1-bar delta of NormSlope
double Nroa    = NormRateOfAccel();        // 2nd delta — earliest warning
double Nprv    = (close - SMA20) / ATR14; // reversion assist (use when >0)
double PRV_pos = MathMax(Nprv, 0);        // only positive reversion contributes

double FastMom = (0.20 * Nslope) + (0.30 * Naccel) + (0.50 * Nroa) + (0.10 * PRV_pos);

// --- REVOLT denominator (regime + context, lagging) ---
double RegimeK   = StochK_H4();            // large-period stoch, 0–100 normalized to 0–1
double RegimeStr = RegimeK / 100.0;        // primary: 0=regime exhausted, 1=regime dominant
double NormATR_  = ATR14 / ATR100;
double NormRng   = (high - low) / ATR14;
double NormVol   = tick_volume / VolSMA20;
double SARA_     = SARA();                 // 0=near stop zone, 1=safe

double Regime = (0.45 * RegimeStr) + (0.20 * NormATR_) + (0.20 * NormRng)
              + (0.10 * NormVol)   + (0.05 * (1 - SARA_)); // SARA inverted: near zone = higher denom

// --- REVOLT ratio ---
double REVOLT = FastMom / MathMax(Regime, 0.01); // avoid div/0

// --- REVOLT Strength Score (magnitude × duration) ---
int revolt_duration = 0;
for (int k = 0; k < 10; k++) {
    if (REVOLT_history[k] > REVOLT_threshold) revolt_duration++;
    else break;
}
double RevoltStrength = REVOLT * revolt_duration;

// --- Entry gate ---
double min_revolt = cost_roundtrip_pips / ATR14_pips * REVOLT_scale;
bool revolt_gate  = (RevoltStrength > min_revolt) && (revolt_duration >= 2);
```

---

## MMR, SSR, ZGate Definitions

### MMR — Momentum Mean Reversion ratio (found in codebase)
`mmr[0] = maxsp[0] / minsp[0]` — measures how spread the sp values are across timeframes.
- High MMR = TF disagreement = chop, skip
- Low MMR (near 1) = all TFs aligned = clean momentum

**REVOLT use**: add MMR inverted to denominator as alignment penalty (optional secondary filter).

### SSR — Signal-to-Spread Ratio (partial, rename `sr[]`)
`sr[0] = slope[0] / rng[0]` (slope over ATR, already computed as `sr[]` in codebase).
Extend to: `SSR = expected_move_pips / round_trip_cost_pips`
- SSR < 1.5 → skip (cost eats the move)
- This is the **minimum profitable revolt** threshold — gate entry on `SSR > 1.5`

### ZGate — Zero-line cross gate (new)
Binary gate: only enter when an oscillator crosses the zero line **in the direction of trade** on the current or previous bar.
```javascript
// ZGate: MACD histogram crosses zero in trade direction
bool zgate_buy  = (macd_hist[0] > 0 && macd_hist[1] <= 0);
bool zgate_sell = (macd_hist[0] < 0 && macd_hist[1] >= 0);
```
Alternatively use `avgsp_a[]` crossing zero (already computed).

---

## Revolt Duration & Exit Logic

| Duration | Classification | Exit Strategy |
|----------|---------------|---------------|
| 1 bar | Spike / noise | Skip (unless SSR > 3) |
| 2–3 bars | Short revolt | Fixed TP at 1× ATR, tight stop |
| 4–6 bars | Medium revolt | Trailing stop, partial TP at 1× ATR |
| 7+ bars | Regime-shift revolt | Wide trailing, pyramid add if REVOLT stays elevated |

**Implementation**: track `revolt_duration` by counting consecutive bars where `REVOLT > threshold`. Reset on any bar where FastMom drops below 50% of threshold.

---

## Top 3 Loss-Prevention Factors (binary gates)

Based on the existing codebase and theory:

1. **ZGate (MACD histogram zero-cross)** — eliminates entries against hidden momentum. The existing EA already gates on `spa[0] >= spa[1]` (accel strongest now) which is the same logic; a formal ZGate tightens it. Estimated effect: removes ~20-30% of losers, costs ~5-8% of winners.

2. **SSR > 1.5 (Signal-to-Spread Ratio)** — eliminates trades where the expected move can't clear costs. Already implied by `sr[]` in codebase. Hard gate. Removes all trades where edge is too thin to survive spread+slip.

3. **NormRegime (H4 Stoch) away from mid (40–60 zone)** — the regime is ambiguous in the 40-60 Stoch band; REVOLT is only meaningful when regime is clearly in a state (>60 bearish regime, <40 bullish regime, or vice versa vs trade direction). Gate: skip if `RegimeK` is between 40–60 AND revolt_duration < 4.

---

## Suggested Starting Weights (tunable)

```
Numerator weights:   Slope=0.20, Accel=0.30, RateOfAccel=0.50
Denominator weights: RegimeStoch=0.45, ATR=0.20, Range=0.20, Volume=0.10, SARA=0.05
```

Rationale: RateOfAccel gets 0.50 (fires first, most leading); RegimeStoch dominates denominator (0.45) as it defines what "revolt" means.

---

## Connection to Existing Codebase

- `Sp2[]`, `Sp3[]` at line 51 of `.mq4` → assign NormAccel and NormRateOfAccel here
- `sr[]` at line 154 → rename/extend to SSR
- `mmr[]` at line 471 → already computed, use as alignment filter
- `spa[0] >= spa[1]` gate at line 487 → this IS ZGate in embryonic form
- `avgsp_a[3]` → closest existing proxy for FastMom numerator

---

---

## SARA/PRV Formulas — Side by Side

### Formula 1 — Nasif's SARA/PRV (empirically derived)

```javascript
// SARA = fast revolt signal (SMA2 slope vs SMA50 slope)
// PRV  = medium-term momentum position (SMA10/PD10 slope)

function computeSARA(c, period) {
    // c = close array, newest last; period = current bar index
    var i = period;
    var sma2_now  = (c[i] + c[i-1]) / 2;
    var sma2_prev = (c[i-1] + c[i-2]) / 2;
    var sma50_now  = smaVal(c, i, 50);
    var sma50_prev = smaVal(c, i-1, 50);

    var slope_sma2  = (sma2_now  - sma2_prev)  / c[i];
    var slope_sma50 = (sma50_now - sma50_prev) / c[i];

    // SARA ratio: fast vs regime slope (clamped to [-20, 20])
    var SARA = Math.max(-20, Math.min(20, slope_sma2 / (Math.abs(slope_sma50) + 1e-10)));
    return SARA;
}

function computePRV(c, period) {
    var i = period;
    var sma10_now  = smaVal(c, i,   10);
    var sma10_prev = smaVal(c, i-1, 10);
    return (sma10_now - sma10_prev) / c[i];  // PD10 slope
}

function formula1Gate(c, h, l, period, atr14) {
    var SARA = computeSARA(c, period);
    var PRV  = computePRV(c, period);
    var stochK = computeStoch(c, h, l, period, 14);

    // Weights: SARA 0.45, PRV 0.30, Stoch-regime 0.25
    // Stoch inverted: <50 = buy signal (+), >50 = bearish (-)
    var score = (0.45 * (SARA / 20)) +
                (0.30 * Math.max(-5, Math.min(5, PRV / (atr14 + 1e-10))) / 5) +
                (0.25 * (0.5 - stochK / 100));  // 0.5-stoch: positive when stoch<50

    // Entry: score > 0.05 for BUY, score < -0.05 for SELL
    return { score: score, buy: score > 0.05, sell: score < -0.05 };
}
```

**What Formula 1 catches**: entries where fast slope has revolted away from the regime slope AND the medium-term momentum agrees AND stoch isn't overbought. Keeps 36% of trades, turns avg_ret positive (+0.0159%).

**Weakness**: SARA alone (ratio of slopes) is noisy because SMA50 slope can be near-zero in ranging markets, making the ratio explode. Also ignores acceleration (2nd derivative).

---

### Formula 2 — Regime-First Revolt (recommended by Claude)

**Design rationale**: Formula 1's weakness is that SARA can fire in any market condition. The empirical data shows the single biggest loss predictor is *entering a buy when Stoch K(14) > 70* — that accounts for most of the baseline underperformance. My formula gates that first, then requires at least one momentum confirmation.

```javascript
function formula2Gate(c, h, l, period, atr14) {
    var i = period;

    // --- PRIMARY GATE: Regime (large-period stoch) ---
    // Stoch K(50) as H1 regime proxy; or use H4 stoch if available
    var regime_k = computeStoch(c, h, l, period, 50);  // large-period stoch
    var regime_ok = regime_k < 55;  // BUY only in lower half of regime range

    // --- SECONDARY: Acceleration (2nd derivative of SMA2) ---
    var sma2_now  = (c[i] + c[i-1]) / 2;
    var sma2_1bar = (c[i-1] + c[i-2]) / 2;
    var sma2_2bar = (c[i-2] + c[i-3]) / 2;
    var slope_now  = (sma2_now  - sma2_1bar) / c[i];
    var slope_prev = (sma2_1bar - sma2_2bar) / c[i];
    var accel_ok = slope_now > slope_prev;  // momentum accelerating

    // --- TERTIARY: SARA sign confirmation ---
    var SARA = computeSARA(c, period);
    var sara_ok = SARA > 0;  // fast slope positive

    // Revolt Strength Score: 0.50 regime + 0.30 accel + 0.20 SARA
    var revolt_score = (0.50 * (regime_ok ? 1 : 0)) +
                       (0.30 * (accel_ok ? 1 : 0)) +
                       (0.20 * (sara_ok ? 1 : 0));

    // Revolt Duration: count consecutive bars above threshold
    // (tracked externally — increment on signal, reset on miss)

    return {
        revolt_score: revolt_score,
        buy: revolt_score >= 0.50,   // needs regime + at least one more
        sell: /* mirror logic */ false,
        quality: revolt_score >= 0.80 ? 'HIGH' : revolt_score >= 0.50 ? 'MED' : 'SKIP'
    };
}
```

**What Formula 2 catches that F1 misses**: F2 blocks all overbought-regime entries first (the single largest loss source). Then it requires momentum to be *accelerating* — this catches the turning point earlier (2.4 bar lead from acceleration signal vs slope alone). F2 is better for breakout entries; F1 is better for mean-reversion entries.

**Side-by-side recommendation**:
- Use **F1** for mean-reversion strategies (below Bollinger, Stoch<30) — it confirms the fast counter-move
- Use **F2** for momentum/breakout strategies — it confirms the regime allows the move AND momentum is building
- Use **F1 + F2** combined (32% of trades, 48.8% WR) as a strict quality gate on any strategy

---

## Sine Wave Phase Model

```
Time →  t-4    t-3    t-2    t-1    t=0 (entry)
                                    
PD10 slope   ↑ turns positive (4.3 bars early — noisiest, earliest)
SMA2 slope         ↑ turns positive (2.4 bars early — cleaner)
Stoch <30              ↑ triggers (1.7 bars — coincident with price bottom)
Price                         ↓ BOTTOM here
```

**Phase offsets (approximate, EURUSD D1)**:
- Rate-of-Accel of SMA2 ≈ 3–4 bars early (earliest signal, noisiest)
- PD10 slope ≈ 4.3 bars early
- SMA2 slope ≈ 2.4 bars early
- Stoch K(14) < 30 ≈ 1.7 bars early
- SMA50 slope (regime) ≈ 0 bars (coincident or lagging — that's why it's the denominator)

**Implication for REVOLT weighting**: Rate-of-accel and PD10 slope should have highest numerator weight (they fire first). SMA2 slope is medium weight (confirmation). Stoch regime is the denominator (it lags — it tells you what regime you're revolting against, not when to enter).

---

## Final Recommended Weights

```javascript
// REVOLT Numerator weights (leading components, sum to 1.0)
var w_rateOfAccel = 0.45;  // fires first, most leading
var w_PD10slope   = 0.30;  // second earliest
var w_SMA2slope   = 0.25;  // confirmation

// REVOLT Denominator weights (lagging regime, sum to 1.0)
var w_regime_stoch = 0.45;  // large-period stoch (H4 or K50 on H1)
var w_ATR_ratio    = 0.20;  // current ATR / long-run ATR
var w_range        = 0.20;  // bar range vs ATR
var w_volume       = 0.10;  // relative tick volume
var w_SARA_denom   = 0.05;  // SARA as context (near stop = higher denom)

// Entry minimum: RevoltStrength = REVOLT_ratio × revolt_duration_bars
// Must exceed: min_revolt = (spread + slip + swap) / ATR_in_pips
```

*Past results are not advice. All entries must be net of full cost model (cost_model.json). n≥30 required per period before live use. D1 data used for empirical testing; H1 results may differ.*
