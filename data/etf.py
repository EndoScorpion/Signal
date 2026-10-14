"""etf.py - one-line progress for the phone report: wins and win rate so far, ETF of the CURRENT test and of the whole round/queue. Read-only. Backtest only.
Wins = finished candidates (>=100 trades, >=6 unseen years) with positive total points; also how many beat the base system. Win rate = share of profitable trades of the current leader
(clean-history reports). Rate = median gap between consecutive year-test reports; candidate rate = candidates finished since this pass started (fallback 8.6 min)."""
import json, os, re, datetime, glob, statistics
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; LOT = 0.16
def fmt(m): m = max(0, int(round(m))); return f"{m//60}h{m%60:02d}m" if m >= 60 else f"{m}m"
now = datetime.datetime.now(); start = None; npass = 0
try:
    for ln in open(os.path.join(D, "evolve_log.txt"), encoding="utf-8", errors="ignore"):
        m = re.match(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) pass (\d+) start", ln)
        if m: start = datetime.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"); npass = int(m.group(2))
except Exception: pass
prog = {}
try: prog = json.load(open(os.path.join(D, "loop_progress.json")))
except Exception: pass
done = int(prog.get("done", 0)); total = int(prog.get("total", 0)); yi = int(prog.get("year_idx", 0)); ny = int(prog.get("years", 8))
reports = sorted(glob.glob(os.path.join(CL, "LOOP_*_real.htm")), key=os.path.getmtime)
recent = [os.path.getmtime(f) for f in reports if datetime.datetime.fromtimestamp(os.path.getmtime(f)) >= now - datetime.timedelta(hours=6)]
gaps = [b - a for a, b in zip(recent, recent[1:]) if 5 < b - a < 900]
per_test = statistics.median(gaps) / 60 if gaps else 3.0
fin = 0
if start:
    fin = len({re.sub(r"_\d{4}_real\.htm$", "", os.path.basename(f)) for f in reports if datetime.datetime.fromtimestamp(os.path.getmtime(f)) >= start})
el = (now - start).total_seconds() / 60 if start else 0
rate = el / fin if (start and fin >= 2 and el > 0) else 8.6
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
def tot(t): o = t.get("oos") or {}; return sum(v["profit"] for v in o.values()) / LOT, sum(v["trades"] for v in o.values()), len(o)
fins = [(n, tot(t)) for n, t in T.items() if t.get("oos") and tot(t)[1] >= 100 and tot(t)[2] >= 6]
wins = [n for n, (p, tr, y) in fins if p > 0]
base = json.load(open(os.path.join(D, "loop_state.json"))).get("base_real") or {}
bp = sum((v["profit"] if isinstance(v, dict) else v) for v in base.values()) / LOT if base else None
beat = [n for n, (p, tr, y) in fins if bp is not None and p > bp]
lead = max(fins, key=lambda x: x[1][0]) if fins else None
wr = ""
if lead:
    w = n_ = 0
    for f in glob.glob(os.path.join(CL, f"LOOP_{lead[0]}_[0-9][0-9][0-9][0-9]_real.htm")):
        h = open(f, encoding="utf-8", errors="ignore").read(); a = re.search(r"Profit trades \(% of total\)</td><td align=right>(\d+)", h); b = re.search(r"Total trades</td><td align=right>(\d+)", h)
        if a and b: w += int(a.group(1)); n_ += int(b.group(1))
    wr = f"; leader {lead[0]} win rate {100*w/max(1,n_):.1f}% ({w}/{n_} trades)"
cur_left = max(0, ny - yi) * per_test if yi else 0
left_pass = max(0, total - done) if total else 0
queued = [e["name"] for e in json.load(open(os.path.join(D, "extra_candidates.json"))) if e["name"] not in T]
ends = (start + datetime.timedelta(hours=14)) if start else None
msg = (f"WINS {len(wins)}/{len(fins)} finished candidates positive, {len(beat)} beat base{wr}. "
       f"ETF current candidate (year {yi}/{ny}, ~{per_test:.1f} min/test): {fmt(cur_left)}; round (pass {npass}, {left_pass} candidates left, ~{rate:.1f} min each): {fmt(left_pass * rate)}; "
       f"whole queue ({len(queued)} candidates): {fmt(len(queued) * rate)}")
if ends: msg += f"; driver stops by {ends:%H:%M} at the latest"
print(msg)
