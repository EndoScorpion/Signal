# SAFE-RUN Task Queue
**Updated:** 2026-10-18T00:24Z

---

## TASK 1 — T131 MT4 Strategy Tester (PRIORITY — EA READY)
**Status:** PENDING — EA FILE READY

**EA file:** `T131_EA.mq4` — pull from Signal repo branch `claude/project-thread-l223a6`
or copy from: `C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\MQL4\Experts\T131_EA.mq4`

**Run MT4 Strategy Tester:**
- Symbol: EURUSD H1
- EA: T131_EA
- Date range: 2019-01-01 to 2023-12-31
- Model: Every tick (or OHLC on H1)
- Initial deposit: 10000
- Lot size: 0.01

**EA Parameters (defaults are correct):**
- Magic=1310, ATRPeriod=14, RankWindow=100, RankThreshold=20
- ConsecBars=3, Lo10Period=10, WickMinATR=0.2, BodyMaxATR=1.5
- EMAperiod=50, EMADistATR=0.5, HoldBars=4, EntryHourUTC=13
- LotSize=0.01, CommissionPts=8

**Report:** n trades, WR%, avg net pips, max DD, per-period (2019-21, 2022-23)

**Output file:** `/mnt/project-files/results/t131_mt4_validation.md`

---

## TASK 2 — TEST_LOG Merge
**Status:** DONE ✅ (7080 lines, confirmed)

---

## TASK 3 — Chaos Theories T-C1 through T-C5
**Status:** PENDING

Run T-C1 through T-C5 on EURUSD H1 FXOpen ECN data. Full cost model.
Report: n, WR%, avg net %/trade, PF per theory.

**Output file:** `/mnt/project-files/results/chaos_theories_results.md`

---

## T131 EA .txt backup
For safety, .txt copy: same content as T131_EA.mq4 — see `/mnt/project-files/backups/T131_EA.txt` (written below by cloud thread)
