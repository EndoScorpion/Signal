#!/usr/bin/env python3
"""
fx_scalp_sweep.py - Grid-search TP/SL/trail combos on MT4 M1 EURUSD CSV.
Usage:
  python3 fx_scalp_sweep.py data/EURUSD_M1_2011_2026.csv [--comm 7.7] [--csv results/sweep.csv]

Reuses fx_scalp_sim.py internals (no orders, research only).
Outputs a markdown table + optional CSV ranked by avg_net pts descending.
"""
import csv as csvmod, sys, argparse, itertools, datetime, importlib, types

ap = argparse.ArgumentParser()
ap.add_argument("csv", nargs="?")
ap.add_argument("--synthetic", action="store_true")
ap.add_argument("--spread",    type=float, default=3)
ap.add_argument("--maxspread", type=float, default=8)
ap.add_argument("--comm",      type=float, default=7.7,
                help="round-turn commission in points (default 7.7 = FXOpen base tier)")
ap.add_argument("--swap",      type=float, default=0)
ap.add_argument("--swaphour",  type=int,   default=22)
ap.add_argument("--frihour",   type=int,   default=19)
ap.add_argument("--rollhour",  type=int,   default=23)
ap.add_argument("--maxhold",   type=int,   default=1440)
ap.add_argument("--cooldown",  type=int,   default=5)
ap.add_argument("--min-n",     type=int,   default=30,   dest="min_n")
ap.add_argument("--csv",       default=None)
ap.add_argument("--session",   choices=["all","1620","0004","1216","2024"],
                default="all", help="session hour filter (server time)")
a = ap.parse_args()

P = 1e-5

# --- load bars (same format as fx_scalp_sim.py) ---
def load():
    if a.synthetic:
        import random; random.seed(1); x = 1.1; out = []
        t = datetime.datetime(2023, 1, 2)
        while len(out) < 150000:
            if t.weekday() < 5:
                o = x; hi = lo = x
                for _ in range(4):
                    x += random.gauss(0, 2.5) * P
                    hi = max(hi, x); lo = min(lo, x)
                out.append((t, o, hi, lo, x))
            t += datetime.timedelta(minutes=1)
        return out
    out = []
    for r in csvmod.reader(open(a.csv)):
        try:
            out.append((datetime.datetime.strptime(r[0] + " " + r[1], "%Y.%m.%d %H:%M"),
                        float(r[2]), float(r[3]), float(r[4]), float(r[5])))
        except Exception:
            pass
    return out

B = load(); n = len(B)
o = [b[1] for b in B]; h = [b[2] for b in B]
l = [b[3] for b in B]; c = [b[4] for b in B]

sma2 = [None] + [(c[i] + c[i-1]) / 2 for i in range(1, n)]
blk  = [(max(h[i:i+15]), min(l[i:i+15]), c[min(i+14, n-1)]) for i in range(0, n, 15)]
raw  = [None if k < 9 else
        (lambda hh, ll, cc: 50 if hh == ll else 100 * (cc - ll) / (hh - ll))
        (max(b[0] for b in blk[k-9:k+1]),
         min(b[1] for b in blk[k-9:k+1]),
         blk[k][2])
        for k in range(len(blk))]

def sm(x, m):
    return [None if i < m-1 or any(v is None for v in x[i-m+1:i+1])
            else sum(x[i-m+1:i+1]) / m for i in range(len(x))]
st = sm(sm(raw, 3), 3)

# session mask
def in_session(t):
    h0 = t.hour
    if a.session == "1620": return 16 <= h0 < 20
    if a.session == "0004": return 0  <= h0 < 4
    if a.session == "1216": return 12 <= h0 < 16
    if a.session == "2024": return 20 <= h0 < 24
    return True

def signals():
    s = []; last = -10**9
    for i in range(20, n-2):
        t = B[i][0]
        if sma2[i] is None or (sma2[i] - sma2[i-1]) / P < 2: continue
        k = i // 15 - 2
        if k < 0 or st[k] is None or st[k] > 80: continue
        if t.weekday() == 4 and t.hour >= a.frihour: continue
        if t.hour >= a.swaphour: continue
        if not in_session(t): continue
        if i - last < a.cooldown: continue
        s.append(i); last = i
    return s

SIG = signals()

def sim(tp, sl, trig=None, trail=None, flat_roll=False):
    res = []; busy = -1
    for i in SIG:
        if i <= busy: continue
        e = i + 1; ent = o[e] + a.spread * P
        stop = ent - sl * P; tgt = ent + tp * P if tp < 10**5 else None
        best = ent; exitp = None; rolls = 0; m = e
        while m < n:
            t = B[m][0]
            if m > e:
                if l[m] <= stop:
                    exitp = stop if o[m] > stop else o[m]; break
                if tgt is not None and h[m] >= tgt:
                    exitp = tgt; break
            if m > e and t.hour == a.rollhour and B[m-1][0].hour != a.rollhour:
                if flat_roll: exitp = o[m]; break
                rolls += 1
            best = max(best, h[m])
            if trail is not None and trig is not None and (best - ent) / P >= trig:
                stop = max(stop, best - trail * P)
            if m - e >= a.maxhold: exitp = c[m]; break
            m += 1
        if exitp is None: exitp = c[n-1]
        pnl = (exitp - ent) / P - a.comm - a.swap * rolls
        res.append(pnl); busy = m
    return res

# period breakdown
def period_label(t):
    y = t.year
    if y <= 2019: return "2015-19"
    if y <= 2022: return "2020-22"
    return "2023-26"

