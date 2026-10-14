"""daily_summary.py - one-day summary of the self-improvement loop (stdout: full text; first line = short ntfy alert). Read-only. Backtest numbers only, never live approval.
Run: python -E -P data/daily_summary.py"""
import json, os, glob, time, datetime, re
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; LOT = 0.16
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
def tot(t): o = t.get("oos") or {}; return round(sum(v["profit"] for v in o.values()) / LOT), sum(v["trades"] for v in o.values()), len(o)
rows = sorted(((tot(t), n) for n, t in T.items() if t.get("oos") and tot(t)[1] >= 100 and tot(t)[2] >= 6), reverse=True)
now = time.time(); day = now - 86400
new_reports = [f for f in glob.glob(os.path.join(CL, "LOOP_*_real.htm")) if os.path.getmtime(f) > day]
done_cands = sorted({re.sub(r"_(\d{4})_real\.htm$", "", os.path.basename(f))[5:] for f in new_reports})
passes = 0
try:
    for ln in open(os.path.join(D, "evolve_log.txt"), encoding="utf-8", errors="ignore"):
        if " done:" in ln and "pass" in ln and ln[:10] == datetime.date.today().isoformat(): passes += 1
except Exception: pass
base = json.load(open(os.path.join(D, "loop_state.json"))).get("base_real") or {}
bpts = round(sum((v["profit"] if isinstance(v, dict) else v) for v in base.values()) / LOT) if base else None
lead = rows[0] if rows else None
alert = (f"Daily EA summary: best {lead[1]} {lead[0][0]:+d} pts/{lead[0][1]} trades/{lead[0][2]} yrs; " if lead else "Daily EA summary: no leader yet; ") + f"{len(done_cands)} candidates tested today, {passes} passes done (backtest only)."
out = [alert, "", f"Daily summary {datetime.datetime.now():%Y-%m-%d %H:%M} (backtest leads only, never live approval)", ""]
out += ["Top candidates over the 8 unseen years (pts = profit / 0.16 lots):"] + [f"  {i+1}. {n}: {p:+d} pts, {tr} trades, {y} yrs (about {p/y/12:+.0f} pts/month, about {p/y/12*0.6:+.0f} with a -40% haircut)" for i, ((p, tr, y), n) in enumerate(rows[:5])]
if bpts is not None: out.append(f"Base system over the same years: {bpts:+d} pts")
out += ["", f"Tested in the last 24 h: {len(done_cands)} candidates ({len(new_reports)} year-tests). Passes finished today: {passes}.",
        "Candidates today: " + (", ".join(done_cands[:20]) or "none"),
        "", "Watch for: small samples (best leads have few trades), selection bias from many tests, cost assumptions (about 3-5 pts per trade).", ""]
try: out.append("Last driver log line: " + open(os.path.join(D, "evolve_log.txt"), encoding="utf-8", errors="ignore").read().strip().splitlines()[-1][:160])
except Exception: pass
import subprocess
try: out += ["", "Next test recommendation: " + subprocess.run(["python", "-E", "-P", os.path.join(D, "recommend.py")], capture_output=True, text=True, timeout=120).stdout.strip()]
except Exception: pass
try:
    r = subprocess.run(["python", "-E", "-P", os.path.join(D, "dsr_check.py")], capture_output=True, text=True, timeout=180).stdout.splitlines()
    row = [l for l in r if l.startswith("| ") and "DSR" not in l and "---" not in l][:1]
    if row: out += ["", "Deflated Sharpe check (is the best result luck?): " + row[0] + "  (0.95+ suggests real; counts fewer trials than were tried)"]
except Exception: pass
print("\n".join(out))
