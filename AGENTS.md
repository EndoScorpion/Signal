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

## Self-improvement and win rate (added 14 Oct 2026)
- `candidates{id: {parent, gen, tests, n, wins, win_rate, avg_net, fitness, momentum, history[]}}`. `mt4-queue --cand ID [--parent PID]` registers a candidate; gen = parent gen + 1.
- `mt4-done ... --n N --wins W --net AVG_NET_PCT` (net of ALL costs) scores it. fitness = avg_net x sqrt(n), 0 when n < 30 or net <= 0 (a "win" only counts after costs). momentum = fitness minus the previous test (or the parent's fitness).
- `mt4-next` takes the queued test whose parent lineage has the highest positive momentum, then parent fitness, then oldest first. Still one test at a time.
- Hold-out numbers are what count; backtests are not guarantees.
## Division of labor (added 14 Oct 2026)

### Exclusive domains (only this agent touches it)
- `signal-a2` (cloud): ER studies, candidate drafting (EAs/.set in `candidates/`), fitness scoring, `candidates{}` on the board.
- `mt4-runner` (RC on LenovoLaptop MQL4): starts/stops MT4 tests, `mt4-next`/`mt4-done`, files under the MQL4 folder. One test at a time.
- Coordinator (project chat): routing, briefs, project memory. Never edits repo code or the board.
- Thread agents (dashboard, docs, etc.): only the files their PR branch owns; one branch per thread.

### Shared resources: write authority
| Resource | Section | Writer |
|---|---|---|
| `data/agent_board.json` | `items[]` | any cloud agent via `tools/agent_board.py` (claim before work) |
| | `mt4.queue[]` add | any cloud agent (`mt4-queue`) |
| | `mt4` run state | `mt4-runner` only |
| | `candidates{}` scores | `signal-a2` only (from `mt4-done` numbers) |
| Signal repo `main` | all | nobody directly; PRs only, the user merges |
| Signal repo branches | own branch | the thread that created it |
| `AGENTS.md`, `cost_model.json` | all | via PR, user approves |

### Conflict rules
1. Board: whoever pushes first wins; the loser pulls, re-reads, re-runs its command. Never hand-edit the JSON.
2. Item already `claimed` by another live agent: pick another item; `reap --minutes 90` frees stale claims.
3. Two agents want the same file: the branch owner edits; the other writes a new file and asks the owner via the coordinator.
4. MT4 busy: queue and wait; never start a 2nd MT4, `evolve.ps1` or `auto_loop.py`.
5. Rule clash (e.g. commission 5 vs 8 pts): stop, report both figures, ask the user.

### Self-improvement standing orders
- Goal for all: raise win rate AND number of wins, net of ALL costs, on hold-out data.
- Cloud agents propose candidates (`mt4-queue --cand`); only `mt4-runner` runs tests.
- `signal-a2` scores fitness (avg_net x sqrt(n), 0 if n<30) and tells the drafter what to mutate next.
- Add files, don't overwrite; keep a .txt backup of new code in `backups/`. No orders, ever.
