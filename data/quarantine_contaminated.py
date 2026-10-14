import json, os, re, shutil
H = r"C:\Users\endos\Desktop\hst_out"; Q = os.path.join(H, "quarantine_contaminated"); os.makedirs(Q, exist_ok=True)
moved = []
for f in os.listdir(H):
    if re.match(r"LOOP_(g2_.+|m5_sell_calm)_\d{4}_(sp5|real)\.(htm|gif)$", f):
        shutil.move(os.path.join(H, f), os.path.join(Q, f)); moved.append(f)
p = r"C:\Users\endos\Signal\data\loop_state.json"; s = json.load(open(p)); T = s["tested"]
c = s.setdefault("contaminated_inherited_inputs", {})
for n in [n for n in list(T) if n == "m5_sell_calm" or n.startswith("g2_")]:
    c[n] = T.pop(n)
json.dump(s, open(p, "w"), indent=1)
print(f"moved {len(moved)} report files to quarantine_contaminated; state entries moved: {list(c)}; candidates now: {list(T)}")
with open(r"C:\Users\endos\Signal\data\generation_log.md", "a") as f:
    f.write("\n## Contamination note (2026-10-13 ~00:05)\nMT4's tester reuses the last value of any input missing from a .set. b51 candidates after m5_sell_atr60 inherited leftovers (m5_sell_calm ran with AtrCapPts=60 plus its calm gate; g2_* ran with CalmRvolMax=29.6/CalmPEMax=0.9452). Their reports were moved to hst_out\\quarantine_contaminated and they will re-run. auto_loop.build_set now lists every EA input with source defaults. Clean results: m5_sell_atr60 (first b51 run), b5_sell_z25_n10 (b50), and all b31-family candidates (the base set lists all inputs).\n")
