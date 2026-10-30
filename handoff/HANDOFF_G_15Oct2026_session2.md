# Clone G Handoff — 15 Oct 2026 (session 2)

## Status
RAM pressure on desktop. Moving to cloud session. Laptop evolve loop (PID 18076) still holds mt4_tester2 run.lock — do NOT kill it.

## MT4 Tests QUEUED (not yet run — waiting for lock to free)
Run in order via run_tester.ps1 on desktop when lock frees:

1. **Base b62** (establish baseline for MR_RegimeSwitch_b62 parent strategy)
```
powershell -File "C:\Users\endos\Desktop\hst_out\run_tester.ps1" -Expert "MR_RegimeSwitch_b62" -SetFile "MR_RegimeSwitch_b62_base.set" -From "2011.01.01" -To "2026.10.01"
```

2. **Skip h16-19** (block hours 16-23 — h16-19 confirmed bad in Python, -20pp WR)
```
powershell -File "C:\Users\endos\Desktop\hst_out\run_tester.ps1" -Expert "MR_RegimeSwitch_b62" -SetFile "MR_RegimeSwitch_b62_skip_h16h19.set" -From "2011.01.01" -To "2026.10.01"
```

3. **Allow h05-h09** (best window: WR=63% +13pp offline, N=27 — needs MT4 confirm)
```
powershell -File "C:\Users\endos\Desktop\hst_out\run_tester.ps1" -Expert "MR_RegimeSwitch_b62" -SetFile "MR_RegimeSwitch_b62_allow_h05h09.set" -From "2011.01.01" -To "2026.10.01"
```

Set files are in BOTH:
- `C:\Users\endos\Desktop\hst_out\*.set`
- `C:\Users\endos\Desktop\mt4_tester2\tester\*.set`

Score at **6 pts RT** (FXOpen EURUSD ECN). Report in points.

## Python Offline Results (parent.csv, 154 sells, MR_RegimeSwitch_b62)
- Base (h2-23): N=154, WR=50.0%, avg=+101pts
- Skip h16-19: N=144, WR=51.4% (+1.4pp), avg=+111pts
- Allow h05-09: N=27, WR=63% (+13pp), avg=+184pts — P1(2010-14) weak 20%, suspect
- H04 bad: WR=30%, H11: WR=17%, H22: WR=0% — also worth blocking
- allyrs_base.csv (465 trades): H08 best WR=77%, H04/H11 confirmed bad

## Files Created This Session
- `hst_out/MR_RegimeSwitch_b62_base.set` — 136-param base .set
- `hst_out/MR_RegimeSwitch_b62_skip_h16h19.set` — HourTo=15
- `hst_out/MR_RegimeSwitch_b62_allow_h05h09.set` — HourFrom=5, HourTo=9
- `hst_out/analysis/skip_h16h19_G.txt` — offline skip_h16h19 analysis
- `hst_out/analysis/hoursweep_v1_G.txt` — full hour window sweep results
- `hst_out/analysis/cloud_G_hoursweep_v1.py` — hour sweep script
- `data/H4BEAR_GATE_FINDINGS.md` — committed + pushed

## Key Context (EA mismatch — read carefully)
Two separate EAs:
- **Strong2010b_claude_b31** — current winner, WIN_GEN1 .set, SMA1200 regime. Use for evolve loop / G2 tests.
- **MR_RegimeSwitch_b62** — parent strategy, SMA3000 regime, ZTrigger=3.515, HoldBars=125, SLPts=1125. G-scripts (runner_G.py, parent.csv, 154 trades) analyze THIS EA. All hour research above is for b62.

Do NOT mix their .set files.

## b62 EA Key Params
From `mt4_tester2/tester/MR_RegimeSwitch_b62.ini`:
- ZTF=15, ZPeriod=15, ZTrigger=3.515
- HoldBars=125, SLPts=1125, TPPts=0
- RegimePeriod=3750, SideMode=1 (sell-only)
- HourFrom=2, HourTo=28 (base = h2-23)
- AtrCapPts=112, MaxSpreadPts=30
- BlockRollover=1, RollFrom=23, RollTo=1

## H4 Bear Gate (from prior session + Clone C)
- H4 bearish bar: WR=67.4%, N=86, +17.4pp vs base 50% in parent.csv
- cp<=0.50 threshold adds NOTHING — use boolean close<open only
- H4bear + CI-16 (Clone C HOLD): 69.4%, N=36 — not standalone P1 but valid filter
- Needs new EA parameter for exact H4 close<open gate (UseH4TrendAnchor uses SMA, not bar close)

## Next Steps for Cloud Session
1. Wait for MT4 lock to free, then run the 3 tests above
2. Write hoursweep MT4 script (sweep HourFrom/HourTo in evolve format) — G5 candidate
3. Coord relay topic: `endoscorpion-goon` on ntfy.sh — post findings there

## Git Branch
`claude/project-thread-j8fma9` — pushed at commit 04ce9c7
