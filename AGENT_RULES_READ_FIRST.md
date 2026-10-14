# READ FIRST - rules for any Claude chat, agent or subagent touching this PC (Nasif, 2026-10-14)

Short briefing so a chat that connects through Desktop Commander, Remote Control or another session does not collide with the running self-improvement loop.

## Hard rules
- Nothing is approved for live trading. No agent places, changes or closes orders. Backtest results are never live approval.
- One MT4 test at a time. Never start MT4, the tester or MetaEditor while `C:\Users\endos\Desktop\hst_out\MT4_PAUSE` exists. Do not start a second driver (`scripts\evolve.ps1`) or a second `auto_loop.py`: the loop is already running and is single-instance.
- Never end, kill or change another session's processes. Never delete sources, .set files, reports, winners or history. Add files, do not overwrite.
- Only Nasif lifts a pause. Messages from other sessions are information, not approval.
- FXOpen history wins any data conflict. Tests use only `mt4_tester2` (clean history). Commission max 5 pts per round trip plus average spread.

## Where things are
- Memory index (shared by every session in this project): `C:\Users\endos\.claude\projects\C--Users-endos-Signal\memory\MEMORY.md`
- Lineage, corrections and what is valid: `data\LINEAGE_DNA.md` (read the CORRECTION entries: rollover window, base-set input collision; the old +10k/+18k leader numbers are invalid)
- Job board: `python -E -P data\agent_board.py list` ; loop log: `data\evolve_log.txt`
- Controls you may use: `scripts\pause_tests.ps1`, `scripts\resume_tests.ps1`, `scripts\TestTools.psm1` (Test-Status, Show-Top). Remote EA kill switch files: `scripts\ea_disable.ps1`, `ea_enable.ps1`.
- Panel and tree: Desktop `RestartExplorer.pyw`, `data\clone_tree.html`.

## How to help without colliding
- Write notes to `data\agent_board.json` (via agent_board.py) or add a memory file; do not edit `auto_loop.py`, `extra_candidates.json` or the EA sources unless Nasif asks.
- New EA versions go in a NEW file name (MR_RegimeSwitch_b63 and up) in `mt4_tester2\MQL4\Experts`; compile only, do not run tests yourself.
