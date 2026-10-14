"""meta_improve.py - watchdog + self-repair for the self-improvement loop (Nasif 2026-10-14: if self-improvement/self-learning does not work, notify me and
search for other ways to improve automatically). Read-mostly; it only ADDS candidates to data/extra_candidates.json (backup kept) and sends ntfy status alerts.
Detects: STALL (driver up, no new report for 40 min), DUPLICATES (3+ different candidates with identical results = bad test setup), STAGNATION (many candidates
finished and no new leader), EMPTY BREEDERS (2 passes in a row with 0 children), DRIVER DOWN.
Responses: L1 stagnation -> inject DIVERSE exploration candidates (other parents, other timeframes, random gene mixes); L2 prolonged stagnation -> high-priority alert,
data/NEEDS_RESEARCH.txt and an option for Claude to research new methods online; stall/duplicates/driver down -> immediate alert with diagnosis.
Run: python -E -P data/meta_improve.py [--quiet]. Alerts are de-duplicated through data/meta_state.json. Backtest tooling only, never live approval."""
import json, os, re, glob, random, shutil, datetime, subprocess, urllib.request, sys, time
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; LOT = 0.16
now = datetime.datetime.now(); QUIET = "--quiet" in sys.argv
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
def tot(t): o = t.get("oos") or {}; return round(sum(v["profit"] for v in o.values()) / LOT), sum(v["trades"] for v in o.values()), len(o)
fins = [(n, tot(t)) for n, t in T.items() if t.get("oos") and tot(t)[1] >= 100 and tot(t)[2] >= 6]
mp = os.path.join(D, "meta_state.json"); ms = json.load(open(mp)) if os.path.exists(mp) else {"alerts": {}}
def ps(cmd):
    try: return subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=40).stdout.strip()
    except Exception: return ""
driver = bool(ps("(Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | Where-Object { $_.CommandLine -like '*evolve.ps1*' }).ProcessId"))
paused = os.path.exists(r"C:\Users\endos\Desktop\hst_out\MT4_PAUSE")
reports = sorted(glob.glob(os.path.join(CL, "LOOP_*_real.htm")), key=os.path.getmtime); last_rep = datetime.datetime.fromtimestamp(os.path.getmtime(reports[-1])) if reports else None
problems = []; level = 0
if not driver and not paused: problems.append(("DOWN", "The driver is not running and tests are not paused. Reply 'resume'.", "high")); level = max(level, 3)
loop_up = bool(ps("(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*auto_loop*' }).ProcessId"))
if driver and loop_up and last_rep and (now - last_rep).total_seconds() > 2400 and not paused: problems.append(("STALL", f"No new test report for {int((now-last_rep).total_seconds()/60)} min while the loop runs (tester hung or RAM stall). Reply 'resume' after a RAM check, or 'pause all'.", "high")); level = max(level, 3)
dups = {}
for n, v in fins: dups.setdefault(v, []).append(n)
dup = [(v, ns) for v, ns in dups.items() if len(ns) >= 3 and v[1] > 0]
if dup: problems.append(("DUPLICATES", f"{len(dup[0][1])} different candidates have identical results {dup[0][0]}: test setup may be wrong (like the b52 clamp bug). Examples: {', '.join(dup[0][1][:3])}.", "high")); level = max(level, 3)
lead = max(fins, key=lambda x: x[1][0]) if fins else None
def mt(n): return max((os.path.getmtime(f) for f in glob.glob(os.path.join(CL, f"LOOP_{n}_*_real.htm"))), default=0)
since = set()
if lead:
    cut = mt(lead[0])
    since = {re.sub(r"_\d{4}_real\.htm$", "", os.path.basename(f)) for f in reports if os.path.getmtime(f) > cut}; since.discard(lead[0])
    hrs = (now.timestamp() - cut) / 3600 if cut else 0
    if len(since) >= 30 or hrs >= 8: problems.append(("STAGNATION-L2", f"Self-improvement is stuck: {len(since)} candidates and {hrs:.1f} h since the leader {lead[0]} ({lead[1][0]:+d} pts) last changed. Auto-explore already ran; a research round for new methods is recommended. Reply 'research'.", "high")); level = max(level, 2)
    elif len(since) >= 12 or hrs >= 3: problems.append(("STAGNATION-L1", f"No new leader after {len(since)} candidates ({hrs:.1f} h). Injecting diverse exploration candidates automatically.", "default")); level = max(level, 1)
