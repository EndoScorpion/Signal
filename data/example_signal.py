"""Pull one real example of the regime + z-score fade (sell) from the M15 metrics for the visual. Offline."""
import csv, math, json, datetime
ep, dt, cl, atr = [], [], [], []
for r in csv.DictReader(open(r"C:\Users\endos\Signal\data\m15_metrics.csv")):
    ep.append(int(r["ts"])); dt.append(r["dt"]); cl.append(float(r["close"])); atr.append(float(r["atr14_pts"]))
n = len(cl); P1 = [0.0]; P2 = [0.0]
for c in cl: P1.append(P1[-1] + c); P2.append(P2[-1] + c * c)
def stats(i, N):
    m = (P1[i + 1] - P1[i + 1 - N]) / N; v = (P2[i + 1] - P2[i + 1 - N]) / N - m * m
    return m, math.sqrt(max(v, 0))
best = None
for i in range(4900, n - 120):
    if not dt[i].startswith("2024"): continue
    m, sd = stats(i, 10)
    if sd <= 0: continue
    z = (cl[i] - m) / sd
    reg = (P1[i + 1] - P1[i + 1 - 4800]) / 4800
    if z >= 2.5 and cl[i] < reg and atr[i] < 60 and ep[i + 48] - ep[i] <= 48 * 900 * 1.25 and 18 > int(dt[i][11:13]) > 6:
        pnl = (cl[i] - cl[i + 48]) * 1e5 - 5
        if pnl > 25:
            best = (i, z, pnl, reg); break
i, z, pnl, reg = best
out = {"entry_dt": dt[i], "z": round(z, 2), "pnl_pts": round(pnl, 1), "regime": round(reg, 5), "entry": i - (i - 40),
       "bars": []}
for k in range(i - 40, i + 60):
    m, sd = stats(k, 10)
    out["bars"].append([dt[k][5:16], round(cl[k], 5), round(m, 5), round(m + 2.5 * sd, 5)])
out["entry_idx"] = 40; out["exit_idx"] = 40 + 48
json.dump(out, open(r"C:\Users\endos\Signal\data\example_signal.json", "w"))
print(out["entry_dt"], out["z"], out["pnl_pts"], out["regime"], out["bars"][40], out["bars"][88])
