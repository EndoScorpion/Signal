"""slope_map.py - SMA slope, acceleration, jerk (rate of acceleration), slope variability at entry, per logic/report,
plus a market-wide yearly timeline. Offline, no MT4.
Definitions (M15): slope = SMA20 change over 8 bars (pts/bar); accel = slope - slope 8 bars ago; jerk = accel - accel 8 bars ago;
slope_vol = std of slope over last 24 bars; regime slope = ~H1 SMA1200 (4800 M15 bars) change over 96 bars (pts/day); regime accel = change of that over 96 bars.
Outputs: slope_map.csv (per report), slope_trades.csv (per trade), slope_timeline.csv (market per year).
Run: python -I data/slope_map.py [regex]. Slope/MMR concepts (c) Nasif Hossain."""
import os, sys, csv, re, datetime, importlib.util, statistics as st
DATA = r"C:\Users\endos\Signal\data"; HST = r"C:\Users\endos\Desktop\hst_out"
spec = importlib.util.spec_from_file_location("al", os.path.join(DATA, "auto_loop.py"))
al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
dt, cl, ab = [], [], []
for r in csv.DictReader(open(os.path.join(DATA, "m15_metrics.csv"))):
    dt.append(r["dt"]); cl.append(float(r["close"])); ab.append(float(r["close_above_sma20_pts"]))
n = len(cl); idx = {d: i for i, d in enumerate(dt)}
sma = [cl[i] - ab[i] * 1e-5 for i in range(n)]
S = [None] * n
for i in range(8, n): S[i] = (sma[i] - sma[i - 8]) / 8 * 1e5
cs = [0.0]
for c in cl: cs.append(cs[-1] + c)
W = 4800
R = [None] * n
for i in range(W - 1, n): R[i] = (cs[i + 1] - cs[i + 1 - W]) / W
def g(a, i, lag=0): j = i - lag; return a[j] if j >= 0 else None
def feat(i):
    s, s8, s16 = S[i], g(S, i, 8), g(S, i, 16)
    if None in (s, s8, s16) or i < 24: return None
    r0, r1, r2 = R[i], g(R, i, 96), g(R, i, 192)
    if None in (r0, r1, r2): return None
    return (s, s - s8, (s - s8) - (s8 - s16), st.pstdev([S[j] for j in range(i - 23, i + 1)]),
            (r0 - r1) * 1e5, ((r0 - r1) - (r1 - r2)) * 1e5)
NAMES = ["slope", "accel", "jerk", "slope_vol", "reg_slope", "reg_accel"]
# market timeline per year
yr = {}
for i in range(W + 192, n, 4):
    f = feat(i)
    if f: yr.setdefault(dt[i][:4], []).append(f)
with open(os.path.join(DATA, "slope_timeline.csv"), "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(["year"] + ["mean_abs_" + x for x in NAMES])
    for y in sorted(yr): w.writerow([y] + [round(sum(abs(f[k]) for f in yr[y]) / len(yr[y]), 3) for k in range(6)])
pat = sys.argv[1] if len(sys.argv) > 1 else r"^(WIN_GEN1_.*sp5|LOOP_.*sp5)\.htm$"
rows, tr_out = [], []
for fn in sorted(os.listdir(HST)):
    if not re.search(pat, fn): continue
    pts = []
    for t, pnl in al.trades_from_report(os.path.join(HST, fn)):
        d = datetime.datetime.strptime(t, "%Y.%m.%d %H:%M")
        i = idx.get((d - datetime.timedelta(minutes=15 + d.minute % 15)).strftime("%Y-%m-%d %H:%M"))
        f = feat(i) if i is not None else None
        if f: pts.append(f + (pnl,)); tr_out.append([fn[:-4], t] + [round(x, 4) for x in f] + [pnl])
    if len(pts) < 30: continue
    m = [sum(p[k] for p in pts) / len(pts) for k in range(6)]
    ter = []
    for k in (1, 2):   # pnl by accel tercile and jerk tercile
        o = sorted(pts, key=lambda p: p[k]); q = len(o) // 3
        ter += [round(sum(p[6] for p in o[:q])), round(sum(p[6] for p in o[2 * q:]))]
    rows.append([fn[:-4], len(pts)] + [round(x, 3) for x in m] + [round(100 * sum(p[6] > 0 for p in pts) / len(pts), 1), round(sum(p[6] for p in pts))] + ter)
hdr = ["report", "n"] + ["avg_" + x for x in NAMES] + ["win%", "pnl", "pnl_accel_low", "pnl_accel_high", "pnl_jerk_low", "pnl_jerk_high"]
with open(os.path.join(DATA, "slope_map.csv"), "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(hdr); w.writerows(rows)
with open(os.path.join(DATA, "slope_trades.csv"), "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(["report", "open"] + NAMES + ["pnl"]); w.writerows(tr_out)
print(" | ".join(hdr))
for r in rows: print(" | ".join(map(str, r)))
print("\nMarket timeline (mean |value| per year) -> data/slope_timeline.csv")
for y in sorted(yr): print(y, [round(sum(abs(f[k]) for f in yr[y]) / len(yr[y]), 2) for k in range(6)])