def per_period(res_with_idx):
    from collections import defaultdict
    pd = defaultdict(list)
    for pnl, idx in res_with_idx:
        lbl = period_label(B[idx][0])
        pd[lbl].append(pnl)
    return pd

def sim_indexed(tp, sl, trig=None, trail=None, flat_roll=False):
    res = []; busy = -1
    for i in SIG:
        if i <= busy: continue
        e = i + 1; ent = o[e] + a.spread * P
        stop = ent - sl * P; tgt = ent + tp * P if tp < 10**5 else None
        best = ent; exitp = None; rolls = 0; m = e
        while m < n:
            t = B[m][0]
            if m > e:
                if l[m] <= stop:
                    exitp = stop if o[m] > stop else o[m]; break
                if tgt is not None and h[m] >= tgt:
                    exitp = tgt; break
            if m > e and t.hour == a.rollhour and B[m-1][0].hour != a.rollhour:
                if flat_roll: exitp = o[m]; break
                rolls += 1
            best = max(best, h[m])
            if trail is not None and trig is not None and (best - ent) / P >= trig:
                stop = max(stop, best - trail * P)
            if m - e >= a.maxhold: exitp = c[m]; break
            m += 1
        if exitp is None: exitp = c[n-1]
        pnl = (exitp - ent) / P - a.comm - a.swap * rolls
        res.append((pnl, e)); busy = m
    return res

# Grid
COMBOS = [
    ("current EA",           dict(tp=8,     sl=290)),
    ("TP15 SL30",            dict(tp=15,    sl=30)),
    ("TP20 SL40",            dict(tp=20,    sl=40)),
    ("TP20 SL60",            dict(tp=20,    sl=60)),
    ("TP30 SL40",            dict(tp=30,    sl=40)),
    ("TP40 SL40",            dict(tp=40,    sl=40)),
    ("TP40 SL60",            dict(tp=40,    sl=60)),
    ("TP60 SL40",            dict(tp=60,    sl=40)),
    ("trail20@20 SL40",      dict(tp=10**6, sl=40,  trig=20,  trail=20)),
    ("trail30@30 SL60",      dict(tp=10**6, sl=60,  trig=30,  trail=30)),
    ("TP40+trail15@15 SL40", dict(tp=40,    sl=40,  trig=15,  trail=15)),
    ("TP60+trail20@20 SL40", dict(tp=60,    sl=40,  trig=20,  trail=20)),
    ("TP20 SL40 flat_roll",  dict(tp=20,    sl=40,  flat_roll=True)),
    ("TP30 SL40 flat_roll",  dict(tp=30,    sl=40,  flat_roll=True)),
]

print(f"bars={n} signals={len(SIG)} spread={a.spread} comm={a.comm} "
      f"session={a.session}" + ("  [SYNTHETIC]" if a.synthetic else ""))
print()

cols = ["label", "n", "win%", "avg_net", "total", "worst",
        "2015-19 n", "2020-22 n", "2023-26 n",
        "2015-19 avg", "2020-22 avg", "2023-26 avg",
        "B/E win%"]

rows = []
for label, kwargs in COMBOS:
    ri = sim_indexed(**kwargs)
    if not ri:
        rows.append({"label": label, "n": 0}); continue
    pnls = [p for p, _ in ri]
    w    = sum(x > 0 for x in pnls)
    pd   = per_period(ri)
    # break-even win% from comm math: comm / (comm + avg_win - 0) ... use actual avg_win/loss
    wins   = [x for x in pnls if x > 0]
    losses = [x for x in pnls if x <= 0]
    avg_w  = sum(wins) / len(wins) if wins else 0
    avg_l  = abs(sum(losses) / len(losses)) if losses else 0
    be     = avg_l / (avg_w + avg_l) * 100 if (avg_w + avg_l) > 0 else None
    row = {
        "label": label,
        "n": len(pnls),
        "win%": f"{100*w/len(pnls):.1f}",
        "avg_net": f"{sum(pnls)/len(pnls):.2f}",
        "total": f"{sum(pnls):.0f}",
        "worst": f"{min(pnls):.0f}",
        "B/E win%": f"{be:.1f}" if be else "n/a",
    }
    for per in ["2015-19", "2020-22", "2023-26"]:
        pp = pd.get(per, [])
        row[f"{per} n"]   = len(pp)
        row[f"{per} avg"] = f"{sum(pp)/len(pp):.2f}" if pp else "n/a"
    rows.append(row)

# sort by avg_net desc
def sortkey(r):
    try: return -float(r.get("avg_net", "-9999"))
    except: return 9999

rows.sort(key=sortkey)

# print markdown
header = "| label | n | win% | avg_net | total | worst | 15-19n | 20-22n | 23-26n | 15-19avg | 20-22avg | 23-26avg | B/E% |"
sep    = "|-------|---|------|---------|-------|-------|--------|--------|--------|----------|----------|----------|------|"
print(header); print(sep)
for r in rows:
    print(f"| {r.get('label','')} | {r.get('n','')} | {r.get('win%','n/a')} "
          f"| {r.get('avg_net','n/a')} | {r.get('total','n/a')} | {r.get('worst','n/a')} "
          f"| {r.get('2015-19 n','n/a')} | {r.get('2020-22 n','n/a')} | {r.get('2023-26 n','n/a')} "
          f"| {r.get('2015-19 avg','n/a')} | {r.get('2020-22 avg','n/a')} | {r.get('2023-26 avg','n/a')} "
          f"| {r.get('B/E win%','n/a')} |")

if a.csv:
    with open(a.csv, "w", newline="") as f:
        w = csvmod.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"\nSaved → {a.csv}")
