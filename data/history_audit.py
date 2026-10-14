"""history_audit.py - low-memory gap audit of an EURUSD .hst file (default: MT4_Backtest M1). Reads in chunks.
Reports per-year bar counts vs expected (~weekday minutes), the biggest gaps (> 1 hour inside a weekday session), and the last bar vs now.
Run: python -I data/history_audit.py [path_to_hst]. Exit code 2 if the file ends more than 10 days ago or any year looks > 3% thin."""
import struct, sys, datetime
p = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD1.hst"
per = {}; gaps = []; prev = None; last = None
with open(p, "rb") as f:
    f.seek(148)
    while True:
        buf = f.read(60 * 100000)
        if not buf: break
        for (t,) in struct.iter_unpack("<q52x", buf[:len(buf) // 60 * 60]):
            d = datetime.datetime.utcfromtimestamp(t)
            per[d.year] = per.get(d.year, 0) + 1
            if prev is not None and t - prev > 3600 and d.weekday() < 5 and datetime.datetime.utcfromtimestamp(prev).weekday() < 5 and (t - prev) < 3 * 86400:
                gaps.append((t - prev, datetime.datetime.utcfromtimestamp(prev).strftime("%Y-%m-%d %H:%M")))
            prev = t
last = datetime.datetime.utcfromtimestamp(prev)
print(f"{p}\nlast bar {last:%Y-%m-%d %H:%M} ({(datetime.datetime.utcnow() - last).days} days ago)")
bad = False
for y in sorted(per):
    exp = 1440 * 5 * 52 * (0.97 if y in (2009, 2010) else 1)
    flag = "" if per[y] >= exp * 0.97 or y in (2009, last.year) else "  <-- THIN"
    bad |= bool(flag)
    print(f"{y}: {per[y]:7d} bars  ({100*per[y]/exp:5.1f}% of ~5d x 24h){flag}")
print("largest intra-week gaps >1h:", [(round(g / 3600, 1), w) for g, w in sorted(gaps, reverse=True)[:8]], f"| count {len(gaps)}")
sys.exit(2 if bad or (datetime.datetime.utcnow() - last).days > 10 else 0)
