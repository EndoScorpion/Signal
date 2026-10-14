"""pts_report.py - express loop results in POINTS (net after the test's spread/commission), independent of balance.
All tests use fixed 0.16-lot sizing (UseLotSim with a fixed SimDeposit for the b31 family, Lots=0.16 for b50/b51), so 1 point = $0.16 and pts = profit / 0.16.
Run: python -I data/pts_report.py [regex of candidate names]"""
import os, re, sys, time, importlib.util
H = r"C:\Users\endos\Desktop\hst_out"; LOT = 0.16
spec = importlib.util.spec_from_file_location("pr", r"C:\Users\endos\Signal\data\parse_results.py"); pr = importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
want = re.compile(sys.argv[1]) if len(sys.argv) > 1 else re.compile(r"^(WIN_GEN1|u_regime_2400|k_hurst_trend|b5_sell_z25_n10|m5_|z_B36_adx|l_dailydd)")
YRS = ["2010", "2013", "2014", "2015", "2016", "2018", "2023", "2024"]
data = {}
for f in os.listdir(H):
    m = re.match(r"(?:LOOP_(.+)|(WIN_GEN1))_(\d{4})_(sp5)\.htm$", f)
    if not m: continue
    name = m.group(1) or "BASE (WIN_GEN1)"; y = m.group(3)
    if not want.search(name) and not (name.startswith("BASE")): continue
    r = pr.parse_report(os.path.join(H, f)); data.setdefault(name, {})[y] = (float(r["profit"]) / LOT, int(r["trades"]))
def line(name, d):
    ys = [y for y in YRS if y in d]; tot = sum(d[y][0] for y in ys); n = sum(d[y][1] for y in ys)
    cells = " ".join(f"{y[2:]}:{d[y][0]:+.0f}" for y in YRS if y in d)
    return f"{name[:26]:26} yrs {len(ys)} | trades {n:5d} | total {tot:+8.0f} pts | per trade {tot/max(n,1):+6.1f} pts | {cells}"
print("net points after cost (sp5), per year; pts = $ / 0.16")
for name in sorted(data, key=lambda k: (not k.startswith("BASE"), -sum(v[0] for v in data[k].values()) / max(len(data[k]), 1))):
    if len(data[name]) >= 4 or name.startswith("BASE"): print(line(name, data[name]))
