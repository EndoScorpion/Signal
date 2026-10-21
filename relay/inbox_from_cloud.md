# Cloud → LocalThug Test Queue
Generated: 2026-10-21T09:22Z
Status: QUEUED — run all in order, 24h batch, no cloud MCP needed.

All tests: EURUSD H1, spread 8 pts (4 pip ECN), commission 8 pts/trade, 0.1 lot.
Cost per trade = 0.00008 (16 pts round-trip).
Flag condition listed per test. Write results to /mnt/project-files/results/ or drop in board.json.

---

## BATCH 1 — High priority (run first)

### nomem6_018 — MKT-13-16-NY-T86s+LOSSY+Z09+FRI+TRAIL08
**Priority:** 3 (trail variant of nomem6_016 — tick run decides)
**Symbol:** EURUSD  **TF:** H1 (Model 1 M1 for tick-level trail)
**Logic:** Friday 13:00–16:00 UTC, first bar per day.
SELL at market if previous bar: Stoch14 %K > 80 AND (min SMA2 slope slots 12–18 < 0 OR min accel < 0) AND count(slope<0) > 0 AND z-score (close–SMA20)/SD20 >= 0.9.
No initial stop. Trailing stop: once price is 0.5×ATR14 in favour, trail stop 0.8×ATR14 behind best price (H1 low for SHORT).
Exit: 21:00 UTC close on Friday (same day), OR trail hit.
**Years:** 2020, 2021, 2022, 2023, 2024, 2025, 2026 (one run per year)
**Timeout:** 180 min/year
**Flag if:** MT4 tick-run PF >= nomem6_016 OOS PF 3.07; cloud bar-close emulation IS 2.88 / OOS 2.55 (below untrailed). Cloud tick emulation IS PF 4.34 / OOS PF 5.65.

---

### nomem6_026 — STACKA-FULL-vs-NOMON17
**Priority:** 1
**Symbol:** EURUSD  **TF:** H1 (Model 1 M15)
**Logic:** Run Stack A in full (all four legs: G11-3 + vgs1b/Mon17x22 + T82 + n016) simultaneously, 0.1 lot each.
- Leg G11-3: Fri 14:00 UTC SHORT, GateA + XNFP, no SL, exit 21:00
- Leg vgs1b (Mon17x22): Mon 17:00–22:00 UTC LONG, day-down gate, no SL, exit 22:00
- Leg T82: (per saved .set)
- Leg n016: Fri 13:00–16:00 SHORT, lossy-divergence + z>=0.9, no SL, exit 21:00
Run twice: (1) all four legs active; (2) without vgs1b leg (G11-3+T82+n016 only).
**Years:** 2020, 2021, 2022, 2023, 2024, 2025, 2026
**Timeout:** 180 min/year
**Flag if:** MT4 PF differs from cloud by >30% or maxDD >2× cloud.
Cloud ref: full IS n=164 WR62 PF2.76 net$1090 DD$100; OOS n=182 WR66 PF2.54 net$1989 DD$122. No-Mon17: IS PF2.85 DD$88; OOS PF3.17 DD$89.

---

### nomem6_027 — STACKA-DAYSTOP-AFTER-LOSS
**Priority:** 2
**Symbol:** EURUSD  **TF:** H1 (Model 1 M15)
**Logic:** Exactly Stack A full (same as nomem6_026 run 1) plus one EA rule: when any stack trade CLOSES with a net loss, block all new entries for the rest of that server day (reset 00:00 server). Count how many entries are blocked.
**Years:** 2020–2026 per year
**Timeout:** 180 min/year
**Flag if:** MT4 PF <2.0 or maxDD >2× nomem6_026 run 1. Cloud ref: IS PF3.16 DD$58 / OOS PF2.96 DD$97 (cloud was lookahead-biased; MT4 run is authoritative).

---

### nomem6_029 — STACKA-MON17-HALFLOT
**Priority:** 2
**Symbol:** EURUSD  **TF:** H1 (Model 1 M15)
**Logic:** Exactly Stack A full (nomem6_026 run 1) but vgs1b (Mon17x22) leg at 0.05 lot; G11-3, T82, n016 stay at 0.1 lot.
**Years:** 2020–2026 per year
**Timeout:** 180 min/year
**Flag if:** MT4 PF or maxDD worse than equal-lot run (nomem6_026 run 1).
Cloud ref: IS PF 2.80 net$963 DD$94; OOS PF 2.76 net$1765 DD$92.

---

## BATCH 2 — Medium priority

### nomem6_028 — MKT-07-ASIA-E7+SL08ATR
**Priority:** 3
**Symbol:** EURUSD  **TF:** H1 (Model 1 M1 for tick stop)
**Logic:** Wed/Thu only, 07:00 UTC bar.
SELL at 07:00 if:
- Asia session (00:00–07:00) up-move >= 0.25×ATR14(H1)
- EMA120 slope < 0
- ADX14 < 30
- ATR14 percentile < 75
- ATR14 >= 50 pts
Hard stop: +0.8×ATR14 above entry (short, so stop above). Exit: 21:00 UTC close.
**Years:** 2020–2026 per year
**Timeout:** 180 min/year
**Flag if:** MT4 PF < 2.0 OR stop-outs > 40% of trades. Cloud ref: FXOpen OOS 2024-26 n=32 PF 6.29.

---

