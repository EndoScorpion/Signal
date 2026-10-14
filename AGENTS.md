# Agent pool and MT4 queue (14 Oct 2026)

Board: `data/agent_board.json`, CLI: `tools/agent_board.py` (see its docstring). Research only: no orders, nobody but the MT4 runner touches LenovoLaptop, and nothing touches MT4_PAUSE.

## Schema
- `items[]`: `{id W0001, kind er|draft|parse|other, title, status open|claimed|done|failed, deps[], owner, claimed, result (repo path), note}`
- `mt4.queue[]`: `{id T0001, item, by, ea, symbol, tf, from, to, set, status queued|running|done|failed, runner, started, finished, report}`; `mt4.max_running = 1`
- `agents{name: {last_seen}}`, `log[]` (last 200), `rev` bumps on every write.

## Rules
1. Pull before, commit+push right after every board write (`git pull --rebase`; on conflict re-run the command on the fresh board). The file lock only guards one machine; git is the cross-agent lock.
2. Only agents in `MT4_AGENTS` (default `mt4-runner` = the session with Desktop Commander on LenovoLaptop) may `mt4-next`/`mt4-done`. `mt4-next` refuses while a job is running, so tests run one at a time.
3. `mt4-done` auto-adds a `parse` item for the report.
4. `reap --minutes 90` returns stale claims to `open`.

## Pool size: 3 cloud agents + 1 MT4 runner
- `er` (ER/report analysis) 1, `draft` (candidate EAs/set files) 1, `parse` (MT4 report to results/) 1.
- More is wasted: MT4 is the bottleneck (one test at a time), so drafting faster than the laptop can test only grows the queue, and every agent costs credits. Add a 2nd drafter only if the queue is empty for a whole MT4 cycle.
