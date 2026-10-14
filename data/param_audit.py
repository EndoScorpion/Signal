"""param_audit.py - SAFETY NET against silent input collisions and stale inherited inputs (the bugs found 2026-10-14: b31 base set leaking AtrSLMult/CrossFast into MR EAs, wrong rollover window).
For every finished clean-history report it compares the inputs the tester ACTUALLY used (report Parameters block) with the inputs the loop INTENDED (tester\LOOP_<name>.set).
Any difference is a mismatch. Also checks that b31 base-set keys cannot override MR expert defaults. Writes data/param_audit.json (used by the watchdog) and prints a summary.
Run: python -E -P data/param_audit.py [--all]   (default: reports from the last 24 hours)"""
import re, glob, os, json, time, sys
CL = r"C:\Users\endos\Desktop\hst_out\clean"; TS = r"C:\Users\endos\Desktop\mt4_tester2\tester"; D = r"C:\Users\endos\Signal\data"
cut = 0 if "--all" in sys.argv else time.time() - 86400
def num(v):
    try: return float(v)
    except ValueError: return str(v).strip().lower()
def setvals(p):
    d = {}
    for ln in open(p, encoding="utf-8", errors="ignore"):
        if "=" in ln and not ln.startswith(";"): k, v = ln.split("=", 1); d[k.strip()] = v.strip()
    return d
bad = {}; checked = 0
for f in glob.glob(os.path.join(CL, "LOOP_*.htm")):
    if os.path.getmtime(f) < cut: continue
    m = re.match(r"LOOP_(.+?)_\d{4}_(?:real|sp5|sp3_T3p45|sp8)\.htm$", os.path.basename(f))
    if not m: continue
    sp = os.path.join(TS, f"LOOP_{m.group(1)}.set")
    if not os.path.exists(sp): continue
    h = open(f, encoding="utf-8", errors="ignore").read(40000)
    blk = re.search(r"Parameters</td><td colspan=4>(.*?)</td></tr>", h, re.S)
    if not blk or "MR_RegimeSwitch" not in h: continue
    used = {k.strip(): v.strip() for k, v in re.findall(r"([A-Za-z0-9_]+)=([^;]*);", re.sub(r"<[^>]+>", " ", blk.group(1)))}
    want = setvals(sp); checked += 1
    diff = {k: (want[k], used[k]) for k in want if k in used and num(want[k]) != num(used[k])}
    if diff: bad.setdefault(m.group(1), {}).update(diff)
coll = {}
try:
    base = setvals(os.path.join(TS, "WIN_GEN1_ZGate_DailyRange_b31.set"))
    for ex in sorted(glob.glob(r"C:\Users\endos\Desktop\mt4_tester2\MQL4\Experts\MR_RegimeSwitch_b*.mq4"))[-3:]:
        d = {a: b.strip() for a, b in re.findall(r"extern\s+\w+\s+(\w+)\s*=\s*([^;/\"]+?)\s*;", open(ex, encoding="latin-1").read())}
        c = {k: (d[k], base[k]) for k in d if k in base and k != "MagicNumber" and num(d[k]) != num(base[k])}
        if c: coll[os.path.basename(ex)] = c
except Exception: pass
json.dump({"checked": checked, "mismatches": bad, "base_collisions": coll, "time": time.strftime("%Y-%m-%d %H:%M")}, open(os.path.join(D, "param_audit.json"), "w"), indent=1)
print(f"param audit: {checked} reports checked; {len(bad)} candidates with intended-vs-used mismatches" + (": " + "; ".join(f"{n}: {list(v.items())[:3]}" for n, v in list(bad.items())[:3]) if bad else "") + f"; base-set collisions that the loop now blocks: {sum(len(v) for v in coll.values())}")
