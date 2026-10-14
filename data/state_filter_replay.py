"""state_filter_replay.py - does convergence state + volatility/range/volume explain EA entry quality? Offline replay.
Per OOS year (base WIN_GEN1 sp5 reports): avg pnl/trade by (a) convergence state, (b) ATR14 tercile, (c) 20-bar close range tercile,
(d) volume-vs-20bar tercile, and the net pnl if only 'diverged/diverging' entries were kept. Consistency across years matters more than totals.
Caveat: removing trades offline ignores ladder/hedge interactions; treat as a lead to confirm in the MT4 tester. Concepts (c) Nasif Hossain."""
import os, csv, math, datetime, importlib.util
DATA = r"C:\Users\endos\Signal\data"; HST = r"C:\Users\endos\Desktop\hst_out"
spec = importlib.util.spec_from_file_location("al", os.path.join(DATA, "auto_loop.py"))
al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
dt, cl, ab, atr, vol = [], [], [], [], []
for r in csv.DictReader(open(os.path.join(DATA, "m15_metrics.csv"))):
    dt.append(r["dt"]); cl.append(float(r["close"])); ab.append(float(r["close_above_sma20_pts"]))
    atr.append(float(r["atr14_pts"])); vol.append(float(r["vol_rel20"]))
n = len(cl); idx = {d: i for i, d in enumerate(dt)}
sma = [cl[i] - ab[i] * 1e-5 for i in range(n)]
F = [None] * n
for i in range(8, n): F[i] = (sma[i] - sma[i - 8]) / 8 * 1e5
cs = [0.0]
for c in cl: cs.append(cs[-1] + c)
W = 4800
R = [None] * n
for i in range(W - 1, n): R[i] = (cs[i + 1] - cs[i + 1 - W]) / W
def slow(i): return (R[i] - R[i - 96]) * 1e5 / 96
def rng(i): w = cl[i - 19:i + 1]; return (max(w) - min(w)) * 1e5
def terc(vals):
    s = sorted(vals); return s[len(s) // 3], s[2 * len(s) // 3]
sample = range(W + 200, n, 7)
cuts = {"atr": terc([atr[i] for i in sample]), "rng": terc([rng(i) for i in sample]), "vol": terc([vol[i] for i in sample])}
def tb(v, c): return "low" if v <= c[0] else "mid" if v <= c[1] else "high"
data = {}
for y in ("2015", "2018", "2023", "2024"):
    p = os.path.join(HST, f"WIN_GEN1_{y}_sp5.htm")
    if not os.path.exists(p): continue
    for t, pnl in al.trades_from_report(p):
        d = datetime.datetime.strptime(t, "%Y.%m.%d %H:%M")
        i = idx.get((d - datetime.timedelta(minutes=15 + d.minute % 15)).strftime("%Y-%m-%d %H:%M"))
        if i is None or i < W + 110 or F[i - 8] is None: continue
        a = (F[i] > 0) == (slow(i) > 0); cv = abs(F[i] - slow(i)) < abs(F[i - 8] - slow(i - 8))
        st = ("aligned" if a else "diverged") + "/" + ("converging" if cv else "diverging")
        data.setdefault(y, []).append((st, tb(atr[i], cuts["atr"]), tb(rng(i), cuts["rng"]), tb(vol[i], cuts["vol"]), pnl))
def table(title, k):
    keys = sorted({r[k] for ys in data.values() for r in ys})
    print(f"\n{title} (avg pnl/trade [n]) per year")
    print("bucket".ljust(24), *[y.rjust(14) for y in sorted(data)])
    for key in keys:
        cells = []
        for y in sorted(data):
            rr = [r[4] for r in data[y] if r[k] == key]
            cells.append((f"{sum(rr)/len(rr):+.1f} [{len(rr)}]" if rr else "-").rjust(14))
        print(key.ljust(24), *cells)
table("Convergence state", 0); table("ATR14 volatility", 1); table("20-bar range", 2); table("Volume vs 20-bar avg", 3)
print("\nNet pnl per year: all entries vs only diverged/diverging")
for y in sorted(data):
    allp = sum(r[4] for r in data[y]); keep = [r[4] for r in data[y] if r[0] == "diverged/diverging"]
    print(y, f"all {allp:+.0f} ({len(data[y])})  kept {sum(keep):+.0f} ({len(keep)})")
