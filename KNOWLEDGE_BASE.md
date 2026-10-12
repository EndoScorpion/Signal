# Signal EA — Master Knowledge Base
Project: EURUSD Expert Advisor for FXOpen ECN  
Owner: EndoScorpion (endoscorpion@gmail.com)  
Last consolidated: 2026-10-12

---

## 1. BROKER / INSTRUMENT SPECIFICS — FXOpen ECN EURUSD 5-digit

| Property | Value |
|---|---|
| Broker | FXOpen ECN |
| Symbol | EURUSD (5-digit, Point = 0.00001) |
| Spread | ~2 pts M15 (2018), ~3 pts M1 (2019) |
| Commission | 8 pts per RT **max** (FXOpen ECN cap) = $0.008/0.01lot = $8/lot |
| Swap | 0 (testing on demo/ECN swaps not modelled) |
| Lot size | 0.01 lot in all backtests unless noted |
| Point value | $0.01 per point at 0.01 lot |
| 1 pip | 10 pts (5-digit convention) |
| MT4 `Point` | 0.00001 — EA uses `Point*10` only for display, never for OrderSend |
| Leverage | 1:100 (OOS tests); 1:500 (some IS — only affects margin, not P/L) |

**5-digit note:** All TP/SL in the EA are in Points (0.00001 units). A 300-pt SL = 30 pips. Avoid mixing pips and points in code.

---

## 2. EA HISTORY — ALL VERSIONS

### 2a. PatternRecognition (Feb 2011 origin)
- File: `strong_feb_2011_272_98.16_PatRec_11_Jul_21_commented.mq4`
- Reference backtest: Feb 2011, 272 trades, **98.16% win rate** (buy-only scalp)
- Developed/tuned July 2021 by Nasif Hossain
- Strategy: long-only scalp on EURUSD M1/M5/M15, multi-timeframe filter stack
- Filters: slope (M1 2-bar + 5-bar), ATR range cap, stochastic, volume, peak/valley
- Status: **archived reference only** — not the active development EA

### 2b. Strong2010b (g1a / g1b family — b20legs, b12_ladder, b12_bracketreg)
- Branch variants: `b20legs`, `b12_ladder12`, `b12_bracketreg`
- g1a = original parameter set; g1b = adjusted (higher TP/wider SL)
- Tested: 2018 M15 + 2019 M1 (in-sample)
- **None pass both periods** at 8pt commission (see leaderboard below)

### 2c. Strong2010b_claude — g2a (current active branch)
- File: `Strong2010b_claude.mq4`
- Branch: `claude/mql4-analysis-comments-bd4kz3`
- Last commit: `6a7fe62` (HUB_STATE.md added)
- Source reference: `data/Strong2010b_claude_g2a.mq4` (1986 lines, g2a features)
- Key params: InpTPRange=300, InpTPTrend=360, InpSLRange=290, InpSLTrend=290, InpCommissionPts=8
- Session filter: London h9-12, Overlap h14-15, NY h17, Asian h2-7 excl h6, EOD h18+h21
- **Known bugs (blocked pending OOS):**
  - `CostGateOK` formula is a no-op: `tp/total_cost` ≈ 37, always true. Fix = `(tp-cost)/(sl+cost)` + raise TP ≥ 458pt
  - `rvc`/`rpc` dead code: unreachable after line 199 bare `return;`

### 2d. g2a source features NOT yet in patched EA
1. H1 SMA(1200) directional gate
2. M15 ADX < 28 block (volatility filter)
3. 3-level sell ladder

---

## 3. ALL BACKTEST RESULTS

