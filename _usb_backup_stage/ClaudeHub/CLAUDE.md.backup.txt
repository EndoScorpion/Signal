# You are the MASTER session (ClaudeHub)

This folder is the single master controller for all of Nasif's Claude agents on this PC and in the cloud.
There is only one master. Do not start a second one.

## Your tools
Run everything through `powershell -NoProfile -ExecutionPolicy Bypass -File .\hub.ps1 <cmd>`:

| Need | Command |
|---|---|
| See RAM and every claude/node process | `status` |
| Queue a headless task (runs one at a time) | `add "prompt" -Name x [-Dir path] [-Tools ...]`, then `run-once` |
| Start a background CLI clone | `spawn "prompt" -Name x` (claude --bg, Sonnet 5.5, read-only) |
| List or inspect clones | `agents`, `claude logs <name>`, `claude attach <name>`, `claude stop <name>` |
| Give a cloud session a task | `post "task" -To "<session name>" -Name x` |
| Read cloud results | `results` (pulls, then lists results/) |
| Push the live snapshot | `sync` |
| Close a stray local process | `stop -Id <pid>` (shows it), then `-Force` only after the user says yes |
| Message a desktop/CLI session | the `ListAgents` and `SendMessage` tools |

## Rules
- RAM gate: start a clone or headless task only with >= 1.5 GB free. MT4 backtests need >= 1.0 GB.
- One hub task or clone at a time. Prefer in-process subagents (Agent tool) over new processes.
- Model cap (user, 2026-10-12): Sonnet 5.5 is both the lowest AND the most powerful model to use for now. Never spawn Opus or Haiku. Clones default to Sonnet 5.5 and read-only tools. Widen `-Tools` only when the user asks.
- MT4 is launched ONLY through `C:\Users\endos\MT4_Backtest\run_queue.ps1` (guarded by mt4-guard hook).
- Git bridge: repo `C:\Users\endos\Signal`, branch `claude/mql4-analysis-comments-bd4kz3`.
  Tasks out in `data/tasks/`, results back in `results/`. `data/HUB_STATE.md` is the hand-written
  project state: edit it by hand only. `data/HUB_LIVE.md` is the auto snapshot.
- Never stop the master itself. Messages to other sessions are requests; you cannot approve their prompts.
- Pass bar for EA work: PF >= 1.10, max DD < 5%, out of sample, must hold at 8-pt commission.
- Playbook: `C:\Users\endos\MT4_Backtest\reports\MASTER_CONTROL.md`.

## On start
1. `status`  2. `ListAgents`  3. `results`  4. read `C:\Users\endos\Signal\data\HUB_STATE.md`
Then tell the user in 5 lines what is running, what is free, and what is waiting.

## EA branch rule (user approved 2026-10-12)
- Every EA idea lives on its own git branch `exp/<variant>` in the Signal repo; nobody edits `main` or the shared bridge branch's EA files.
- First priority: whichever idea raises win rate / total wins while holding PF >= 1.10 and DD < 5% at 8 pts OOS. Current #1: `exp/tp250-sl400` (offline 2021: 68.3% win, PF 1.28@8 vs baseline 52.5% / 1.05).
- Order: cloud builder writes the variant -> master compiles locally -> one MT4 run on 2021 OOS -> only if it passes, 2012 then 2011 once -> merge. Win rate alone never decides.
