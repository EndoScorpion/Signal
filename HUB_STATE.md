# endos-29 Master Hub — State File
Last updated: 2026-10-12 (signal-ba cloud session)

## BLOCKING GATE
**2021 M1 OOS backtest must exit 0 before ANY EA code changes.**
Pass bar: PF ≥ 1.10 AND max DD < 5% ($500 on $10k) after 8pt commission.

---

## Overnight Queue (process in order)

### JOB 1 — BLOCKING OOS GATE
```
EA:        b20legs_g1a  (Strong2010b_claude.mq4 current branch)
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

Job 1 result: PENDING
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
