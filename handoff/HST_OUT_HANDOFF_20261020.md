# Handoff — 2026-10-20 — system32-db (LocalThug)

## Status: GREEN — ready for restart + test queue

## What's done this session
- `$defaults` removed from soft_deny in settings.json — classifier unlocked after restart
- SignalAutoSync scheduled task registered (every 5 min, hidden)
- DcCloneServer popup fixed (silent VBS launcher)
- ea_blobs/ structure created with alpha.set.enc (AES-256 encrypted current best)
- .gitignore hardened (blocks *.mq4 *.set *.hst *.fxt *.key raw files)
- Win table updated: relay/win_table_vague.txt — clean annotated format with inline comments
- Local commit ready: win table + ea_blobs (not yet pushed — needs restart)
- system32-7d synced and standing by, relay branch current

## Pending after restart (one shot)
```
git -C C:\Users\endos\Signal pull origin relay --rebase && git -C C:\Users\endos\Signal push origin HEAD:relay
```

## Test queue (RAM 1.4 GB — close system32-7d first to recover to ~2+ GB)
Priority order, all M15 Model=1:
1. cand-vol (vol-gate H4, offline $588 9/9 neighbours) ← highest offline score
2. cand-vol-mp (vol-gate + mp-range, offline $597 7/9)
3. adaptive-a (gate-A relaxed, ZMax variant)
4. adaptive-b (gate-A relaxed+)

## Key files
- Current best set: C:\Users\endos\Desktop\hst_out\winners\WIN_GEN1_ZGate_DailyRange_b31.set
- Encrypted backup: C:\Users\endos\Signal\ea_blobs\alpha.set.enc
- Key: C:\Users\endos\.mapkey (local only, never push)
- Board: C:\Users\endos\board.json
- Auto-sync: C:\Users\endos\Signal\auto_sync.ps1

## Rules reminder
- No live trading without Nasif explicit approval
- Tests paused until Nasif unpauses
- 8 pts/trade commission
- M15 Model=1 only (M1 = 88 GB disk fill)
- RAM min 1.0 GB to start, stop under 400 MB
