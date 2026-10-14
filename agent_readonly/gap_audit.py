"""gap_audit.py - read-only M1 .hst gap/integrity audit. Pure Python, streaming, low RAM. Usage: python -I gap_audit.py HST OUT.txt
Counts weekday gaps > 5 min (Fri >= 20:00 UTC through Sun excluded), missing minutes, longest gaps, duplicate/backwards timestamps, per year."""
import sys, struct, array, datetime, collections
f, out = sys.argv[1], sys.argv[2]
T = array.array("i")
with open(f, "rb") as fh:
    hdr = fh.read(148); ver = struct.unpack_from("<i", hdr, 0)[0]
    size = 44 if ver == 400 else 60
    while True:
        buf = fh.read(size * 200000)
        if not buf: break
        for i in range(0, len(buf) // size * size, size):
            T.append(struct.unpack_from("<i", buf, i)[0])
n = len(T)
def ts(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
def weekend(t):
    d = (t // 86400 + 3) % 7; h = (t % 86400) // 3600
    return d in (5, 6) or (d == 4 and h >= 20)
yr = collections.defaultdict(lambda: [0, 0, 0, 0, 0])  # bars, gaps>5m, missing minutes, dup, backwards
top = []
for i in range(n):
    y = 1970 + int(T[i] // 31556952)
    yr[y][0] += 1
    if i == 0: continue
    dt = T[i] - T[i - 1]
    if dt == 0: yr[y][3] += 1
    elif dt < 0: yr[y][4] += 1
    elif dt > 300 and not weekend(T[i - 1]):
        yr[y][1] += 1; yr[y][2] += dt // 60 - 1; top.append((dt, T[i - 1]))
top.sort(reverse=True)
L = [f"{f}\nhst v{ver}, {n} bars, {ts(T[0])} .. {ts(T[-1])}",
     "year  bars    weekday_gaps>5m  missing_min  dup  backwards  (weekday minutes per year ~ 370,000 expected)"]
for y in sorted(yr): b = yr[y]; L.append(f"{y}  {b[0]:7d}  {b[1]:8d}  {b[2]:10d}  {b[3]:4d}  {b[4]:5d}")
L.append("\nLongest weekday gaps (start UTC, hours):")
for dt, t in top[:20]: L.append(f"{ts(t)}  {dt/3600:.1f}h")
open(out, "w").write("\n".join(L) + "\n"); print("\n".join(L))
