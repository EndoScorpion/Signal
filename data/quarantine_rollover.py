"""quarantine_rollover.py - candidates whose reports show RollFrom=20 (the b50/b51 default rollover window 20-22, wrong for the clean server clock whose rollover spike is 23-01)
traded through the real rollover window, so their profit is overstated (the leader fell from +18.1k to about +4.1k with the correct window). MOVES (never deletes) their reports to
hst_out/clean/_quarantine_rollover_20_22_14Oct2026/, backs up both state files, moves their entries from `tested` to `tested_rollover_20_22` (kept for the record) and queues corrected
re-tests (rt_<name>, expert b57, correct rollover) for the best ones. Run ONLY while no auto_loop runs. python -E -P data/quarantine_rollover.py"""
import re, glob, os, json, shutil
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; Q = os.path.join(CL, "_quarantine_rollover_20_22_14Oct2026"); os.makedirs(Q, exist_ok=True)
bad = set()
for f in glob.glob(os.path.join(CL, "LOOP_*.htm")) + glob.glob(os.path.join(os.path.dirname(CL), "LOOP_*.htm")):
    h = open(f, encoding="utf-8", errors="ignore").read(6000)
    if re.search(r"RollFrom=(?!23)\d+", h) and "MR_RegimeSwitch" in h:
        m = re.match(r"LOOP_(.+?)_(\d{4})_(real|sp5|sp3_T3p45|sp8)\.htm$", os.path.basename(f))
        if m: bad.add(m.group(1))
moved = 0
for n in bad:
    for f in glob.glob(os.path.join(CL, f"LOOP_{n}_*")) + glob.glob(os.path.join(os.path.dirname(CL), f"LOOP_{n}_*")):
        shutil.move(f, os.path.join(Q, os.path.basename(f))); moved += 1
ex_path = os.path.join(D, "extra_candidates.json"); ex = json.load(open(ex_path)); names = {e["name"] for e in ex}; retests = []
removed = {}
for sp in ("loop_state.json", "loop_state_clean.json"):
    p = os.path.join(D, sp); shutil.copy(p, p + ".bak_14Oct2026_rollover"); s = json.load(open(p)); T = s["tested"]; old = s.setdefault("tested_rollover_20_22", {})
    for n in list(T):
        if n in bad: old[n] = T.pop(n); removed[n] = old[n]
    json.dump(s, open(p, "w"), indent=1)
def pts(t): return sum(v["profit"] for v in (t.get("oos") or {}).values()) / 0.16
for n, t in sorted(removed.items(), key=lambda kv: -pts(kv[1]))[:14]:
    if not t.get("oos") or f"rt_{n}"[:90] in names: continue
    patch = {k: v for k, v in t["patch"].items() if k != "_expert"}; patch["_expert"] = "MR_RegimeSwitch_b57"; patch.pop("RollFrom", None); patch.pop("RollTo", None)
    retests.append({"name": f"rt_{n}"[:90], "why": f"corrected re-test of {n} (was +{pts(t):.0f} pts with rollover window 20-22; now with the correct 23-01 window on b57)", "patch": patch})
json.dump(retests + ex, open(ex_path, "w"), indent=1)
open(os.path.join(Q, "README.txt"), "w").write("Reports of candidates that ran with RollFrom=20 RollTo=22 (wrong rollover window for the clean clock). Results overstated; kept for the record.\nNames: " + ", ".join(sorted(bad)) + "\n")
print(f"quarantined {len(bad)} candidates ({moved} files); queued {len(retests)} corrected re-tests at the FRONT of the queue")
