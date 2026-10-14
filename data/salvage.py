"""salvage.py - Nasif's rule (2026-10-14): only drop logic if it cannot be improved, cannot serve as loss prevention/protection, and cannot improve other logic.
For every finished candidate that did NOT beat the current leader (a 'loser'), each of its changed inputs (a 'gene') is SALVAGED instead of dropped:
  1. INVERT   flip mode inputs (1<->2) so the gate protects the opposite state;
  2. TUNE     scale numeric thresholds x0.8 and x1.25 (the gate may be right with another strictness);
  3. PROTECT  apply the gene to the leader together with the leader's best known winning gene (use it to improve other logic / as protection);
  Everything is queued as new candidates (s_*) in data/extra_candidates.json (add only, backup kept).
A gene is RETIRED (recorded, never deleted: reports, sets and EA code stay) only after >= 3 salvage variants were tested and none beat the leader.
Registry: data/logic_registry.json and data/LOGIC_REGISTRY.md. Run: python -E -P data/salvage.py [--max 6]. Backtest leads only, never live approval."""
import json, os, re, shutil, sys, datetime
D = r"C:\Users\endos\Signal\data"; LOT = 0.16
MAXC = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 6
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
def exp(t): return t.get("expert") or (t.get("patch") or {}).get("_expert") or ""
def ver(e): m = re.search(r"b(\d+)$", str(e)); return int(m.group(1)) if m else 0
def pts(t, ys=None): o = t.get("oos") or {}; ys = ys or list(o); return sum(o[y]["profit"] for y in ys if y in o) / LOT, sum(o[y]["trades"] for y in ys if y in o)
F = {n: t for n, t in T.items() if "MR_RegimeSwitch" in exp(t) and (t.get("oos") or {})}
big = [n for n in F if pts(F[n])[1] >= 100 and len(F[n]["oos"]) >= 6]
if not big: raise SystemExit("no leader yet")
leader = max(big, key=lambda n: pts(F[n])[0]); lp = {k: v for k, v in F[leader]["patch"].items() if k != "_expert"}; lexp = exp(F[leader])
MODE = {"SlopeGapMode", "SlopeStackMode", "SsrMode", "AlligatorMode", "AdMode", "WprMode", "FractalMode", "FibMode", "StochMode", "CciMode", "EntryMode", "AccelMode", "SideMode"}
reg_path = os.path.join(D, "logic_registry.json"); reg = json.load(open(reg_path)) if os.path.exists(reg_path) else {}
ex_path = os.path.join(D, "extra_candidates.json"); ex = json.load(open(ex_path))
def sig(p): return json.dumps({k: v for k, v in sorted(p.items())}, sort_keys=True)
seen = {sig(e["patch"]) for e in ex} | {sig(dict(t["patch"], _expert=exp(t))) for t in T.values()}
winners = []   # best non-leader genes that beat the leader (to pair with salvaged ones)
for n, t in F.items():
    if n == leader: continue
    com = [y for y in t["oos"] if y in F[leader]["oos"]]
    if len(com) < 4: continue
    d = pts(t, com)[0] - pts(F[leader], com)[0]; diff = {k: v for k, v in t["patch"].items() if k != "_expert" and lp.get(k) != v}
    if d > 0 and diff: winners.append((d, diff, ver(exp(t))))
winners.sort(key=lambda w: -w[0]); bestw = winners[0] if winners else None
new = []
def add(name, why, patch, v):
    p = dict(patch); p["_expert"] = f"MR_RegimeSwitch_b{max(v, ver(lexp))}"
    if sig(p) in seen or len(new) >= MAXC: return False
    seen.add(sig(p)); new.append({"name": re.sub(r"[^A-Za-z0-9_]", "p", name)[:90], "why": why, "patch": p}); return True
for n, t in sorted(F.items()):
    if n == leader or n.startswith("s_"): continue
    com = [y for y in t["oos"] if y in F[leader]["oos"]]
    if len(com) < 4: continue
    if pts(t, com)[0] - pts(F[leader], com)[0] > 0: continue
    diff = {k: v for k, v in t["patch"].items() if k != "_expert" and lp.get(k) != v}
    if not diff or len(diff) > 3: continue
    gk = "+".join(f"{k}={v}" for k, v in sorted(diff.items())); r = reg.setdefault(gk, {"status": "salvaging", "from": n, "variants": []})
    if r["status"] == "retired": continue
    v0 = ver(exp(t)); base = dict(lp)
    for k, v in diff.items():          # 1 INVERT
        if k in MODE and str(v) in ("1", "2"):
            p = dict(base); p.update(diff); p[k] = 2 if str(v) == "1" else 1
            if add(f"s_{n}_inv", f"salvage {gk} of {n}: inverted mode (protects the opposite state)", p, v0): r["variants"].append(f"s_{n}_inv")
    for k, v in diff.items():          # 2 TUNE
        if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in MODE:
            for f, tag in ((0.8, "x08"), (1.25, "x125")):
                p = dict(base); p.update(diff); p[k] = int(round(v * f)) if isinstance(v, int) else round(v * f, 3)
                if add(f"s_{n}_{k}_{tag}", f"salvage {gk} of {n}: {k} {v} -> {p[k]}", p, v0): r["variants"].append(f"s_{n}_{k}_{tag}")
    if bestw:                          # 3 PROTECT / improve other logic
        p = dict(base); p.update(bestw[1]); p.update(diff)
        if add(f"s_{n}_with_winner", f"salvage {gk} of {n}: combined with the best winning gene {bestw[1]} to improve other logic / protect it", p, max(v0, bestw[2])): r["variants"].append(f"s_{n}_with_winner")
# retire only after >= 3 salvage variants were tested and none beat the leader
for gk, r in reg.items():
    done = [T[v] for v in r["variants"] if v in T]
    if r["status"] == "salvaging" and len(done) >= 3 and all(pts(t, [y for y in t["oos"] if y in F[leader]["oos"]])[0] <= pts(F[leader], [y for y in t["oos"] if y in F[leader]["oos"]])[0] for t in done if t.get("oos")):
        r["status"] = "retired"; r["retired_on"] = datetime.date.today().isoformat(); r["reason"] = f"{len(done)} salvage variants tested, none beat {leader}; reports, sets and EA code kept"
if new: shutil.copy(ex_path, ex_path + ".bak5_14Oct2026"); json.dump(ex + new, open(ex_path, "w"), indent=1)
json.dump(reg, open(reg_path, "w"), indent=1)
open(os.path.join(D, "LOGIC_REGISTRY.md"), "w", encoding="utf-8").write("# Logic registry (salvage rule)\n\nLeader: " + leader + f" {pts(F[leader])[0]:+.0f} pts\n\n| gene | status | from | variants queued/tested |\n|---|---|---|---|\n" + "\n".join(f"| {k} | {v['status']} | {v['from']} | {len(v['variants'])} |" for k, v in reg.items()) + "\n")
print(f"leader {leader}; genes tracked {len(reg)} ({sum(1 for v in reg.values() if v['status']=='retired')} retired); queued {len(new)} salvage candidates: {[x['name'] for x in new]}")
