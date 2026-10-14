"""tz_offset_check.py - compare FXOpen CSV (zip) timestamps with the MT4 .hst timestamps to find the time offset per month (is the CSV UTC while MT4 history is server time?)."""
import zipfile, io, datetime, calendar, time
import numpy as np
Z = r"C:\Users\endos\Signal\data\quotes_download\2026-10-13_18-48-11\EURUSD_M1_2009-01-01-14-00-51_2026-10-06-00-00-00.zip"
HST = r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD1.hst"
dt = np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"), ("tv", "<i8"), ("sp", "<i4"), ("rv", "<i8")]); assert dt.itemsize == 60
a = np.memmap(HST, dtype=dt, mode="r", offset=148); T = a["t"]; C = a["c"]
print("machine local tz offset (hours from UTC):", -time.timezone / 3600, "| DST now:", time.daylight and time.localtime().tm_isdst)
import sys
TOL = 3e-5 if "--loose" in sys.argv else 6e-6
want = {f"{y}.{m:02d}" for y in (2010, 2011, 2012, 2013, 2016, 2017, 2019, 2020, 2021) for m in (1, 2, 7, 8, 11, 12)} | {"2015.10", "2015.11", "2018.10", "2018.11", "2010.09", "2010.12"} if "--loose" in sys.argv else {f"{y}.{m:02d}" for y in (2011, 2012, 2015, 2018, 2022, 2023, 2024, 2025) for m in (1, 2, 3, 4, 7, 10, 11, 12)}
sample = {}; zf = zipfile.ZipFile(Z)
for line in io.TextIOWrapper(zf.open("M1 bid.csv"), encoding="utf-8"):
    k = line[:7]
    if k in want and len(sample.setdefault(k, [])) < 4000 and int(line[14:16]) % 7 == 0 and 8 <= int(line[11:13]) <= 18:
        p = line.split(","); sample[k].append((calendar.timegm(time.strptime(p[0], "%Y.%m.%d %H:%M:%S")), float(p[4])))
print("month | best offset (hours added to CSV time to reach the .hst time) : matches of up to N")
for k in sorted(sample):
    pts = sample[k]; best = None
    for off in range(-3, 10):
        ts = np.array([x[0] for x in pts]) + off * 3600; idx = np.searchsorted(T, ts); ok = idx < len(T); idx = np.where(ok, idx, 0)
        hit = ok & (T[idx] == ts); m = int(np.sum(hit & (np.abs(C[idx] - np.array([x[1] for x in pts])) < TOL)))
        if best is None or m > best[1]: best = (off, m)
    print(f"{k} | {best[0]:+d}h : {best[1]}/{len(pts)}")
