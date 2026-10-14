"""mmr_edge_test.py - rung 1: does MMR predict forward M15 returns, gross of all costs?
Streams data/m15_metrics.csv. For each year and MMR quintile (cuts from the full sample), mean forward
return in points over H bars. Edge = Q5 - Q1 spread. Offline, no MT4. Run: python -I data/mmr_edge_test.py
MMR (c) Nasif Hossain 2019."""
import csv, math, os
from collections import defaultdict
CSV = r"C:\Users\endos\Signal\data\m15_metrics.csv"
HS = (4, 16, 96)            # 1h, 4h, 1 day ahead
ts, cl, mm, ep = [], [], [], []
for r in csv.DictReader(open(CSV)):
    ts.append(r["dt"]); cl.append(float(r["close"])); mm.append(float(r["mmr_6_12_18"])); ep.append(int(r["ts"]))
n = len(cl)
srt = sorted(mm); cuts = [srt[int(n * q / 5)] for q in (1, 2, 3, 4)]
def bucket(v): return sum(v > c for c in cuts)
acc = {h: defaultdict(lambda: [0, 0.0, 0.0]) for h in HS}      # (year,q) -> n,sum,sumsq
for i in range(n - max(HS)):
    y, q = ts[i][:4], bucket(mm[i])
    for h in HS:
        if ep[i + h] - ep[i] > h * 900 * 1.25: continue
        f = (cl[i + h] - cl[i]) * 1e5
        a = acc[h][(y, q)]; a[0] += 1; a[1] += f; a[2] += f * f
print("MMR cuts (quintile edges):", [round(c, 3) for c in cuts], "bars", n)
for h in HS:
    print(f"\nForward {h} bars: mean pts by MMR quintile Q1(low)..Q5(high); edge=Q5-Q1; z")
    for y in sorted({k[0] for k in acc[h]}):
        row = [acc[h][(y, q)] for q in range(5)]
        if min(r[0] for r in row) < 200: continue
        m = [r[1] / r[0] for r in row]
        v = lambda r: (r[2] / r[0] - (r[1] / r[0]) ** 2) / r[0]
        z = (m[4] - m[0]) / math.sqrt(v(row[4]) + v(row[0]))
        print(y, " ".join(f"{x:+6.2f}" for x in m), f" edge={m[4]-m[0]:+6.2f} z={z:+5.2f}")