### nomem6_033 — ALLIGATOR-JAW-FILTER (G11-3 on-trend only)
**Priority:** 1
**Symbol:** EURUSD  **TF:** H1
**Logic:** G11-3 base entry (Fri 14:00 UTC SHORT, GateA + XNFP, no SL, exit 21:00) PLUS require: at entry bar, close is ABOVE the Alligator Jaw (SMMA13 shifted 8).
In MT4: use iAlligator(NULL,0,13,8,8,5,5,3,MODE_SMMA,PRICE_MEDIAN,MODE_GATOR_JAW,0) — ALLOW entry only when Close[1] > jaw (trending direction for short).
Report: n trades allowed vs skipped; PF, WR, avg pts for ABOVE-jaw subset vs BELOW-jaw subset.
**Years:** 2020–2026
**Timeout:** 90 min
**Flag if:** above-jaw WR >= 70% AND PF >= 2.0. Cloud sim: above-jaw n=26 WR 85% PF 5.62; below-jaw n=10 WR 46% PF 1.12.

---

## BATCH 3 — Next-cycle candidates (lower priority, run after above)

### nomem6_016 — MKT-13-16-NY-T86s+LOSSY+Z09+FRI (base, no trail)
**Priority:** 1
**Symbol:** EURUSD  **TF:** H1 (Model 1 M15)
**Logic:** Friday 13:00–16:00 UTC, first hit per day.
SELL at market if previous bar: Stoch14 %K > 80 AND (min SMA2 slope slots 12–18 < 0 OR min accel < 0) AND count(slope<0)>0 AND z-score (close–SMA20)/SD20 >= 0.9. No stop. Exit 21:00 UTC Friday.
**Years:** 2020–2026 per year  **Timeout:** 90 min/year
**Flag if:** n>30 AND PF>1.3. Cloud IS PF 2.67 / OOS PF 3.07.

### nomem6_017 — MKT-13-16-NY-T87s+Z09+MMR+FRI
**Priority:** 2
**Symbol:** EURUSD  **TF:** H1
**Logic:** Friday 13:00–16:00 UTC, first hit.
SELL if z-score >= 0.9 AND MMR >= -1 (12-bar max 1-bar up move / |min down move|, g2a form). No stop. Exit 21:00.
**Years:** 2020–2026  **Timeout:** 90 min
**Flag if:** n>30 AND PF>1.3. Cloud IS PF 2.59 / OOS PF 2.33.

### nomem6_019 — MKT-15-16-NY-T88l+LOSSYl+Zm09+MON
**Priority:** 2
**Symbol:** EURUSD  **TF:** H1
**Logic:** Monday 15:00 or 16:00 UTC LONG (first hit).
BUY if: Stoch14 %K < 20 AND (max SMA2 slope slots 12–18 > 0 OR max accel > 0) AND count(slope>0)>0 AND z-score <= -0.9. No stop. Exit 21:00 Monday.
**Years:** 2020–2026  **Timeout:** 90 min
**Flag if:** n>30 AND PF>1.3. Cloud IS n=36 WR58 PF2.22 / OOS n=31 WR61 PF2.71.

### nomem6_020 — MKT-13-16-NY-T89s+SARAPRV+Z09+FRI
**Priority:** 2
**Symbol:** EURUSD  **TF:** H1
**Logic:** Friday 13:00–16:00 UTC, one trade/day.
SELL if prev bar SARA/PRV ratio >= 0.17 (sara = slope+accel+roa of EMA20 in pts; prv = range+10×vrel+(K–D)+K/10, vrel=1 no volume) AND z-score >= 0.9. No stop. Exit 21:00. Cost 0.00008.
**Years:** 2020–2026  **Timeout:** 90 min
**Flag if:** n>30 AND PF>1.3.

### nomem6_030 — G11-3-EXIT22
**Priority:** 2  **EA:** T131_EA
**Symbol:** EURUSD  **TF:** H1  **Spread:** 8  **Comm:** 8 pts
**Set base:** nomem6_b35_chk  **Overrides:** InpEntryHour=14, InpExitHour=22, InpDOW=4, InpDirection=-1, InpGateA=true, InpXNFP=true, InpNoStop=true
**Years:** 2020–2026  **Timeout:** 15 min/year
**Flag if:** n>=30 AND PF>=1.3. Cloud IS PF=1.49 n=72, OOS PF=1.73 n=57.

### nomem6_031 — MON17-EXIT22-GATEA-DAYDOWN
**Priority:** 2  **EA:** T131_EA
**Symbol:** EURUSD  **TF:** H1  **Spread:** 8  **Comm:** 8 pts
**Set base:** nomem6_b40_risk  **Overrides:** InpEntryHour=17, InpExitHour=22, InpDOW=0, InpDirection=1, InpGateA=true, InpDayDown=true, InpNoStop=true
**Years:** 2020–2026  **Timeout:** 15 min/year
**Flag if:** n>=25 AND PF>=1.4. Cloud IS PF=1.61 n=54, OOS PF=2.52 n=25.

---

## Notes
- All costs net ECN: spread 8 pts + commission 8 pts = 16 pts/round-trip ($1.60 at 0.1 lot).
- Write results to /mnt/project-files/results/nomem6_NNN_result.md and update signal-board board.json.
- Cloud will NOT poll until LocalThug posts a completion signal. Go ahead and run all.
- Past results are not advice. Research only.
