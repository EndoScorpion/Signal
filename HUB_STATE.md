# endos-29 Master Hub — State File
Last updated: 2026-10-12 (OOS-gate cloud thread)

## BLOCKING GATE
**2021 M1 OOS backtest must exit 0 before ANY EA code changes.**
Pass bar: PF ≥ 1.10 AND max DD < 5% ($500 on $10k) after 8pt commission.

---

## GATE STATUS (2026-10-12): NOT RUN — needs local MT4
- **Cannot run in cloud.** MT4 Strategy Tester + FXOpen 2021 M1 tick history exist only on the PC.
- **EA mismatch fixed in this file.** Old Job 1 said "b20legs_g1a (Strong2010b_claude.mq4 current branch)".
  Those are different EAs: the branch `Strong2010b_claude.mq4` (662 lines) is a BUY-only PatRec rewrite;
  b20legs_g1a is the SELL-leg EA whose 2019 IS numbers are in the leaderboard. Testing the branch file
  would gate an EA that has no in-sample baseline. Job 1 now targets the compiled
  `MQL4\Experts\Strong2010b_claude_b20legs_g1a.ex4` (present on the PC, built 2026-10-08).
- **Scorer verified.** `oos_check.py` on the 2019 g2a report: 403 trades, PF 1.249, DD 1.05%, exit 0.
  Price-based 8pt recompute gives PF 1.26 / net $138.76, matching data/stats_8pt.md. Note: the report's
  profit column already carries ~8.6pt/trade broker cost, so `--commission 8` adds only $0.008/trade on top.
- **One-command runner:** `scripts/run_oos_gate.ps1` (RAM gate, writes tester ini, runs MT4 headless,
  copies report to data/, runs oos_check, exits 0/1). Set deposit $10,000 in the tester GUI once first.

### Next steps
1. Close MT4, then from the Signal folder: `powershell -ExecutionPolicy Bypass -File scripts\run_oos_gate.ps1`
2. Push the .htm from data/, fill in ## RESULTS below.
3. For the full OOS candidate set (stats_8pt.md, m=21): compile g2a–g2d .mq4 in MetaEditor (no .ex4 yet),
   rerun with `-Expert Strong2010b_claude_g2a` etc. A winner also needs day-block p ≤ 0.0024.
4. Only after exit 0: unblock Jobs 2–4.

---

## Overnight Queue (process in order)

### JOB 1 — BLOCKING OOS GATE
```
EA:        Strong2010b_claude_b20legs_g1a.ex4  (MQL4\Experts on the PC — NOT the branch Strong2010b_claude.mq4)
Pair:      EURUSD
TF:        M1
Period:    2021-03-19 to 2022-01-01
SpreadPt:  3  (sp3)
Deposit:   $10,000
Leverage:  1:100
Commission: 8pt per RT (InpCommissionPts=8)
```
**Steps:**
1. RAM check: `Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory`
   - Must be ≥ 1,000,000 KB (1.0 GB) before launching MT4
2. Launch MT4 Strategy Tester → load Strong2010b_claude.mq4
3. Set dates: 2021.03.19 – 2022.01.01, M1, EURUSD, Every Tick, $10k, 1:100
4. Run → wait for completion
5. Right-click Report tab → Save as HTML → save to:
   `Signal\data\Strong2010b_claude_b20legs_g1a_M1_20210319-20220101_sp3.htm`
6. Push to git:
   ```
   cd Signal
   git add data/Strong2010b_claude_b20legs_g1a_M1_20210319-20220101_sp3.htm
   git commit -m "data: 2021 M1 OOS backtest result (b20legs_g1a)"
   git push -u origin claude/mql4-analysis-comments-bd4kz3
   ```
7. Score:
   ```
   python analysis/oos_check.py data/Strong2010b_claude_b20legs_g1a_M1_20210319-20220101_sp3.htm --commission 8 --deposit 10000
   ```
8. Record result in this file under ## RESULTS

---

### JOB 2 — HOLD (post OOS gate)
CostGateOK formula fix + TP raise to ≥ 458pt  
File: Strong2010b_claude.mq4  
See analysis/rvc_patch_draft.txt for details

### JOB 3 — HOLD (post OOS gate)
Restore g2a features missing from patched EA:
- H1 SMA(1200) directional gate
- M15 ADX<28 block  
- 3-level sell ladder

### JOB 4 — HOLD (post OOS gate)
Thursday filter: DayOfWeek() != 4 guard
Cross-check 2019 AND 2021 Thursday data first

---

## Security Constraints (HARD — do not override)
- No EA code commits without Job 1 exit 0
- RAM gate: ≥ 1.0 GB free for MT4 backtests
- RAM gate: ≥ 1.5 GB free for new local CLI clones
- Pass bar for ALL changes: PF ≥ 1.10 AND DD < 5% on 2021 M1 OOS
- Lucky bar (13 variants tested): 2021 OOS PF ≥ 1.306 (5%) or ≥ 1.275 (10%)

---

## RESULTS
*(fill in after Job 1 completes)*

Job 1 result: PENDING (not run — local MT4 required; runner ready)
- Trades: 
- Win rate: 
- PF: 
- Net PnL: 
- Max DD: 
- Verdict: 

---

## Session Map
| Role | Session ID | Status | Notes |
|------|-----------|--------|-------|
| master | endos-29 (new session) | ACTIVE | runs queue |
| analyst | system32-df (cloud) | ACTIVE | multi-factor win model |
| scorer | signal-ba (cloud) | ACTIVE | 8pt rescore done |

## EA Branch
`claude/mql4-analysis-comments-bd4kz3`  
Last commit: `1ac0ba2`
