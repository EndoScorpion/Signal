"""spread_stats.py - real EURUSD spread from FXOpen M1 bid/ask (ask close - bid close, in points; 5-digit).
TIME ZONE: the CSV clock is UTC, so the "hour" columns are UTC hours (MT4 server time = UTC+2, UTC+3 in US DST).
SOURCE: FXOpen QuotesDownloader raw M1 bid+ask (EURUSD, FXOpenEU-ECN). Streams the two CSVs inside the full-history zip in lockstep (low RAM). Outputs data/spread_stats.csv and prints
per-year mean/median/p90 and share of minutes <=2 and <=5 pts, plus mean by server hour for 2023-2026.
Note: M1 close quotes only (a minute-end snapshot), not tick-level spread. Concepts (c) Nasif Hossain."""
import zipfile, io, csv, os, datetime
from collections import defaultdict
Z = r"C:\Users\endos\Signal\data\quotes_download\2026-10-13_18-48-11\EURUSD_M1_2009-01-01-14-00-51_2026-10-06-00-00-00.zip"
zf = zipfile.ZipFile(Z)
def rows(name):
    for line in io.TextIOWrapper(zf.open(name), encoding="utf-8"):
        p = line.split(",")
        if len(p) >= 5 and p[0][:4].isdigit(): yield p[0], float(p[4])
bid, ask = rows("M1 bid.csv"), rows("M1 ask.csv")
yr = defaultdict(lambda: [0, 0.0, [0] * 41, 0, 0]); hr = defaultdict(lambda: [0, 0.0])
tb = next(bid); ta = next(ask); n = 0
while True:
    try:
        if tb[0] == ta[0]:
            sp = (ta[1] - tb[1]) * 1e5
            if -5 <= sp <= 400:
                y = tb[0][:4]; a = yr[y]; a[0] += 1; a[1] += sp; a[2][min(40, max(0, int(sp)))] += 1; a[3] += sp <= 2; a[4] += sp <= 5
                if y >= "2023": h = hr[int(tb[0][11:13])]; h[0] += 1; h[1] += sp
            tb = next(bid); ta = next(ask)
        elif tb[0] < ta[0]: tb = next(bid)
        else: ta = next(ask)
    except StopIteration: break
out = []
print("year   minutes  mean  median  p90   %<=2pts  %<=5pts")
for y in sorted(yr):
    c, s, h, le2, le5 = yr[y]; cum = 0; med = p90 = 0
    for i, v in enumerate(h):
        cum += v
        if not med and cum >= c * .5: med = i
        if not p90 and cum >= c * .9: p90 = i
    out.append([y, c, round(s / c, 2), med, p90, round(100 * le2 / c, 1), round(100 * le5 / c, 1)])
    print(y, f"{c:8d} {s/c:5.2f} {med:5d} {p90:5d}  {100*le2/c:6.1f}  {100*le5/c:6.1f}")
with open(r"C:\Users\endos\Signal\data\spread_stats.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "minutes", "mean_pts", "median", "p90", "pct_le2", "pct_le5"]); w.writerows(out)
print("\nmean spread (pts) by server hour, 2023-2026:", {h: round(v[1] / v[0], 1) for h, v in sorted(hr.items())})
