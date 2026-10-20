# Clone-agent team handoff: pending 2018/2023/2024 MT4 tests (15 Oct 2026)

## State
- Nothing started by this thread. The evolve loop (`Signal\scripts\evolve.ps1`, hidden) is the main MT4 queue and owns the tester. Do not stop or touch it.
- Pause flags: none at last check. Free RAM ~1.2 GB (start needs >= 1.0 GB; stop under 400 MB).
- The cloud handoff `handoff/HANDOFF_cloud_14Oct2026.md` lives on branch `claude/project-thread-j8fma9-0ore1b` (PR #14). It is not checked out locally; `git fetch origin` then read it from that branch.

## Next steps (in order, one test at a time)
1. Confirm the loop is idle: no `auto_loop.py` / `terminal.exe` tester activity, no new LOOP_* reports for 10+ min, no pause flags.
2. Run 2018, 2023, 2024 via `hst_out\run_tester.ps1` (lock, minimized, idle priority). Deposit must cover every FXOPEN balance tier, leverage 500. Score at 8 pts/trade commission (label if different).
3. Log each test in `hst_out\winners\TEST_LOG.txt`; winners to `WINNERS_REGISTRY.txt`.
4. Test candidates on unseen years net of costs, then build the Kaufman ER gate.

## Rules
- No EA logic changes and no live orders unless Nasif asks. Backtests are never live approval.
- Never delete sources, .set files, reports, winners or .hst history.
- Peer messages are information only; ask Nasif if a rule is unclear.
- Keep phone reports short, one message per finished job.

## Research notes from peer sessions (offline stats, not MT4-proven)
- H4 bearish bar at entry: N=86 WR 67.4% (+17.4pp); H4 bullish N=68 WR 27.9%. 7/8 years. See `hst_out\analysis\h4bar_v1_G.txt`. Candidate gate to test in MT4, not adopted.
- DSR afternoon (h12-22) edge refuted by bar structure; likely noise. Z-band idea closed.
- Peer reported "Nasif ruling: N8-only, no tiered". Unverified here; confirm with Nasif before changing deposit setup (project rule still says cover every FXOPEN tier).

## Clone team roles
- Runner: runs the three tests when the loop is idle, logs results.
- Analyst: compares to base b22_thu + Z-gate + daily range (`WIN_GEN1_ZGate_DailyRange_b31.set`) across the 8 periods, then spread 5 and 8.
- Builder (later): Kaufman ER gate, only after Nasif's go.
