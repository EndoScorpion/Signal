import json
s = json.load(open(r"C:\Users\endos\Signal\data\loop_state.json")); b = s["base"]; T = s["tested"]
yrs = sorted(b); print("base per year:", {y: round(b[y]["profit"]) for y in yrs}, "| base trades:", {y: b[y]["trades"] for y in yrs})
print(f"\ncandidates tested: {len(T)} | years each (early-abort drops weak ones after 1 year)")
rows = []
for n, t in T.items():
    o = t["oos"]; real = [y for y in o if y in b and o[y]["trades"] >= 100]
    if not real: rows.append((-1e9, n, t, [], 0, 0)); continue
    d = sum(o[y]["profit"] - b[y]["profit"] for y in real) / len(real)
    rows.append((d, n, t, real, sum(1 for y in real if o[y]["profit"] > 0), sum(1 for y in real if o[y]["profit"] > b[y]["profit"])))
rows.sort(key=lambda r: -r[0])
print("name | yrs(>=100 trades) | beats base | profitable yrs | avg improvement $/yr vs base | abs avg $/yr | audit(real cost)")
for d, n, t, real, prof, beat in rows[:14]:
    o = t["oos"]; ab = sum(o[y]["profit"] for y in real) / len(real) if real else 0
    au = t.get("real"); aus = f"{au['beats']}/{len(au['profit'])}" if au else "-"
    print(f"{n[:24]:24} | {len(real)}/{len(o)} | {beat}/{len(real)} | {prof}/{len(real)} | {d:+8.0f} | {ab:+8.0f} | {aus}")
print("\nfailed screens (lost to base on the first year):", sum(1 for t in T.values() if t['of'] == 1), "of", len(T))
print("promoted:", [n for n, t in T.items() if t.get("promoted")])
print("diversity:", s.get("diversity"))
