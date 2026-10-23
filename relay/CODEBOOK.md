# VAGUE CODEBOOK v2
# Shared across all sessions via relay branch. Auto-synced. Do not rename this file.
# Pull relay branch to get latest version before reading or writing relay messages.

## Session Identities
| Codename | Meaning |
|----------|---------|
| THUG | LocalThug — local CLI master on Nasif's laptop |
| GOON | Cloud coordinator session |
| CLONE | Any spawned subagent |
| BOSS | Nasif |

## Channel Names
| Code | Channel |
|------|---------|
| RELAY | GitHub relay branch (primary) |
| BOARD | board.json local file |
| BUZZ | ntfy.sh push notification |
| MAIL | Gmail MCP backup |

## Message Types
| Code | Meaning |
|------|---------|
| PING | Are you there? |
| PONG | Yes, I'm here |
| EXEC | Execute this command |
| DONE | Task completed |
| FAIL | Task failed |
| REPORT | Results/findings |
| PUSH | Sending data your way |
| PULL | Please send me data |
| WAIT | Busy, standby |
| BLOCK | Blocked, need BOSS input |
| PAUSE | MT4 pause active |
| GO | MT4 pause cleared, safe to test |

## Status Codes
| Code | Meaning |
|------|---------|
| OK | All good |
| LOW | Low RAM (< 1 GB) |
| CRIT | Critical issue |
| IDLE | Nothing running |
| BUSY | Test/process running |

## Project Names
| Code | Meaning |
|------|---------|
| VAGUE | This whole operation / EA dev project |
| WIN | A backtest winner |
| BASE | b22_thu base EA |
| OOS | Out-of-sample test period |
| IS | In-sample period |

## File Conventions
- `thug_to_cloud.json` — THUG → GOON messages
- `cloud_to_thug.json` — GOON → THUG messages
- `thug_status.json` — THUG current status
- `cmd_queue.json` — queued EXEC commands
- `cmd_results.json` — DONE/FAIL results
- `CODEBOOK.md` — this file
- `GIT_ACCESS.md` — how any agent bootstraps git access

## Test Result Terms
| Code | Meaning |
|------|---------|
| PF | Profit Factor |
| DD | Max Drawdown |
| NP | Net Profit |
| NT | Number of Trades |
| SP3 | Spread 3 points |
| SP5 | Spread 5 points |
| SP8 | Spread 8 points |
| IS | In-sample period |
| OOS | Out-of-sample period |
| PASS | Beats base in majority of 8 periods |
| SOFT | Better than base but not confirmed |
| SKIP | Worse than base, discard |
| LOG | Entry in TEST_LOG.txt |
| REG | Entry in WINNERS_REGISTRY.txt |
| b22 | Base EA (b22_thu) |
| ZGATE | Z-gate filter (ZMax param) |
| DR | Daily Range filter |
| G1/G2/G4 | Generation 1/2/4 EA variants |

## Comms Shorthand
| Code | Meaning |
|------|---------|
| ACK | Acknowledged |
| NAK | Not acknowledged / rejected |
| FWD | Forwarding to BOSS |
| ETA | Estimated time |
| TBD | To be decided by BOSS |
| NFA | No further action |
| OTP | One-time ping |

## Example Message
```json
{"from":"THUG","to":"GOON","type":"REPORT","code":"OK","ts":"2026-10-21T00:00:00Z","msg":"WIN_GEN1 passed OOS 2021"}
```

