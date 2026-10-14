"""tz_transitions.py - find when the CSV->MT4-server offset flips between +2h and +3h (US or EU daylight saving?), using original server-time months."""
import zipfile, io, calendar, time, datetime, collections
import numpy as np
Z = r"C:\Users\endos\Signal\data\quotes_download\2026-10-13_18-48-11\EURUSD_M1_2009-01-01-14-00-51_2026-10-06-00-00-00.zip"
HST = r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD1.hst"
dt = np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"), ("tv", "<i8"), ("sp", "<i4"), ("rv", "<i8")])
a = np.memmap(HST, dtype=dt, mode="r", offset=148); T = a["t"]; C = a["c"]
days = collections.defaultdict(list)
want = set()
for y in (2019, 2020, 2021, 2025):
    d = datetime.date(y, 1, 1)
    while d.year == y:
        if d.weekday() in (1, 3): want.add(d.strftime("%Y.%m.%d"))   # Tue and Thu samples (covers every week, dense around switches)
        d += datetime.timedelta(days=1)
zf = zipfile.ZipFile(Z)
for line in io.TextIOWrapper(zf.open("M1 bid.csv"), encoding="utf-8"):
    k = line[:10]
    if k in want and line[11:13] in ("10", "11") and len(days[k]) < 90:
        p = line.split(","); days[k].append((calendar.timegm(time.strptime(p[0], "%Y.%m.%d %H:%M:%S")), float(p[4])))
res = []
for k in sorted(days):
    pts = days[k]; best = (None, -1); ts0 = np.array([x[0] for x in pts]); cl = np.array([x[1] for x in pts])
    for off in range(0, 7):
        ts = ts0 + off * 3600; idx = np.searchsorted(T, ts); ok = idx < len(T); idx = np.where(ok, idx, 0)
        m = int(np.sum(ok & (T[idx] == ts) & (np.abs(C[idx] - cl) < 3e-5)))
        if m > best[1]: best = (off, m)
    res.append((k, best[0], best[1], len(pts)))
prev = None
for k, off, m, n in res:
    tag = off if m >= 0.6 * n else f"?({off}:{m}/{n})"
    if tag != prev: print(k, "->", tag); prev = tag
