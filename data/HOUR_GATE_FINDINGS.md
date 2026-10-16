# Hour Gate Research — Cross-Validated (G + C), 15 Oct 2026

## Datasets
- **G**: parent.csv, 154 sells, MR_RegimeSwitch_b62 full history
- **C**: HOLD base pool, n=160, ATR-filtered (ATR>50 + h>=12 cells mostly excluded)

## Per-Hour Summary (Both Sessions)

| Hour | G WR | G N | C WR | C N | Status |
|------|------|-----|------|-----|--------|
| h02  | 48%  | 40  | 55.6%| 18  | OK, modest |
| h03  | 50%  | 64  | 70.6%| 34  | G weak, C strong — divergence |
| h04  | 30%  | 10  | 54.5%| 11  | **BAD confirmed both** |
| h05  | 62%  | 8   | 71.4%| 7   | Good (thin) |
| h06  | 100% | 4   | 75.0%| 4   | Good (thin) |
| h07  | 25%  | 4   | 66.7%| 3   | G bad, C ok — thin, inconclusive |
| h08  | 64%  | 11  | 88.9%| 9   | Best hour, consistent — N small |
| h09  | 55%  | 44  | 65.4%| 26  | Good, best volume in window |
| h10  | 48%  | 25  | 62.5%| 32  | OK |
| h11  | 17%  | 6   | 55.6%| 9   | **BAD confirmed both** (AvgNet negative) |
| h22  | 0%   | 4   | n<5  | 1   | G bad, C excluded — unconfirmed |

## Cross-Validated Conclusions

### Confirmed bad hours (block these):
- **h04**: WR 30%/55% G/C, AvgNet -64/-97 — CONFIRMED BAD both sessions
- **h11**: WR 17%/56% G/C, AvgNet -81/-11 — CONFIRMED BAD both sessions

### Best window h05-h09:
- G: WR=63%, +13pp vs base, N=27
- C avg WR h05-h09 = (71+75+67+89+65)/5 = **73.4%** — consistent with G
- C AvgNet: all positive (+78 to +246) in this window
- **Cross-validated**: h05-h09 is a real signal, not G-only artifact
- Caveat: N thin per year — MT4 multi-year test needed before claiming win

### h03 divergence:
- G: WR=50%, C: WR=70.6% — C has high-volume anchor here (n=34)
- May reflect different sub-strategies or regime filters
- Don't block h03; watch in MT4

## MT4 Tests Queued
1. `MR_RegimeSwitch_b62_base.set` — baseline
2. `MR_RegimeSwitch_b62_skip_h16h19.set` — HourTo=15 (offline +1.4pp)
3. `MR_RegimeSwitch_b62_allow_h05h09.set` — HourFrom=5, HourTo=9 (offline +13pp, C 73% avg)

Next candidate: `skip_h04_h11.set` — block h04 AND h11 (both confirmed bad)

## Status
- MT4 lock held by PID 18076 (evolve loop) — waiting
- G: set files ready in hst_out/ + mt4_tester2/tester/
- C: confirmed h05-h09 window; h04/h11 double-confirmed bad
