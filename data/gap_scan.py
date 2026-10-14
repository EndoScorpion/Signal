"""gap_scan.py - find holes in EURUSD history: M15 and H1 bars per month and weekday gaps > 1 day, for the tester copy and the MT4_Backtest copy."""
import struct, datetime, os, sys
from collections import defaultdict
def scan(path):
    raw = open(path, "rb").read()[148:]; n = len(raw) // 60; ts = [struct.unpack_from("<q", raw, k * 60)[0] for k in range(n)]; del raw
    dt = datetime.datetime.utcfromtimestamp
    per = defaultdict(int); gaps = []
    for k, t in enumerate(ts):
        d = dt(t); per[(d.year, d.month)] += 1
        if k and t - ts[k - 1] > 86400 and (t - ts[k - 1]) > 3 * 86400 or (k and 100 * 3600 < t - ts[k - 1] <= 3 * 86400 and dt(ts[k - 1]).weekday() < 4):
            gaps.append((dt(ts[k - 1]), dt(t), (t - ts[k - 1]) / 86400))
    return per, gaps, ts
for label, base in (("tester copy", r"C:\Users\endos\Desktop\mt4_tester\history\FXOpenEU-ECN Live Server"), ("MT4_Backtest copy", r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server")):
    for f, exp in (("EURUSD15.hst", 1990), ("EURUSD60.hst", 497)):
        per, gaps, ts = scan(os.path.join(base, f))
        thin = [(y, m, c) for (y, m), c in sorted(per.items()) if c < 0.8 * exp and not (y == 2010 and m <= 6) and not (y == 2026 and m >= 10)]
        print(f"\n{label} {f}: {len(ts):,} bars; thin months (<80% of ~{exp}): {thin if thin else 'none'}")
        big = [g for g in gaps if g[2] > 4]
        print("  gaps > 4 days:", [(f"{a:%Y-%m-%d}", f"{b:%Y-%m-%d}", round(d)) for a, b, d in big] if big else "none")
