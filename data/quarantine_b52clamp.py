"""quarantine_b52clamp.py - moves (never deletes) reports of candidates that ran on the WRONG expert because auto_loop clamped every MR_RegimeSwitch
expert to b52 and could not find the b54+ input lists (stale inputs inherited). Affected: tested names starting n_, b6_, t7_ (b54..b58 gate candidates) and their loop mutations.
Backs up the state files, moves LOOP_<name>_* reports to hst_out/clean/_quarantine_b52clamp_14Oct2026/, and removes those names from loop_state_clean.json
so the fixed loop re-runs them. Run ONLY while no auto_loop is running. python -I data/quarantine_b52clamp.py"""
import json, os, glob, shutil
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; Q = os.path.join(CL, "_quarantine_b52clamp_14Oct2026"); os.makedirs(Q, exist_ok=True)
p = os.path.join(D, "loop_state_clean.json"); shutil.copy(p, p + ".bak_14Oct2026_clamp")
s = json.load(open(p)); T = s["tested"]
bad = [n for n in T if n.startswith(("n_", "b6_", "t7_"))]
moved = 0
for n in bad:
    for f in glob.glob(os.path.join(CL, f"LOOP_{n}_*")):
        shutil.move(f, os.path.join(Q, os.path.basename(f))); moved += 1
    T.pop(n, None)
json.dump(s, open(p, "w"), indent=1)
open(os.path.join(Q, "README.txt"), "w").write("Reports from candidates run before the 2026-10-14 auto_loop fix (expert clamped to b52, b54+ inputs missing from sets). Kept for the record; results invalid.\nNames: " + ", ".join(bad) + "\n")
print(f"quarantined {len(bad)} candidates, moved {moved} files; names: {bad}")