### 3a. Leaderboard (6pt commission, IS only)
| rank | variant | test | trades | win% | PF | net$ | maxDD$ | pass |
|---|---|---|---|---|---|---|---|---|
| 1 | b12_ladder12_g1b | 2018_M15 | 588 | 52.0 | 1.05 | 51 | 319 | NO |
| 1 | b12_ladder12_g1b | 2019_M1 | 1053 | 51.9 | 1.04 | 77 | 416 | NO |
| 2 | b20legs_g1b | 2019_M1 | 670 | 52.7 | 1.08 | 89 | 271 | NO |
| 3 | b12_bracketreg_g1b | 2018_M15 | 380 | 51.8 | 1.04 | 28 | 203 | NO |
| 3 | b12_bracketreg_g1b | 2019_M1 | 704 | 51.7 | 1.04 | 44 | 282 | NO |
| 4 | b20legs_g1a | 2018_M15 | 365 | 48.2 | 0.89 | -61 | 215 | NO |
| 4 | b20legs_g1a | 2019_M1 | 670 | 54.0 | 1.13 | 122 | 187 | NO |
| 5 | b12_bracketreg_g1a | 2018_M15 | 380 | 47.6 | 0.87 | -77 | 164 | NO |
| 5 | b12_bracketreg_g1a | 2019_M1 | 704 | 53.8 | 1.12 | 120 | 198 | NO |
| 6 | b12_ladder12_g1a | 2018_M15 | 588 | 48.1 | 0.89 | -101 | 259 | NO |
| 6 | b12_ladder12_g1a | 2019_M1 | 1053 | 53.3 | 1.10 | 144 | 324 | MARGINAL |

### 3b. 8pt Rescore — 2019 M1 In-Sample
| report | trades | win%@8 | PF@8 | net@8$ | maxDD@8$ (%) | day-block p |
|---|---|---|---|---|---|---|
| g2a 2019 M1 sp3 | 403 | 57.1 | **1.26** | 138.76 | 105.96 (1.1%) | 0.183 |
| b20legs_g1a 2019 M1 sp3 | 670 | 54.0 | **1.11** | 108.40 | 192.52 (1.9%) | 0.347 |

Both pass PF ≥ 1.10 and DD < 5% at 8pt — but IN-SAMPLE. p-values (0.18, 0.35) = not distinguishable from luck.

### 3c. TP/SL Grid — 2019 M1 g1a SELL legs (8pt commission)
Source: 670 SELL entries replayed. Spread 3pt on exits. IN-SAMPLE only.

| TP | SL | trades | win% | PF@8 | net@8$ | maxDD$ |
|---|---|---|---|---|---|---|
| 200 | 300 | 670 | 64.2 | 1.12 | 86.40 | 138.16 |
| 200 | 400 | 670 | 72.8 | 1.26 | 194.40 | 162.96 |
| 250 | 300 | 670 | 59.3 | 1.14 | 119.90 | 135.52 |
| 250 | 400 | 670 | 67.3 | 1.22 | 197.90 | 180.18 |
| 300 | 300 | 670 | 54.0 | 1.11 | 108.40 | 192.52 |
| 300 | 400 | 670 | 61.9 | 1.16 | 171.40 | 247.08 |

Best IS combo: TP200/SL400 (win 72.8%, PF 1.26) — needs OOS validation.

---

## 4. OOS GATE — HARD RULES

**Nothing committed to the EA until the 2021 M1 OOS backtest exits 0.**

| Rule | Value |
|---|---|
| OOS window | 2021-03-19 to 2022-01-01 (avoids M1 data hole 2021-02-16 to 2021-03-18) |
| Pass bar | PF ≥ 1.10 AND max DD < 5% ($500 on $10k) |
| Commission | 8pt FXOpen max |
| Lucky bar (13 variants, α=5%) | OOS PF ≥ **1.306** |
| Lucky bar (α=10%) | OOS PF ≥ **1.275** |
| Multiple-comp bar (m=21) | day-block p ≤ 0.0024 (Bonferroni) |
| Verdict tool | `python analysis/oos_check.py data/<file>.htm --commission 8 --deposit 10000` |

---

## 5. DATA CAVEATS

| Gap | Details |
|---|---|
| M1 hole | 2021-02-16 to 2021-03-18 — all 2021 OOS starts 2021-03-19 |
| 2011 M15 | Missing ~3.5 weeks incl Aug 8-24 |
| 2012 M15 | Missing ~2 weeks |
| 2019 M1 | Missing Jan 3-11 |
| Post-2022 | No history 2022-09-28 to 2025-08-28 |

---

## 6. PENDING TASK QUEUE (in order)

