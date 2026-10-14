import json
p = r"C:\Users\endos\Signal\data\loop_state.json"
s = json.load(open(p)); T = s["tested"]; b = s["base"]
bad = {n: T.pop(n) for n in [n for n in list(T) if n.startswith("x_")]}
s.setdefault("invalid_crossovers", {}).update(bad)
json.dump(s, open(p, "w"), indent=1)
print("moved", len(bad), "junk crossovers to invalid_crossovers; candidates now:", len(T))
for n, t in T.items():
    ys = [y for y in t["oos"] if y in b]
    w = sum(1 for y in ys if t["oos"][y]["profit"] > b[y]["profit"]); tot = sum(t["oos"][y]["profit"] for y in ys)
    print(f"{n[:26]:26} yrs {len(ys)} beats {w}/{len(ys)} total {tot:+.0f} | " + " ".join(f"{y[2:]}:{t['oos'][y]['profit']:+.0f}" for y in sorted(ys)))
