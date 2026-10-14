"""ssr_edge_test.py - SSR (slope-to-slope ratio, Nasif Hossain): slope of a small SMA divided by slope of a larger SMA, EURUSD M15.
Forward return (pts, gross) by SSR quintile per year at 4 and 16 bars; edge = Q5-Q1. Sells profit when forward return is negative.
Offline derived data only, never live approval. Run: python -I data/ssr_edge_test.py [fast=20] [slow=200]"""
import struct, sys, math, datetime
from collections import defaultdict
FAST = int(sys.argv[1]) if len(sys.argv) > 1 else 20; SLOW = int(sys.argv[2]) if len(sys.argv) > 2 else 200
data = open(r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD15.hst", "rb").read()[148:]
n = len(data) // 60; T = []; C = []
for i in range(n):
    t, o, h, l, c, tv, sp, rv = struct.unpack_from("<qddddqiq", data, i * 60); T.append(t); C.append(c)
def sma(p):
    out = [None] * n; s = 0.0
    for i, v in enumerate(C):
        s += v
        if i >= p: s -= C[i - p]
        if i >= p - 1: out[i] = s / p
    return out
f = sma(FAST); s_ = sma(SLOW)
rows = []
for i in range(SLOW + 2, n - 17):
    sf = (f[i] - f[i - 1]) * 1e5; ss = (s_[i] - s_[i - 1]) * 1e5
    if abs(ss) < 0.05: continue
    r = max(-10.0, min(10.0, sf / ss))
    y = datetime.datetime.fromtimestamp(T[i], datetime.timezone.utc).year
    rows.append((y, r, (C[i + 4] - C[i]) * 1e5, (C[i + 16] - C[i]) * 1e5, max(C[i:i + 17]) - min(C[i:i + 17])))
rs = sorted(x[1] for x in rows); q = [rs[int(len(rs) * k / 5)] for k in (1, 2, 3, 4)]
print(f"SSR = slope(SMA{FAST}) / slope(SMA{SLOW}), quintile edges {[round(x,3) for x in q]}, bars {len(rows)}")
def qi(r): return sum(r > e for e in q)
for h, name in ((2, "4 bars"), (3, "16 bars")):
    print(f"\nForward {name}: mean pts by SSR quintile Q1(low)..Q5(high); edge = Q5-Q1")
    acc = defaultdict(lambda: [[0, 0.0] for _ in range(5)])
    for x in rows:
        a = acc[x[0]][qi(x[1])]; a[0] += 1; a[1] += x[h]
    neg = 0; tot = 0
    for y in sorted(acc):
        m = [a[1] / a[0] if a[0] else 0 for a in acc[y]]
        print(y, " ".join(f"{v:+6.2f}" for v in m), f" edge={m[4]-m[0]:+.2f}"); tot += 1; neg += (m[4] - m[0]) < 0
    print(f"years with edge<0 (high SSR falls more): {neg}/{tot}")

print("\nDivergence vs chaos: next-16-bar range (pts) by slope state (aligned = same sign, ratio 0.2..5; opposite = slopes of opposite sign; extreme = ratio beyond 0.2..5)")
def st(r):
    if r < 0: return "opposite"
    return "aligned" if 0.2 <= r <= 5 else "extreme"
acc = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
for x in rows:
    a = acc[x[0]][st(x[1])]; a[0] += 1; a[1] += x[4] * 1e5
hi = 0; tot = 0
for y in sorted(acc):
    m = {k: (v[1] / v[0] if v[0] else 0) for k, v in acc[y].items()}
    print(y, " ".join(f"{k}={m.get(k,0):6.1f} (n={acc[y][k][0]})" for k in ("aligned", "opposite", "extreme")))
    tot += 1; hi += m.get("opposite", 0) > m.get("aligned", 0)
print(f"years where opposite-slope (diverging) bars precede a wider range than aligned: {hi}/{tot}")
