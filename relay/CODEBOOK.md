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

## Example Message
```json
{"from":"THUG","to":"GOON","type":"REPORT","code":"OK","ts":"2026-10-21T00:00:00Z","msg":"WIN_GEN1 passed OOS 2021"}
```
