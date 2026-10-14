"""convergence_map.py - curve alignment, fast/slow slope convergence-divergence, slope std-dev z-scores.
fast = SMA20 8-bar slope; slow = regime SMA(4800 M15 ~ H1 1200) 96-bar slope, both in pts per M15 bar.
aligned = same sign. converging = |fast-slow| smaller than 8 bars ago. z = fast slope / rolling std (1200 bars).
Outputs: convergence_timeline.csv (per year), prints correlations and EA pnl by state. Offline, no MT4.
Slope/MMR concepts (c) Nasif Hossain."""
import os, csv, re, math, datetime, importlib.util
DATA = r"C:\Users\endos\Signal\data"; HST = r"C:\Users\endos\Desktop\hst_out"
spec = importlib.util.spec_from_file_location("al", os.path.join(DATA, "auto_loop.py"))
al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
dt, cl, ab = [], [], []
for r in csv.DictReader(open(os.path.join(DATA, "m15_metrics.csv"))):
    dt.append(r["dt"]); cl.append(float(r["close"])); ab.append(float(r["close_above_sma20_pts"]))
n = len(cl); idx = {d: i for i, d in enumerate(dt)}
sma = [cl[i] - ab[i] * 1e-5 for i in range(n)]
F = [None] * n
for i in range(8, n): F[i] = (sma[i] - sma[i - 8]) / 8 * 1e5
cs = [0.0]
for c in cl: cs.append(cs[-1] + c)
W = 4800
R = [None] * n
for i in range(W - 1, n): R[i] = (cs[i + 1] - cs[i + 1 - W]) / W
Sl = [None] * n
for i in range(W + 95, n): Sl[i] = (R[i] - R[i - 96]) * 1e5 / 96
P1 = [0.0]; P2 = [0.0]
for v in F: x = v or 0.0; P1.append(P1[-1] + x); P2.append(P2[-1] + x * x)
def zs(i):
    if i < 1300: return None
    a, b = i - 1200 + 1, i + 1
    m = (P1[b] - P1[a]) / 1200; var = (P2[b] - P2[a]) / 1200 - m * m
    return F[i] / math.sqrt(var) if var > 0 else None
def state(i):
    if i < W + 110 or F[i] is None or F[i - 8] is None or Sl[i] is None or Sl[i - 8] is None: return None
    al_ = (F[i] > 0) == (Sl[i] > 0)
    cv = abs(F[i] - Sl[i]) < abs(F[i - 8] - Sl[i - 8])
    return al_, cv, zs(i)
yr = {}
for i in range(W + 200, n, 4):
    s = state(i)
    if s and s[2] is not None:
        y = yr.setdefault(dt[i][:4], [0, 0, 0, 0.0, 0.0, 0.0]); y[0] += 1; y[1] += s[0]; y[2] += s[1]
        y[3] += abs(s[2]); y[4] += abs(F[i]); y[5] += abs(Sl[i]) * 1e0
years = sorted(yr)
rows = [[y, round(100 * yr[y][1] / yr[y][0], 1), round(100 * yr[y][2] / yr[y][0], 1), round(yr[y][3] / yr[y][0], 2),
         round(yr[y][4] / yr[y][0], 2), round(yr[y][5] / yr[y][0], 3)] for y in years]
with open(os.path.join(DATA, "convergence_timeline.csv"), "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(["year", "pct_aligned", "pct_converging", "mean_abs_z", "mean_abs_fast", "mean_abs_slow"]); w.writerows(rows)
print("year pct_aligned pct_converging mean|z| |fast| |slow|")
for r in rows: print(*r)
def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
cols = list(zip(*rows))[1:]; nm = ["aligned", "converging", "|z|", "|fast|", "|slow|"]
print("\nCurve correlations across years:")
for i in range(5):
    print(nm[i].ljust(11), " ".join(f"{corr(cols[i], cols[j]):+.2f}" for j in range(5)))
# EA pnl by state
st = {}
for fn in sorted(os.listdir(HST)):
    if not re.search(r"^WIN_GEN1_.*sp5\.htm$", fn): continue
    for t, pnl in al.trades_from_report(os.path.join(HST, fn)):
        d = datetime.datetime.strptime(t, "%Y.%m.%d %H:%M")
        i = idx.get((d - datetime.timedelta(minutes=15 + d.minute % 15)).strftime("%Y-%m-%d %H:%M"))
        s = state(i) if i is not None else None
        if not s or s[2] is None: continue
        k = ("aligned" if s[0] else "diverged") + "/" + ("converging" if s[1] else "diverging")
        z = abs(s[2]); kz = "|z|<1" if z < 1 else "1-2" if z < 2 else ">2"
        for key in (k, "z " + kz):
            a = st.setdefault(key, [0, 0, 0.0]); a[0] += 1; a[1] += pnl > 0; a[2] += pnl
print("\nBase WIN_GEN1 entries (2015,2018,2023,2024 sp5) by state: n, win%, avg pnl/trade")
for k in sorted(st): print(k.ljust(26), st[k][0], f"{100*st[k][1]/st[k][0]:.1f}%", f"{st[k][2]/st[k][0]:+.2f}")