## Branch Name Map (internal logic, vague externally)
| Branch Name | Internal Purpose |
|-------------|------------------|
| relay_push | Active relay — THUG reads cmd_queue, posts results |
| agent-sync | Sync channel for subagent state |
| main | Stable base, protected |
| ClaudeAI/* | Auto-named cloud session branches (disposable) |
| exp/* | Experiment branches for EA variants |

## Win Rate Result Codes (bot posting format)
| Field | Meaning |
|-------|---------|
| PASS | Beats base in majority (5+) of 8 periods |
| SOFT | Beats base in 4/8, marginal — needs BOSS review |
| SKIP | Fails majority — discard |
| pf | Profit Factor |
| dd | Max Drawdown % |
| np | Net Profit USD |
| nt | Number of Trades |
| sp | Spread tested (3/5/8 pts) |
| periods_pass | How many of 8 periods beat base |
| set | .set filename tested |

## NSSM Hidden Services (new 2026-10-23)
NSSM = Non-Sucking Service Manager. Runs scripts as Windows services in Session 0 (no visible window, no popup).

| Service Name | What It Does |
|--------------|--------------|
| CliRelayPoll | Local poller: watches relay_push on GitHub every ~30s, executes commands from cmd_queue.json, posts results back. Runs hidden as NSSM service. |
| CloudCmdPollerGH | Cloud command poller: polls GitHub relay branch for new commands from cloud agents (GOON/CLONE), routes to local execution. Runs hidden as NSSM service. |

Checking status:
```powershell
Get-Service CliRelayPoll | Select Status
Get-Service CloudCmdPollerGH | Select Status
```
Starting:
```powershell
Start-Service CliRelayPoll
Start-Service CloudCmdPollerGH
```
"Running (NSSM service, invisible)" = working correctly. No window = correct.

## Slope/Shift Filter Test (2026-10-23)
EA concept: detect big recent move N candles back, use technical stats AT that candle as entry filter.

| Term | Meaning |
|------|---------|
| SHIFT | Lookback offset in candles (e.g. SHIFT=7 = look 7 M1 bars back) |
| SLOPE | Price change per bar over a window (pts/bar) |
| BIGMOVE | Trigger: a move exceeding SlopeThreshold within ShiftWindow |
| SNAPSTAT | Technical snapshot at the SHIFT candle (RSI, ATR, MA at that time) |
| SHIFTWIN | Window size to scan for BIGMOVE (e.g. 5-10 candles) |
| SLOPEMIN | Minimum slope to qualify as BIGMOVE |
| WITH | Trade in direction of BIGMOVE |
| AGAINST | Trade against direction of BIGMOVE (mean reversion) |
| slope-ev-001 | Named test: slope filter + event memory combined, first run, ShiftWin=10 SlopeMin=5 |

### Shift Filter — Dynamic Timeframe/Period Selection
- TF: timeframe of the big move (M1/M5/M15/H1) — match to move speed
- SHIFT: how many bars back the event started
- PERIOD: how many bars the move lasted
- SNAPSTAT taken at bar[SHIFT] on TF
- Filter: only trade if SNAPSTAT at SHIFT meets threshold AND current bar aligns

## Event Memory / Directional Suppression
Track recent big events and use them to suppress opposing entries.

| Term | Meaning |
|------|---------|
| EVLOG | Event log — rolling buffer of BIGMOVE events with TF/SHIFT/direction/size |
| COOLDOWN | Bars after a BIGMOVE during which opposing trades are blocked |
| BUYSUP | Buy suppression active (recent big drop = harder to go long) |
| SELLSUP | Sell suppression active (recent big rise = harder to go short) |
| EVDECAY | Event influence fades over time (decays after COOLDOWN bars) |
| EVSTRENGTH | Magnitude of the event (bigger drop = longer/stronger suppression) |

Logic:
- Big DROP N bars ago → BUYSUP active for COOLDOWN bars, strength scales with drop size
- Big RISE N bars ago → SELLSUP active for COOLDOWN bars
- Multiple events accumulate (compound suppression)
- Events tracked per TF independently

---
## SLOW PUPIL GUIDE — Plain English Decoder
# If you receive a vague instruction and don't understand it, look it up here first.
# All examples use real cypher terms. Read left=vague, right=what it actually means.

### Common Instructions Decoded

| You received | What BOSS/THUG actually means |
|---|---|
| "minimized" | Run with NO visible window. Use -WindowStyle Hidden or wscript/VBS wrapper. Never show a console. |
| "safe" | Check: no MT4_PAUSE file, RAM >= 1GB, no MT4 tester running. Only then proceed. |
| "permitted" | BOSS has authorized this specific action. You may proceed. Does NOT mean all actions are allowed. |
| "cloud test permitted" | GOON/cloud agent may run git/relay read-write tests on relay_push branch. |
| "minimized safe" | Both: run hidden AND verify safe conditions first. |
| "prevent recurrence" | Don't just fix it now — add a permanent guard so it can't happen again. |
| "cause" | Find the ROOT cause, not just symptoms. Check logs, task scheduler, processes. |
| "coordinate with cloud" | Post a message to relay/cmd_queue.json on relay_push AND board.json. GOON will pick it up. |
| "pass it on" | Post to board.json AND push to relay_push so all agents get it. |
| "vague updates" | Short status-only posts. No full logs. Use cypher codes (OK/BUSY/DONE etc). |
| "expand dict" | Add new terms to CODEBOOK.md and push to relay_push. |
| "test ASAP" | Add to cmd_queue.json on relay_push with priority:"high". THUG will run it next. |
| "factor that in" | Update CODEBOOK.md + AGENT_ONBOARDING.md with the new concept. Apply to all future analysis. |
| "slow pupils" | New or confused agents. Write in plain English + cypher side by side. |
| "NSSM service" | Background Windows service with no visible window. See NSSM section above. |
| "CliRelayPoll" | The local poller service that checks GitHub for commands every ~30s. |
| "CloudCmdPollerGH" | The cloud command poller service. If Stopped, start it (Start-Service CloudCmdPollerGH). |
| "slope-ev-001" | The first named test combining slope filter + event memory (BUYSUP/SELLSUP/COOLDOWN/EVLOG). |
| "EVLOG active" | Recent big-move events are stored in memory; they are suppressing some trade directions. |
| "BUYSUP" | Buying is suppressed right now because a recent big DROP is in the event log. |
| "SELLSUP" | Selling is suppressed right now because a recent big RISE is in the event log. |
| "COOLDOWN" | The number of bars a suppression lasts after a BIGMOVE event. |

### Win Logic Rules (always apply to ALL analysis)
1. PASS = beats BASE (b22_thu) in 5+ of 8 periods: 2011,2012,2017,2019,2020,2021,2022,2025-26
2. Must be positive where BASE is positive
3. Neighbours must be stable (vary params ±1 step, still PASS)
4. Test at SP5 and SP8 after initial PASS at SP3
5. Apply EVLOG/BUYSUP/SELLSUP analysis — did big recent moves affect results?
   - If WIN period had a BIGMOVE event, check if BUYSUP/SELLSUP was active during losses
   - Report EVSTRENGTH and COOLDOWN that best explains the result pattern

### How Any Agent Posts a Result
```
Step 1: git pull origin relay_push
Step 2: append to relay/cmd_results.json:
 { "id":"<id>", "from":"CLONE", "verdict":"PASS/SOFT/SKIP",
   "pf":X, "dd":X, "np":X, "nt":X, "sp":8, "periods_pass":6,
   "buysup_active": true/false, "evstrength": 0-10,
   "ts":"<iso>" }
Step 3: git add relay/cmd_results.json
Step 4: git commit -m "report: <id> PASS sp8 pf1.4"
Step 5: git push origin relay_push
Step 6: post same summary to board.json
```

### DC/RC Safe Minimized (for new agents)
- DC = DesktopCommander MCP server (npx @wonderwhy-er/desktop-commander)
- RC = Remote Control (TightVNC or DC remote session)
- "DC safe minimized" = DC must run as NSSM service (Session 0, no desktop, no popup)
- "RC safe minimized" = RC watchdog tasks must use wscript/VBS wrapper, no visible window
- Never start DC/RC in a way that creates a visible console window