| # | Job | Status | Condition |
|---|---|---|---|
| 1 | **2021 M1 OOS backtest** — b20legs_g1a M1 2021-03-19→2022-01-01 sp3 | **BLOCKING** | RAM ≥ 1.0 GB, local MT4 only |
| 2 | CostGateOK fix + TP raise ≥ 458pt | HOLD | Job 1 exits 0 |
| 3 | Restore g2a features (H1 SMA gate, M15 ADX<28, 3-level sell ladder) | HOLD | Job 1 exits 0 |
| 4 | Thursday filter: DayOfWeek() != 4 | HOLD | Job 1 exits 0 + cross-check 2019 AND 2021 |
| 5 | rvc/rpc dead code patch | HOLD | Job 1 exits 0 |

---

## 7. SESSION MAP / CLONE ROLES

| Session | Type | Role | RAM cost | Status |
|---|---|---|---|---|
| endos-29 (new) | LOCAL | Master hub — runs MT4 queue, owns backtests | ~400-600 MB | ACTIVE |
| system32-df | CLOUD | Read-only analyst — multi-factor win model | 0 MB | ACTIVE |
| signal-ba | CLOUD | Scorer — 8pt rescore done, this session | 0 MB | ACTIVE |

**Clone rules:**
- Only ONE local hub at a time (clone-guard: RAM ≥ 1.5 GB required)
- Cloud clones: ALWAYS safe (zero PC RAM)
- Hub protection: `scripts/hub_protected.ps1` — type CLOSE to exit, Enter restarts
- Start hub: double-click `scripts/start_hub.bat` (runs as Admin)

---

## 8. COMMISSION MATH (quick reference)

```
8pt commission at 0.01 lot = $0.008 per trade
At 0.01 lot, 1 pt = $0.01
Commission = 8 × $0.01 = $0.08 per round-trip

Net R:R (TP/SL both 300pt, SL=290pt, cost=9pt):
  Net R:R = (TP - 9) / (SL + 9) = (300-9)/(290+9) = 291/299 = 0.97  ← sub-1
  
For R:R = 1.5:  TP = 1.5 × 299 + 9 = 458 pt minimum
```

---

## 9. KEY FILES

| File | Purpose |
|---|---|
| `Strong2010b_claude.mq4` | Active EA (branch: claude/mql4-analysis-comments-bd4kz3) |
| `strong_feb_2011_272_98.16_PatRec_11_Jul_21_commented.mq4` | Archived original (buy-only, 98% WR ref) |
| `data/Strong2010b_claude_g2a.mq4` | g2a source (1986 lines, 3 missing features) |
| `data/Strong2010b_claude_g2a_M1_20190101-20200101_sp3.htm` | 2019 IS backtest HTML |
| `analysis/oos_check.py` | OOS scorer — exit 0 = PASS |
| `analysis/rvc_patch_draft.txt` | Dead-code patch notes |
| `analysis/tp_rr_targets.txt` | TP/R:R target table |
| `data/stats_8pt.md` | 8pt rescore + multiple-testing bar |
| `data/leaderboard.md` | All IS backtest results |
| `data/commission_repricing.md` | Full commission repricing table |
| `data/tpsl_grid_2019_8pt.md` | TP/SL grid at 8pt |
| `data/TAKEOVER_PROMPT.md` | Paste into new cloud session to onboard it |
| `HUB_STATE.md` | Overnight queue + gate rules (root) |
| `scripts/hub_protected.ps1` | Protected master hub launcher |
| `scripts/start_hub.bat` | Double-click to open hub as Admin |

---

## 10. MASTER HUB BOOT SEQUENCE

Paste into any new local or cloud Claude Code session on this branch:

```
Read KNOWLEDGE_BASE.md and HUB_STATE.md.
Rules: OOS gate is BLOCKING — no EA code commits until Job 1 exits 0.
RAM gate: ≥ 1.0 GB for MT4, ≥ 1.5 GB for new local clone.
Commission: always 8pt FXOpen max.
Pass bar: PF ≥ 1.10 AND DD < 5% ($500) on 2021 M1 OOS.
Report in 5 lines max. You are READ-ONLY until Job 1 passes.
```
