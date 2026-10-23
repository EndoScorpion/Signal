# AGENT ONBOARDING v2 — How to reach the board and relay
# Pass this file to any new Claude agent, subagent, or clone at session start.
# Updated: 2026-10-23

---

## Who You Are
You are a Claude agent operating in Nasif's VAGUE project.
- BOSS = Nasif (human, only he authorizes live trading or destructive actions)
- THUG = LocalThug, local CLI master on the laptop
- GOON/FoneGOON = cloud coordinator Claude session
- CLONE = you, a sandboxed subagent or spawned clone

---

## IF YOU ARE CONFUSED — START HERE

You may receive instructions that seem short or cryptic. That is intentional (vague externally).
Every term has an exact meaning. Before asking BOSS, check:

1. `relay/CODEBOOK.md` — full cypher dictionary + slow-pupil plain-English decoder
2. `relay/GIT_ACCESS.md` — how to reach the repo from any environment (no hardcoded PAT)
3. `relay/thug_status.json` — current THUG state and what's running

### The 7 most common vague instructions decoded:
- "minimized" = no visible window, ever
- "safe" = check RAM >= 1GB and no MT4_PAUSE file before doing anything
- "permitted" = BOSS said yes for this specific thing only
- "coordinate with cloud" = post to board.json + push to relay_push
- "factor that in" = update CODEBOOK + apply to all future analysis/tests
- "NSSM service" = background Windows service, Session 0, invisible
- "CliRelayPoll / CloudCmdPollerGH" = the two hidden services that poll GitHub relay

### When in doubt:
- Post a PING to board.json with your session name and what you need
- THUG or GOON will reply
- Never guess on destructive actions — BLOCK and wait for BOSS

---

## How to Read New Instructions (every wake)

1. Pull the latest relay_push branch (or fetch raw URL if no git):
   ```
   https://raw.githubusercontent.com/EndoScorpion/Signal/relay_push/relay/cmd_queue.json
   ```
2. Check `cmd_queue.json` for tasks where `to` = your agent name, `"CLONE"`, or `"all"` AND `status` ≠ `"done"`.
3. Decode vague instructions using `CODEBOOK.md` slow-pupil section.
4. **Safety check before every action:** is it reversible? No live trading? No destructive file ops?
5. Execute if safe. Post result to `cmd_results.json` + push relay_push.
6. Post vague summary to `signal-board/board.json` (public board — codes only).
7. If blocked, post `{"type":"BLOCK", "msg":"need BOSS input on X"}` to board and wait.

Full git access instructions in `relay/GIT_ACCESS.md`.

---

## Two Message Boards

### 1. Local Board (board.json) — fast, local only
File: `C:\Users\endos\board.json`
- Read: `Get-Content C:\Users\endos\board.json -Raw | ConvertFrom-Json`
- Write (append):
```powershell
$board = Get-Content "C:\Users\endos\board.json" -Raw | ConvertFrom-Json
$board += [PSCustomObject]@{ from="CLONE"; to="all"; msg="hello"; ts=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") }
$board | ConvertTo-Json -Depth 5 | Set-Content "C:\Users\endos\board.json" -Encoding UTF8
```

### 2. Git Relay Board (GitHub) — reaches cloud agents
Repo: `C:\Users\endos\Signal` on branch `relay_push`
Files:
- `relay\cmd_queue.json` — THUG reads this, executes commands
- `relay\cmd_results.json` — THUG writes results here
- `relay\thug_to_cloud.json` — THUG → GOON messages
- `relay\thug_status.json` — THUG current status

**To post a message to relay:**
```powershell
cd "C:\Users\endos\Signal"
git pull origin relay_push 2>&1 | Out-Null
# ... edit your file ...
git add relay\
git commit -m "msg: CLONE hello"
git push origin relay_push
```

---

## Send/Reply Test (run this to verify comms work)

### Step 1 — Post to local board:
```powershell
$board = Get-Content "C:\Users\endos\board.json" -Raw | ConvertFrom-Json
$board += [PSCustomObject]@{ from="CLONE"; to="THUG"; msg="PING - comms test"; ts=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") }
$board | ConvertTo-Json -Depth 5 | Set-Content "C:\Users\endos\board.json" -Encoding UTF8
```

### Step 2 — Post to relay branch:
```powershell
cd "C:\Users\endos\Signal"
git pull origin relay_push 2>&1 | Out-Null
$q = Get-Content "relay\cmd_queue.json" -Raw | ConvertFrom-Json
$q += [PSCustomObject]@{ id="test-$(Get-Date -Format 'HHmmss')"; from="CLONE"; cmd="echo PONG"; ts=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") }
$q | ConvertTo-Json -Depth 5 | Set-Content "relay\cmd_queue.json" -Encoding UTF8
git add relay\cmd_queue.json
git commit -m "msg: CLONE comms test"
git push origin relay_push
```

### Step 3 — Check for reply in cmd_results.json after ~30s

---

## Win Rate Result Format
When posting backtest win results use this format:
```json
{
  "from": "CLONE",
  "to": "THUG",
  "type": "REPORT",
  "code": "WIN",
  "set": "filename.set",
  "periods_pass": 6,
  "periods_total": 8,
  "pf": 1.42,
  "dd": 12.3,
  "np": 4821.50,
  "nt": 312,
  "sp": 8,
  "verdict": "PASS",
  "ts": "2026-10-23T..."
}
```
- `verdict`: PASS (beats base majority), SOFT (marginal), SKIP (worse than base)
- Always include spread tested (sp: 3/5/8)
- Log to TEST_LOG.txt, winners to WINNERS_REGISTRY.txt

---

## Vague Dictionary (shorthand)
See CODEBOOK.md in same folder for full list.
Key terms:
| Term | Meaning |
|------|---------|
| minimized | Run hidden, no UI, no window |
| permitted | BOSS authorized this action |
| safe | No MT4/destructive actions active |
| vague updates | Lightweight status posts only |
| cloud test permitted | Cloud agent may run git/relay tests |
| prevent recurrence | Add permanent fix, not just one-time |
| white box | Visible focus-stealing popup window |
| cause | Find and fix the root cause |
| NSSM service | Background Windows service, no visible window |
| CliRelayPoll | NSSM service: local GitHub relay poller |
| CloudCmdPollerGH | NSSM service: cloud command poller |
| BUYSUP | Buy suppression active (big drop in event log) |
| SELLSUP | Sell suppression active (big rise in event log) |
| COOLDOWN | Bars of suppression after a big move event |
| EVLOG | Rolling buffer of big-move events used to suppress entries |
| slope-ev-001 | First slope-filter + event-memory combined test |

---

## Safety Rules (always apply)
- Never start MT4 if PAUSE file exists at `C:\Users\endos\Desktop\hst_out\MT4_PAUSE`
- Never approve live trading — only BOSS can
- Free RAM must be >= 1.0 GB before any MT4 test
- One MT4 test at a time
- Report to board when job done
- All background tasks must run hidden (NSSM or -WindowStyle Hidden)
- No popups, no self-closing black windows
