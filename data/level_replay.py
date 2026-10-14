"""level_replay.py - stochastic, support/resistance, Fibonacci position, psychological levels, news-day proxy vs EA entry pnl.
Per OOS year, avg pnl/trade [n]. Offline replay of base WIN_GEN1 sp5 reports. Look for the SAME sign in all 4 years.
S/R = lowest/highest M15 close over last 192 bars (2 days). Fib = where close sits in the 480-bar (5-day) range (0=low, 1=high).
Psych = distance to nearest 0.0050 level. News proxy = US NFP day (first Friday) only; real calendars/events need a data download."""
import os, csv, datetime, importlib.util
DATA = r"C:\Users\endos\Signal\data"; HST = r"C:\Users\endos\Desktop\hst_out"
spec = importlib.util.spec_from_file_location("al", os.path.join(DATA, "auto_loop.py"))
al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
dt, cl, k14 = [], [], []
for r in csv.DictReader(open(os.path.join(DATA, "m15_metrics.csv"))):
    dt.append(r["dt"]); cl.append(float(r["close"])); k14.append(float(r["stoch_k14"]))
idx = {d: i for i, d in enumerate(dt)}
def feats(i, d):
    c = cl[i]; w2 = cl[i - 191:i + 1]; w5 = cl[i - 479:i + 1]
    dlo, dhi = (c - min(w2)) * 1e5, (max(w2) - c) * 1e5
    f = (c - min(w5)) / max(max(w5) - min(w5), 1e-9)
    psy = abs(((c * 1e5 + 250) % 500) - 250)
    nfp = d.weekday() == 4 and d.day <= 7
    return {"stoch": "k<20" if k14[i] < 20 else "k>80" if k14[i] > 80 else "k20-80",
            "dist to 2d low": "<15" if dlo < 15 else "15-60" if dlo < 60 else ">60",
            "dist to 2d high": "<15" if dhi < 15 else "15-60" if dhi < 60 else ">60",
            "fib pos(5d)": "<0.382" if f < .382 else "0.382-0.618" if f < .618 else ">0.618",
            "psych 0.0050": "<15pts" if psy < 15 else "15-60" if psy < 60 else ">60",
            "NFP day": "NFP" if nfp else "other"}
data = {}
for y in ("2015", "2018", "2023", "2024"):
    p = os.path.join(HST, f"WIN_GEN1_{y}_sp5.htm")
    if not os.path.exists(p): continue
    for t, pnl in al.trades_from_report(p):
        d = datetime.datetime.strptime(t, "%Y.%m.%d %H:%M")
        i = idx.get((d - datetime.timedelta(minutes=15 + d.minute % 15)).strftime("%Y-%m-%d %H:%M"))
        if i is None or i < 500: continue
        data.setdefault(y, []).append((feats(i, d), pnl))
ys = sorted(data)
for name in next(iter(data.values()))[0][0]:
    print(f"\n{name}".ljust(26), *[y.rjust(14) for y in ys])
    for b in sorted({r[0][name] for v in data.values() for r in v}):
        cells = []
        for y in ys:
            rr = [r[1] for r in data[y] if r[0][name] == b]
            cells.append((f"{sum(rr)/len(rr):+.1f} [{len(rr)}]" if rr else "-").rjust(14))
        print(("  " + b).ljust(24), *cells)
