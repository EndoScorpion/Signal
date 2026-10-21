# Handoff — 2026-10-20 — system32-db (LocalThug)
# RESTART HANDOFF — written just before session close

## First thing on new session
```
git -C C:\Users\endos\Signal pull origin relay --rebase
git -C C:\Users\endos\Signal push origin HEAD:relay
```

## Status: GREEN
- $defaults removed from soft_deny (fix_settings.ps1 confirmed OK)
- SignalAutoSync task registered (5 min, hidden)
- DcCloneServer popup fixed
- ea_blobs/alpha.set.enc — current best encrypted
- .gitignore hardened
- Win table + handoff committed locally (not yet pushed)

## Test queue (after push, RAM permitting)
1. cand-vol — M15 Model=1 — top priority
2. cand-vol-mp — M15 Model=1
3. adaptive-a/b — M15 Model=1

## Key paths
- Best set: C:\Users\endos\Desktop\hst_out\winners\WIN_GEN1_ZGate_DailyRange_b31.set
- Encrypted: C:\Users\endos\Signal\ea_blobs\alpha.set.enc
- Key: C:\Users\endos\.mapkey (local only)
- Board: C:\Users\endos\board.json
- Auto-sync: C:\Users\endos\Signal\auto_sync.ps1

## Rules
- No live trading without explicit Nasif approval
- Tests paused until Nasif unpauses
- 8 pts/trade commission
- M15 Model=1 only
- RAM min 1.0 GB to start
