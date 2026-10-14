"""pts_projection.py - scale tested point results to account balances (linear, same % risk per trade).
Test basis: $10,000 sim deposit, 0.16 lot (1 pt = $0.16), SL 600 pts => ~0.96% of balance risked per trade at the stop.
Lot for balance B = 0.16 * B / 10000. Dollars = points * lot. No compounding. Backtest arithmetic, not a forecast or advice."""
import os, re, importlib.util
H = r"C:\Users\endos\Desktop\hst_out"; LOT = 0.16
spec = importlib.util.spec_from_file_location("pr", r"C:\Users\endos\Signal\data\parse_results.py"); pr = importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
def load(name, kind):
    out = {}
    for y in ("2010", "2013", "2014", "2015", "2016", "2018", "2023", "2024"):
        p = os.path.join(H, f"LOOP_{name}_{y}_{kind}.htm")
        if os.path.exists(p):
            r = pr.parse_report(p); out[y] = (float(r["profit"]) / LOT, int(r["trades"]), float(r["dd_pct"]) / 100 * 10000 / LOT)
    return out
sets = {"m5_sell_atr60 (sp5)": load("m5_sell_atr60", "sp5"), "m5_sell_atr60 (realistic cost)": load("m5_sell_atr60", "real"), "b5_sell_z25_n10 (sp5)": load("b5_sell_z25_n10", "sp5")}
stats = {}
for k, d in sets.items():
    if len(d) < 8: print("incomplete:", k, sorted(d)); continue
    tot = sum(v[0] for v in d.values()); n = sum(v[1] for v in d.values())
    stats[k] = dict(avg=tot / 8, best=max(v[0] for v in d.values()), worst=min(v[0] for v in d.values()), dd=max(v[2] for v in d.values()), trades=n, tot=tot)
    print(f"{k}: total {tot:+.0f} pts over 8 yrs, {n} trades, avg {tot/8:+.0f} pts/yr, best yr {stats[k]['best']:+.0f}, worst yr {stats[k]['worst']:+.0f}, deepest in-year drawdown {stats[k]['dd']:.0f} pts")
print()
print("| Balance | Lot | " + " | ".join(f"{k}: avg/yr, worst yr, deepest DD" for k in stats) + " |")
for B in range(5000, 50001, 5000):
    lot = LOT * B / 10000; cells = []
    for k, s in stats.items():
        cells.append(f"${s['avg']*lot:,.0f} ({s['avg']*lot/B*100:.1f}%), ${s['worst']*lot:,.0f}, ${s['dd']*lot:,.0f}")
    print(f"| ${B:,} | {lot:.2f} | " + " | ".join(cells) + " |")
