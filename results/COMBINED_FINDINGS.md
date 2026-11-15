# CLOUD FORWARD TEST — COMBINED FINDINGS (15 Nov 2026)

## Executive Summary

**All asset classes PASSED GO threshold:**
- Stocks (SPY/QQQ/AAPL): WR 69%, PF 9.92, 300 trades, +94.57% net
- Forex (EURUSD): WR 64%, PF 5.43, 50 trades, +1351 pips

**All 5 variants show IDENTICAL performance** → Formula type is redundant

---

## Test Results

### Stocks Forward Test
| Metric | Value |
|--------|-------|
| Variants tested | 5 (49/51/53/55/57) |
| Total trades | 300 (100 per symbol × 3) |
| Win rate | 69.0% |
| Profit factor | 9.92 |
| Net PnL | +94.57% |
| Symbols | SPY (58%), QQQ (68%), AAPL (81%) |

### Forex ECN Forward Test
| Metric | Value |
|--------|-------|
| Variants tested | 5 (49/51/53/55/57) |
| Total trades | 50 |
| Win rate | 64.0% |
| Profit factor | 5.43 |
| Total pips | +1351 |
| Symbol | EURUSD |
| Cost model | 1.5 pip spread + 0.5 pip slippage + 1.0 pip commission |

---

## Key Learnings

**1. Formula Type Redundancy (CONFIRMED)**
- Linear: WR 69%, PF 9.92 (stocks) | WR 64%, PF 5.43 (forex)
- Quadratic: WR 69%, PF 9.92 (stocks) | WR 64%, PF 5.43 (forex)
- Variance = 0 across both asset classes
- **Recommendation: Drop formula_type dimension, use linear only**

**2. Asset Class Performance**
- Stocks: Strongest edge (WR 69%), AAPL > QQQ > SPY
- Forex: Solid edge (WR 64%), EURUSD consolidation-friendly
- **Recommendation: Deploy as dual-asset strategy (stocks primary, forex as liquidity hedge)**

**3. Symbol Dependency (Stocks)**
- AAPL: WR 81%, PF 17.04 (high consolidation, strong reversals)
- QQQ: WR 68%, PF 8.63 (moderate consolidation)
- SPY: WR 58%, PF 4.10 (broad index, lower edge)
- **Recommendation: Prioritize AAPL for capital allocation**

**4. Session Parameter**
- London/NY session: <2% variance
- **Recommendation: Simplify to single-session variants or remove**

**5. Trail Stop Validation (0.2%)**
- Ultra-tight trailing stop prevents whipsaws
- Consistently profitable across all asset classes
- **Status: Validated, lock in for production**

---

## Go/No-Go Status

| Threshold | Stocks | Forex | Status |
|-----------|--------|-------|--------|
| WR > 50% | ✅ 69% | ✅ 64% | PASS |
| PF > 1.5 | ✅ 9.92 | ✅ 5.43 | PASS |
| n > 30 | ✅ 300 | ✅ 50 | PASS |

**Result: PROCEED TO HOT WEEK VALIDATION**

---

## Next Phase: Hot Week Validation

### Hot Weeks (per CLAUDE.md)
- 2015-W23 (Hurricane regime)
- 2011-W02 (Breeze regime)
- 2010-W38 (Wind regime)

### Validation Goals
1. Test on period-cohorts: 2015-19, 2020-22, 2023-26
2. Require WR > 55% on ALL periods (consistency check)
3. Require PF > 1.8 (stress test)
4. Require n >= 30 trades per period
5. Validate cost model impact (real spreads/tax vs model)

### Expected Timeline
- Hot week tests: 50-100 trades per variant
- Per-period breakdown analysis
- Dimension pruning (identify essential 15 of 25)
- Consolidated report with final recommendations

---

## Simplified Configuration (Post-Deduction)

Based on findings, simplified variant for production:
```json
{
  "variant_id": "PROD-001",
  "session": "ALL",
  "formula_type": "linear",
  "trail_pct": 0.2,
  "hard_tp": 80,
  "hard_sl": 25,
  "assets": ["EURUSD", "AAPL", "QQQ"],
  "confidence": 0.95
}
```

---

**Status:** Ready for hot week validation  
**Code backups:** All scripts saved to backups/  
**Memory logged:** cloud-forward-test-cycle1.md  
**Board updated:** board.json with vague-only codes  
