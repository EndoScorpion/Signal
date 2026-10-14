# Handoff - cloud session -> local session, 2026-10-14
Branch: claude/project-thread-j8fma9-0ore1b | Draft PR #14 (no CI, no reviews yet)

## Done
- Desktop WIP snapshot triaged: kept code/reports/backups; excluded binaries, logs, .hst, zips, _usb_backup_stage, adb_tools via .gitignore.
- No MT4 tests run, no EA logic changed, no orders.

## Findings to act on (from data/*.md; all unvalidated leads)
- g7a (BlockADX 24) is in-sample tuned; FAILS 2015/2016/2018 (PF 0.70/0.59/0.70). Not validated.
- DIVERGENCE_LOSS_MAP: 3479 trades, -97872 pts. Worst: gap_diverging (-48.5 pts/trade, 43% WR), stack_diverging (-40.7). Converging buckets lose far less -> test "skip diverging entries" filter.
- ALT_WIN_LOGIC: best zfade_N20_k2.5_H48_buy (+16 pts net, 11/17 yrs). Replay only; confirm in MT4.
- DSR_REPORT: best g2_AtrCapPts_90 DSR 0.909 (<0.95 gate).

## Next (needs local PC + user go; MT4 needs ~1 GB free RAM)
1. Paste the 2015 `OK ... in X min` result and gap-scanner output; run 2018/2023/2024 (spread 6, commission 6, every tick, SimDeposit 10000).
2. Test diverging gap/stack skip filter + zfade_N20_k2.5_H48_buy on unseen years, net of costs; reject if inconsistent across periods.
3. Build Kaufman ER gate + MMR (keep Nasif Hossain attribution), then validate out of sample.
4. Unknown: item 2 of the original "Unfinished Work" list was truncated.
