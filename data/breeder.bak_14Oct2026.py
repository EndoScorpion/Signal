"""breeder.py - next-generation builder for the b50/b51/b52 mean-reversion family (test before merge).
1. Parent = best total points (min 100 trades if any) among finished family candidates in loop_state.json.
2. Singles: one-parameter neighbours on a ladder (+-1 step) that were never tested -> queued in extra_candidates.json.
3. Merge: parameter values that individually BEAT the parent (total pts >= parent*1.05 and trades >= 100) are combined (one per parameter)
   into merged children, which are queued and tested; a merge is only kept if it beats its parents.
Run any time: python -I data/breeder.py. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>."""
import json, os, itertools
D = r"C:\Users\endos\Signal\data"; LOT = 0.16
s = json.load(open(os.path.join(D, "loop_state.json"))); T = s["tested"]
ex_path = os.path.join(D, "extra_candidates.json"); extra = json.load(open(ex_path)) if os.path.exists(ex_path) else []
LADD = {"ZTrigger": [1.75, 2.0, 2.25, 2.5, 2.75, 3.0], "ZPeriod": [8, 10, 14, 20, 30], "AtrCapPts": [35, 45, 60, 75, 90, 120], "HoldBars": [24, 32, 48, 64, 96],
        "SLPts": [300, 450, 600, 800, 1000], "RegimePeriod": [1200, 2400, 4800], "CalmRvolMax": [0, 29.6, 45.6]}
def fam(n, t): return "MR_RegimeSwitch" in str(t.get("expert")) or (t.get("patch") or {}).get("_expert", "").startswith("MR_Regime")
def stat(t):
    ys = list(t["oos"]); pts = sum(t["oos"][y]["profit"] for y in ys) / LOT; n = sum(t["oos"][y]["trades"] for y in ys)
    return pts, n, len(ys)
F = {n: t for n, t in T.items() if fam(n, t) and t["of"] >= 6}
if not F: raise SystemExit("no finished family candidates yet")
rank = sorted(F, key=lambda n: -stat(F[n])[0]); big = [n for n in rank if stat(F[n])[1] >= 100] or rank
parent = big[0]; pp = dict(F[parent]["patch"]); pexp = F[parent].get("expert") or pp.get("_expert")
ppts, pn, _ = stat(F[parent])
def sig(p): return json.dumps({k: v for k, v in sorted(p.items())}, sort_keys=True)
seen = {sig(dict(t["patch"], _expert=t.get("expert") or t["patch"].get("_expert"))) for t in T.values()} | {sig(e["patch"]) for e in extra}
gen = s.get("generation", 1) + 1; new = []
base = dict(pp); base["_expert"] = pexp
# singles
for k, lad in LADD.items():
    cur = base.get(k, lad[0] if k != "CalmRvolMax" else 0)
    if cur not in lad: continue
    i = lad.index(cur)
    for j in (i - 1, i + 1):
        if 0 <= j < len(lad):
            c = dict(base); c[k] = lad[j]
            if sig(c) in seen: continue
            seen.add(sig(c)); new.append({"name": f"g{gen}_{k}_{lad[j]}", "why": f"gen{gen} single mutation of {parent}: {k} {cur} -> {lad[j]}", "patch": c})
# merges of single improvements already tested
imp = {}
for n, t in F.items():
    if n == parent: continue
    diff = {k: v for k, v in t["patch"].items() if k != "_expert" and pp.get(k) != v}
    if len(diff) == 1:
        pts, nn, ny = stat(t); k = next(iter(diff))
        if pts >= ppts * 1.05 and nn >= 100 and ny >= 8: imp.setdefault(k, []).append((pts, diff[k], n))
best = {k: max(v) for k, v in imp.items()}
if len(best) >= 2:
    keys = sorted(best, key=lambda k: -best[k][0])
    for r in range(2, min(len(keys), 3) + 1):
        for combo in itertools.combinations(keys, r):
            c = dict(base)
            for k in combo: c[k] = best[k][1]
            if sig(c) in seen: continue
            seen.add(sig(c)); new.append({"name": f"g{gen}_merge_" + "_".join(f"{k}{best[k][1]}" for k in combo), "why": f"gen{gen} merge of tested improvements {combo}", "patch": c})
for x in new: x["name"] = x["name"].replace(".", "p")   # dots in names break MT4 report files
json.dump(new + extra, open(ex_path, "w"), indent=1); s["generation"] = gen
log = os.path.join(D, "generation_log.md")
with open(log, "a") as f:
    f.write(f"\n## Generation {gen}\nParent {parent}: {ppts:+.0f} pts over {stat(F[parent])[2]} yrs, {pn} trades. Single-parameter improvements found so far: " + (", ".join(f"{k}={best[k][1]} ({best[k][0]:+.0f} pts)" for k in best) or "none yet") + f".\nQueued {len(new)} children: " + ", ".join(x['name'] for x in new) + "\n")
print(f"parent {parent} {ppts:+.0f} pts / {pn} trades; improvements: {list(best)}; queued {len(new)} children")
for x in new[:12]: print("  ", x["name"])
