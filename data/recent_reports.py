import os, re, time, importlib.util
H = r"C:\Users\endos\Desktop\hst_out"
spec = importlib.util.spec_from_file_location("pr", r"C:\Users\endos\Signal\data\parse_results.py"); pr = importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
base = {}
for y in ("2010", "2013", "2014", "2015", "2016", "2018", "2023", "2024"):
    p = os.path.join(H, f"WIN_GEN1_{y}_sp5.htm")
    if os.path.exists(p): base[y] = float(pr.parse_report(p)["profit"])
cut = time.time() - 4 * 3600
rows = {}
for f in os.listdir(H):
    m = re.match(r"LOOP_(.+)_(\d{4})_(sp5|real)\.htm$", f)
    if m and os.path.getmtime(os.path.join(H, f)) >= cut:
        r = pr.parse_report(os.path.join(H, f)); rows.setdefault((m.group(1), m.group(3)), {})[m.group(2)] = (float(r["profit"]), int(r["trades"]), float(r["pf"]))
print("base sp5:", {y: round(v) for y, v in base.items()})
for (name, kind), ys in sorted(rows.items()):
    if kind != "sp5": continue
    wins = [y for y in ys if y in base and ys[y][0] > base[y]]
    print(f"{name[:26]:26} {len(ys)} yrs beats {len(wins)}/{len(ys)} | " + " ".join(f"{y}:{ys[y][0]:+.0f}({ys[y][1]}tr)" for y in sorted(ys)))
print("realistic-cost passes:", {k[0]: {y: round(v[0]) for y, v in ys.items()} for k, ys in rows.items() if k[1] == "real"})
