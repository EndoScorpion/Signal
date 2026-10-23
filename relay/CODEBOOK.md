# VAGUE CODEBOOK v1
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
|-------------|-----------------|
| relay_push | Active relay � THUG reads cmd_queue, posts results |
| agent-sync | Sync channel for subagent state |
| main | Stable base, protected |
| ClaudeAI/* | Auto-named cloud session branches (disposable) |
| exp/* | Experiment branches for EA variants |

## Win Rate Result Codes (bot posting format)
| Field | Meaning |
|-------|---------|
| PASS | Beats base in majority (5+) of 8 periods |
| SOFT | Beats base in 4/8, marginal � needs BOSS review |
| SKIP | Fails majority � discard |
| pf | Profit Factor |
| dd | Max Drawdown % |
| np | Net Profit USD |
| nt | Number of Trades |
| sp | Spread tested (3/5/8 pts) |
| periods_pass | How many of 8 periods beat base |
| set | .set filename tested |