gl = os.path.join(D, "generation_log.md"); zero = 0
try: zero = len(re.findall(r"queued 0 children", open(gl, encoding="utf-8", errors="ignore").read()[-3000:])) + len(re.findall(r"winning genes 0; queued 0", open(os.path.join(D, "evolve_log.txt"), encoding="utf-8", errors="ignore").read()[-3000:]))
except Exception: pass
if zero >= 4: problems.append(("EMPTY-BREEDERS", "The breeders keep proposing nothing new. Switching on exploration.", "default")); level = max(level, 1)
added = []
if level >= 1 and lead and not QUIET:   # AUTO-EXPLORE: diverse candidates the normal breeders do not produce
    ex_path = os.path.join(D, "extra_candidates.json"); ex = json.load(open(ex_path)); seen = {json.dumps({k: v for k, v in sorted(e["patch"].items())}, sort_keys=True) for e in ex}
    rnd = random.Random(int(now.strftime("%Y%m%d%H")))
    parents = [n for n, v in sorted(fins, key=lambda x: -x[1][0])[:6]]
    GENES = [{"QuietRvolMax": 45.6, "QuietZTrigger": 2.0}, {"SlopeGapMode": 1}, {"SlopeStackMode": 1}, {"SsrMode": 1}, {"HurstMax": 0.5}, {"AdxMax": 25}, {"VolRelMax": 1.5}, {"WprMode": 1}, {"AlligatorMode": 1, "AllSpreadPts": 60}, {"FractalMode": 1}, {"ErMax": 0.25}, {"ZExitLevel": 0.5}, {"AcMax": 0.0}, {"UseRegZ": "true"}, {"FibMode": 1}, {"ZTF": 30}, {"ZTF": 60, "ZPeriod": 8}, {"BearBuyBlock": "true", "SideMode": 0}, {"HourFrom": 7, "HourTo": 20}]
    for i in range(6):
        pn = rnd.choice(parents); pp = {k: v for k, v in T[pn]["patch"].items() if k != "_expert"}; p = dict(pp)
        for g in rnd.sample(GENES, rnd.choice([1, 2, 2, 3])): p.update(g)
        p["_expert"] = "MR_RegimeSwitch_b57"; sg = json.dumps({k: v for k, v in sorted(p.items())}, sort_keys=True)
        if sg in seen: continue
        seen.add(sg); ex.append({"name": f"ex_{now:%m%d%H}_{i}", "why": f"auto-explore (stagnation): random gene mix on diverse parent {pn}", "patch": p}); added.append(ex[-1]["name"])
    if added: shutil.copy(ex_path, ex_path + ".bak6_14Oct2026"); json.dump(ex, open(ex_path, "w"), indent=1)
if level >= 2:
    open(os.path.join(D, "NEEDS_RESEARCH.txt"), "w", encoding="utf-8").write(f"{now:%Y-%m-%d %H:%M} self-improvement is stuck. Leader {lead[0] if lead else '?'}; candidates since last improvement {len(since)}.\nAsk Claude to: search the web and papers for new mean-reversion/regime/volatility methods for EURUSD M15, turn the best 3 into new gates in a new MR_RegimeSwitch version, queue them, and report.\nOptions logged in last_options.json.\n")
def push(title, msg, prio):
    t = open(os.path.join(D, "ntfy_topic.txt")).read().strip()
    try: urllib.request.urlopen(urllib.request.Request(f"https://ntfy.sh/{t}", data=msg[:1200].encode(), headers={"Title": title, "Priority": prio}), timeout=10)
    except Exception: pass
sent = []
for code, msg, prio in problems:
    last = ms["alerts"].get(code)
    if last and (now - datetime.datetime.fromisoformat(last)).total_seconds() < (6 if code.startswith("STAG") or code == "EMPTY-BREEDERS" else 1) * 3600: continue
    if not QUIET: push(f"EA watchdog: {code}", msg + (f" Queued {len(added)} exploration candidates." if added and code.startswith(("STAG", "EMPTY")) else "") + " (backtest only)", prio)
    ms["alerts"][code] = now.isoformat(timespec="seconds"); sent.append(code)
good = []   # GOOD NEWS alerts (Nasif 2026-10-14): a new leader, or a candidate that clearly beats the previous best; only candidates with correct rollover (reports RollFrom=23)
if lead and fins and not QUIET:
    pn, (pp, ptr, pyr) = lead
    best = ms.get("best", {"name": "", "pts": -10**9})
    if pn != best["name"] and pp >= best["pts"] * 1.10 and pp > 0:
        flag = ""
        try: cf = json.load(open(os.path.join(D, "cost_flags.json")))["candidates"].get(pn, {}); flag = f" cost flag {cf.get('flag','?')} (break-even {cf.get('break_even')} pts)"
        except Exception: pass
        good.append(f"GOOD NEWS: new leader {pn}: {pp:+d} pts over {pyr} unseen years, {ptr} trades,{flag}. Previous best {best['name'] or 'none'} {best['pts'] if best['name'] else ''}. Unproven until validated (backtest only).")
        ms["best"] = {"name": pn, "pts": pp}
    elif not best["name"]: ms["best"] = {"name": pn, "pts": pp}
for g in good: push("EA good news", g, "high")
json.dump(ms, open(mp, "w"), indent=1)
print(f"watchdog: level {level}; problems {[p[0] for p in problems] or 'none'}; alerts sent {sent or 'none'}; explore candidates added {len(added)}")
