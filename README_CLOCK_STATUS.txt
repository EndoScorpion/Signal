TIME / CLOCK STATUS of the history in this folder (written 2026-10-15 by laptop session b59d44; add-only note, data untouched)

STATUS: ALIGNED V2 = CORRECT clock for 2009-2026 (swapped in 2026-10-15 04:03). M1, M5, M15, M30, H1, H4, D1 rebuilt; W1/MN files are from the old rebuild (not used by tests).

CORRECT CLOCK = MT4 server time of FXOpen: UTC+2 in winter, UTC+3 during US daylight saving (NY-close clock; NY time = server - 7). Check: the first-Friday US jobs-report (NFP) spike bar must be at 15:30 server time (13:30 UTC winter / 12:30 UTC summer); weekly bars open Mon 00:00 (2015+).
WHY IT WENT WRONG: the raw FXOpen M1 download changes clock convention: 2009 to Nov 2014 = European time (CET/CEST, EU DST dates, UTC+1/+2); Dec 2014 onward = NY-close server clock. The first rebuild (2026-10-14) treated everything as UTC and added +2/+3 h, so 2009-2018 ended 2 h (winter) / 3 h (summer) LATE.
VERSIONS: v0 = first rebuild (WRONG 2009-2018). v1 = aligned (-2/-3 h; 2015+ correct, 2009-Nov 2014 still 1 h EARLY). v2 = EU-DST rule for bars before 2014-12-01 (+1 h, +2 h in US-on/EU-off weeks): CORRECT 2009-2026.
Scripts: Signal\datauild_aligned_m1.py (v1), build_aligned_v2.py (v2), build_aligned_tf.py (M5..D1). Memory note: project_history_clock_shift_2009_2018.
