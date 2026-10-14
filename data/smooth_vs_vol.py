"""smooth_vs_vol.py - tracks market smoothness (Kaufman ER, low = choppy/noisy, high = smooth trend) vs volatility (ATR14 pts)
per year and joins them with each tested candidate's per-year result from loop_state.json.
Output: data/SMOOTH_VS_VOL.md (overwritten each run; derived data only). Run: python -I data/smooth_vs_vol.py
Backtest leads only, never live approval."""
import csv, json, os, math
from collections import defaultdict
D = r"C:\Users\endos\Signal\data"; LOT = 0.16
acc = defaultdict(lambda: [0, 0.0, 0.0, 0.0])  # n, sum er20, sum atr, sum atr^2
with open(os.path.join(D, "m15_metrics.csv")) as f:
    for r in csv.DictReader(f):
        y = r["dt"][:4]; a = acc[y]; er = float(r["er20"]); at = float(r["atr14_pts"])
        a[0] += 1; a[1] += er; a[2] += at; a[3] += at * at
yr = {}
for y, (n, se, sa, sa2) in acc.items():
    m = sa / n; yr[y] = {"er": se / n, "atr": m, "atr_sd": math.sqrt(max(0, sa2 / n - m * m)), "n": n}
s = json.load(open(os.path.join(D, "loop_state.json"))); T = s["tested"]
base = s.get("base_real") or s.get("base") or {}
def pts(v):
    return (v.get("profit", 0) / LOT) if isinstance(v, dict) else (v / LOT)
rows = []
for y in sorted(yr):
    b = base.get(y); rows.append((y, yr[y], pts(b) if b is not None else None))
def corr(xs, ys):
    n = len(xs)
    if n < 3: return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((v - my) ** 2 for v in ys))
    return None if sx == 0 or sy == 0 else sum((x - mx) * (v - my) for x, v in zip(xs, ys)) / (sx * sy)
out = ["# Smoothness vs volatility (auto-generated)", "",
       "ER20 = smoothness (0 choppy, 1 smooth trend). ATR14 = volatility in points. Pts = profit / 0.16 lot.", "",
       "| Year | ER20 | ATR14 pts | ATR sd | Base pts |", "|---|---|---|---|---|"]
for y, d, bp in rows:
    out.append(f"| {y} | {d['er']:.3f} | {d['atr']:.1f} | {d['atr_sd']:.1f} | {'' if bp is None else round(bp)} |")
bx = [(d["er"], d["atr"], bp) for _, d, bp in rows if bp is not None]
if bx:
    out += ["", f"Base vs smoothness corr: {corr([a for a, _, _ in bx], [c for _, _, c in bx])}",
            f"Base vs volatility corr: {corr([b for _, b, _ in bx], [c for _, _, c in bx])}"]
out += ["", "## Candidates (pts per year; corr with smoothness / volatility across tested years)", "",
        "| Candidate | years | total pts | corr ER | corr ATR |", "|---|---|---|---|---|"]
for n, t in T.items():
    o = t.get("oos") or {}
    ys = [y for y in o if y in yr]
    if len(ys) < 3: continue
    p = [pts(o[y]) for y in ys]
    fmt = lambda c: "n/a" if c is None else f"{c:.2f}"
    out.append(f"| {n} | {len(ys)} | {round(sum(p))} | {fmt(corr([yr[y]['er'] for y in ys], p))} | {fmt(corr([yr[y]['atr'] for y in ys], p))} |")
open(os.path.join(D, "SMOOTH_VS_VOL.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out[:16]))
