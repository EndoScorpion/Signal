"""recommend.py - next-step recommendation for the hourly and daily phone reports (read-only; it only SUGGESTS, Nasif or Claude decides).
Signals: stagnation (many candidates finished since the leader last changed), small sample, one-year concentration, queue families still untested,
failing families, RAM/driver state. Prints one short paragraph ending with the phrase to reply with. Backtest tooling only, never live approval."""
import json, os, re, glob, datetime, subprocess
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; LOT = 0.16
now = datetime.datetime.now()
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
def tot(t): o = t.get("oos") or {}; return sum(v["profit"] for v in o.values()) / LOT, sum(v["trades"] for v in o.values()), len(o)
fins = [(n, tot(t)) for n, t in T.items() if t.get("oos") and tot(t)[1] >= 100 and tot(t)[2] >= 6]
rec = []
if not fins: print("No leader yet: let the first pass finish before changing anything."); raise SystemExit
lead = max(fins, key=lambda x: x[1][0]); ln, (lp, ltr, ly) = lead
def mt(n):
    fs = glob.glob(os.path.join(CL, f"LOOP_{n}_*_real.htm")); return max((os.path.getmtime(f) for f in fs), default=0)
lead_t = datetime.datetime.fromtimestamp(mt(ln)) if mt(ln) else None
cut = lead_t or (now - datetime.timedelta(hours=6))
since = {re.sub(r"_\d{4}_real\.htm$", "", os.path.basename(f)) for f in glob.glob(os.path.join(CL, "LOOP_*_real.htm")) if datetime.datetime.fromtimestamp(os.path.getmtime(f)) > cut}
since.discard(ln)
reg = {}
try: reg = json.load(open(os.path.join(D, "logic_registry.json")))
except Exception: pass
queued = [e["name"] for e in json.load(open(os.path.join(D, "extra_candidates.json"))) if e["name"] not in T]
fam = {}
for q in queued:
    k = re.match(r"([a-z]+\d?)_", q); fam[k.group(1) if k else q] = fam.get(k.group(1) if k else q, 0) + 1
oy = T[ln].get("oos", {}); ypts = sorted(((v["profit"] / LOT, y) for y, v in oy.items()), reverse=True); share = (ypts[0][0] / lp) if lp > 0 and ypts else 0
free = 0
try: free = int(subprocess.run(["powershell", "-NoProfile", "-Command", "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)"], capture_output=True, text=True, timeout=30).stdout.strip() or 0)
except Exception: pass
driver = bool([l for l in subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | Where-Object { $_.CommandLine -like '*evolve.ps1*' }).ProcessId"], capture_output=True, text=True, timeout=30).stdout.split() if l])
paused = os.path.exists(r"C:\Users\endos\Desktop\hst_out\MT4_PAUSE")
if not driver and not paused: rec.append("The driver is DOWN: reply 'resume' to restart it.")
elif free and free < 700: rec.append(f"RAM is low ({free} MB): consider 'pause all' until it recovers (or close a browser).")
if len(since) >= 8:
    untested = {k: v for k, v in fam.items() if k in ("b6", "t7", "n", "x3", "th", "s")}
    rec.append(f"Stagnation: {len(since)} candidates finished since the leader {ln} last changed. Recommend 'pause all', then reorder the queue to the untested new theories ({', '.join(f'{k}:{v}' for k, v in untested.items()) or 'none left'}) ahead of the g2 mutations, or build the next EA theories (Ehlers cycle, Kalman channel, variance regime).")
if ltr < 150: rec.append(f"Leader {ln} has only {ltr} trades: validate it on the 8 training periods and spreads 5 and 8 before cloning it further.")
if share > 0.5 and ypts: rec.append(f"{100*share:.0f}% of the leader's profit comes from {ypts[0][1]}: test more quiet and hard years (walk-forward) before trusting it.")
ret = [k for k, v in reg.items() if v.get("status") == "retired"]
if ret: rec.append(f"{len(ret)} logic ideas retired after failed salvage: {', '.join(ret[:3])}.")
if not rec: rec.append("No change needed: keep running. Next up: " + (", ".join(queued[:4]) or "queue empty (the breeders will refill it)") + ".")
opts = []
if not driver and not paused: opts.append(("Resume the driver", "resume"))
if free and free < 700 and not paused: opts.append(("Pause until RAM recovers", "pause_all"))
if len(since) >= 8: opts += [("Pause, then move the untested new theories (b6/t7/n) to the front of the queue", "pause_reorder"), ("Build the next EA theories (Ehlers cycle, Kalman channel, variance regime) as b58 and queue them", "build_b58")]
if ltr < 150: opts.append(("Validate the leader on the 8 training periods and spreads 5 and 8", "validate_leader"))
if share > 0.5 and ypts: opts.append((f"Walk-forward the leader on more quiet and hard years ({ypts[0][1]} gives most of its profit)", "walkforward"))
if os.path.exists(os.path.join(D, "NEEDS_RESEARCH.txt")): opts.insert(0, ("Research new methods online (Claude searches, builds new gates in a new EA version, queues them)", "research"))
opts.append(("Keep running as is", "keep"))
if not paused: opts.append(("Pause all", "pause_all"))
seen_a = set(); opts = [o for o in opts if not (o[1] in seen_a or seen_a.add(o[1]))][:4]
json.dump({"time": now.isoformat(timespec="seconds"), "leader": ln, "options": [{"n": i + 1, "label": l, "action": a} for i, (l, a) in enumerate(opts)]}, open(os.path.join(D, "last_options.json"), "w"), indent=1)
print((" ".join(rec)[:600] + " OPTIONS: " + " ".join(f"{i+1}) {l}." for i, (l, a) in enumerate(opts)) + " Reply 'proceed with option N'.")[:1100])
