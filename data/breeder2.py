"""breeder2.py - deconstruct + mix-and-match breeder (Nasif 2026-10-14: next-gen clones may deconstruct and recombine win logic).
1. DECONSTRUCT: every finished candidate (loop_state.json + loop_state_clean.json) is diffed against the parent patch (best MR-family result with >=100 trades);
   each changed input = a gene. A gene WINS when its candidate beats the parent on the common years (delta pts > 0, >=4 common years, >=60 trades).
2. MIX: combine 2-3 non-conflicting winning genes (and the best whole-parent crossovers) into new children; the child's expert is the highest MR_RegimeSwitch version any gene needs.
3. MUTATE: +-20% on one numeric input of the best parent at a time (max 4).
Only ADDS entries to data/extra_candidates.json (backup kept) and appends data/generation_log.md. Never touches ancestors, sets or results.
Run: python -I data/breeder2.py [--max 8]. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>. Backtest only, never live approval."""
import json, os, re, itertools, shutil, sys, datetime
D = r"C:\Users\endos\Signal\data"; LOT = 0.16
MAXC = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 8
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"])
cp = os.path.join(D, "loop_state_clean.json")
if os.path.exists(cp): T.update(json.load(open(cp)).get("tested", {}))
ex_path = os.path.join(D, "extra_candidates.json"); extra = json.load(open(ex_path)) if os.path.exists(ex_path) else []
def ver(e): m = re.search(r"b(\d+)$", str(e or "")); return int(m.group(1)) if m else 0
def exp(t): return t.get("expert") or (t.get("patch") or {}).get("_expert") or ""
def fam(t): return "MR_RegimeSwitch" in exp(t)
def pts(t, ys=None):
    o = t.get("oos") or {}; ys = ys or list(o); return sum(o[y]["profit"] for y in ys if y in o) / LOT, sum(o[y]["trades"] for y in ys if y in o)
F = {n: t for n, t in T.items() if fam(t) and (t.get("oos") or {})}
if not F: raise SystemExit("no finished MR-family candidates yet")
big = [n for n in F if pts(F[n])[1] >= 100 and len(F[n]["oos"]) >= 6] or list(F)
parent = max(big, key=lambda n: pts(F[n])[0]); pp = {k: v for k, v in F[parent]["patch"].items() if k != "_expert"}; pexp = exp(F[parent])
def sig(p): return json.dumps({k: v for k, v in sorted(p.items())}, sort_keys=True)
seen = {sig(dict(t["patch"], _expert=exp(t))) for t in T.values()} | {sig(e["patch"]) for e in extra}
genes = {}   # (key, value) -> (delta pts, trades, years, expert version, source)
for n, t in F.items():
    if n == parent: continue
    common = [y for y in t["oos"] if y in F[parent]["oos"]]
    if len(common) < 4: continue
    c, ct = pts(t, common); p0, _ = pts(F[parent], common)
    if ct < 60 or c - p0 <= 0: continue
    diff = {k: v for k, v in t["patch"].items() if k != "_expert" and pp.get(k) != v}
    if not diff or len(diff) > 3: continue
    for k, v in diff.items():
        g = (k, json.dumps(v)); d = (c - p0) / len(diff)
        if g not in genes or d > genes[g][0]: genes[g] = (d, ct, len(common), ver(exp(t)), n)
win = sorted(genes.items(), key=lambda kv: -kv[1][0])[:8]
gen = (json.load(open(os.path.join(D, "loop_state.json"))).get("generation", 1)) + 2
new = []
def add(name, why, patch, v):
    p = dict(patch); p["_expert"] = f"MR_RegimeSwitch_b{max(v, ver(pexp))}"
    if sig(p) in seen or len(new) >= MAXC: return
    seen.add(sig(p)); new.append({"name": name.replace(".", "p"), "why": why, "patch": p})
for r in (2, 3):
    for combo in itertools.combinations(win, r):
        ks = [g[0][0] for g in combo]
        if len(set(ks)) < len(ks): continue
        p = dict(pp)
        for (k, v), meta in combo: p[k] = json.loads(v)
        add("x" + str(gen) + "_mix_" + "_".join(f"{k}{json.loads(v)}" for (k, v), _ in combo)[:80], f"mix of winning genes {[(k, json.loads(v)) for (k, v), _ in combo]} on parent {parent}", p, max(m[3] for _, m in combo))
others = sorted([n for n in big if n != parent], key=lambda n: -pts(F[n])[0])[:1]
for o in others:   # whole-parent crossover: midpoints of numeric inputs with the second best
    q = {k: v for k, v in F[o]["patch"].items() if k != "_expert"}; p = dict(pp)
    for k in pp:
        if k in q and isinstance(pp[k], (int, float)) and isinstance(q[k], (int, float)) and not isinstance(pp[k], bool):
            m = (pp[k] + q[k]) / 2; p[k] = int(round(m)) if isinstance(pp[k], int) and isinstance(q[k], int) else round(m, 3)
    add(f"x{gen}_cross_{parent}_{o}"[:90], f"crossover midpoints of {parent} and {o}", p, ver(exp(F[o])))
for k, v in pp.items():
    if len(new) >= MAXC + 4: break
    if isinstance(v, bool) or not isinstance(v, (int, float)) or k in ("SideMode", "MagicNumber"): continue
    for f in (0.8, 1.2):
        nv = int(round(v * f)) if isinstance(v, int) else round(v * f, 3); p = dict(pp); p[k] = nv
        if len([x for x in new if x["name"].startswith(f"x{gen}_mut")]) >= 4: break
        add(f"x{gen}_mut_{k}_{nv}", f"mutation {k} {v} -> {nv} on parent {parent}", p, 0)
shutil.copy(ex_path, os.path.join(D, "extra_candidates.bak3_14Oct2026.json"))
json.dump(extra + new, open(ex_path, "w"), indent=1)
with open(os.path.join(D, "generation_log.md"), "a") as f:
    f.write(f"\n## breeder2 {datetime.datetime.now():%Y-%m-%d %H:%M} (gen {gen})\nParent {parent}: {pts(F[parent])[0]:+.0f} pts / {pts(F[parent])[1]} trades. Winning genes: {[(g[0], json.loads(g[1]), round(m[0])) for g, m in win]}. Queued {len(new)} children: {[x['name'] for x in new]}\n")
print(f"parent {parent}; winning genes {len(win)}; queued {len(new)} children"); [print("  ", x["name"]) for x in new]
