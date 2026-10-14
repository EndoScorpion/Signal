# HANDOFF - web companion + MarketWatch build 041 (12 Oct 2026, 16:40)

Owner session: web/claude.ai build chat. MT4 not touched. Nothing deleted.

## Live links (artifact, private)
- Companion + MarketWatch files: artifact 4eg14ZNXTzt6qEkzudkPTq, version 1791493708-b41c (build 041 job guard).
- Original artifact 1d8df881... is the older build; do not republish over it.

## Unique local backups (copied, not moved)
- Signal\backups_web_build041_12Oct2026\MarketWatch_jobguard_build041_12Oct2026_1640.html
- Signal\backups_web_build041_12Oct2026\SignalLiveCompanion_build040_web_index_12Oct2026.html
- Signal\backups_web_build041_12Oct2026\patch_mw041_jobguard.py, patch_b040_companion.py

## State
- Build 041: history and HTML exports run in chunks with memory check, cool-down, Pause/Stop.
- Not browser-tested. Backtest runs and sandbox_container.html NOT chunked yet.
- Browser localStorage (slots, snapshots) is per browser and is not in any artifact. Export it from the app before moving machines.

## Pending (needs Nasif)
- Chunking of backtest runs and sandbox copy (not started).
- Decide whether to keep the .txt source backup prompt on.

## Cleanup check (12 Oct 2026, later)
- Delete rule: only exact duplicates beyond 3 copies. Checked Signal root and handoff folder by name, size and mtime. Non-MT4 duplicates found are at most 2 copies (for example HANDOFF_pirates_session_12Oct2026.md in root and handoff, same size and mtime). Nothing met the >3 threshold, so nothing was deleted.
- HUB_STATE has three versions (live, _backup, _edited). That is 3 copies, not more than 3, so none removed.
- MT4 files (Strong2010b*, .mq4 copies, QuotesDownloader, MT4_Backtest) were not opened, copied, or deleted.
- Keep limit (3 max recent unique copies) respected for my web backups: one copy of each build file in backups_web_build041_12Oct2026.
- Session idle after this note.
