"""theorize.py - the ANALYZE -> THEORIZE step of the self-improvement cycle (Nasif 2026-10-14).
Takes the current leader's trade reports (clean history, all unseen years), maps every trade to market-state features at entry
(SMA slope gap / slope-stack convergence, SSR, flat slopes, 4-hour block, weekday, ATR level) and finds the buckets where the leader loses most.
Each loss bucket becomes a LOSS-PROTECTION candidate: the leader's patch + the existing gate input that skips that bucket (b58/b57 expert).
Only ADDS entries to data/extra_candidates.json (backup kept) and appends data/generation_log.md. Offline, backtest leads only, never live approval.
Run: python -E -P data/theorize.py [--max 6]"""
import re, struct, glob, os, math, json, bisect, shutil, datetime, sys
import numpy as np
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; LOT = 0.16
MAXC = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 6
HST = r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server\EURUSD15.hst"
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
def tot(t): o = t.get("oos", {}); return sum(v["profit"] for v in o.values()) / LOT, sum(v["trades"] for v in o.values()), len(o)
cands = [(n, tot(t)) for n, t in T.items() if "MR_RegimeSwitch" in str(t.get("expert") or t.get("patch", {}).get("_expert")) and tot(t)[1] >= 100 and tot(t)[2] >= 6]
if not cands: raise SystemExit("no leader yet")
leader = max(cands, key=lambda c: c[1][0])[0]; lp = {k: v for k, v in T[leader]["patch"].items() if k != "_expert"}
a = np.memmap(HST, dtype=np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"), ("tv", "<i8"), ("sp", "<i4"), ("rv", "<i8")]), mode="r", offset=148)
Tt = np.asarray(a["t"]); C = np.asarray(a["c"]); H = np.asarray(a["h"]); L = np.asarray(a["l"]); n = len(C)
def sl(p):
    cs = np.cumsum(np.insert(C, 0, 0.0)); m = np.full(n, np.nan); m[p - 1:] = (cs[p:] - cs[:-p]) / p; s = np.zeros(n); s[1:] = np.diff(m) * 1e5; return np.nan_to_num(s)
S = {p: sl(p) for p in (10, 20, 50, 100, 200)}
tr = np.maximum(H - L, np.maximum(np.abs(H - np.roll(C, 1)), np.abs(L - np.roll(C, 1)))); atr = np.convolve(tr, np.ones(14) / 14, mode="same") * 1e5
def sd5(i): v = [S[p][i] for p in S]; return float(np.std(v))
def feats(ts):
    i = int(np.searchsorted(Tt, ts - 900)) - 1
    if i < 210: return None
    f, s = S[20][i], S[200][i]; r = (f / s) if abs(s) > 0.05 else None
    ssr = "n/a" if r is None else ("opposite" if r < 0 else ("aligned" if 0.2 <= r <= 5 else "extreme"))
    d = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    return {"gap": "gap_diverging" if abs(S[20][i] - S[50][i]) >= abs(S[20][i - 1] - S[50][i - 1]) else "gap_converging",
            "stack": "stack_diverging" if sd5(i) >= sd5(i - 1) else "stack_converging", "ssr": ssr,
            "flat": "flat_fast" if abs(f) < 1.0 else "moving_fast", "hour4": f"hours_{(d.hour // 4) * 4:02d}-{(d.hour // 4) * 4 + 3:02d}",
            "weekday": d.strftime("%a"), "atr": "atr_low" if atr[i] < 40 else ("atr_mid" if atr[i] < 80 else "atr_high")}
trades = []
for fp in sorted(glob.glob(os.path.join(CL, f"LOOP_{leader}_[0-9][0-9][0-9][0-9]_real.htm"))):
    html = open(fp, encoding="utf-8", errors="ignore").read(); op = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(c) >= 8 and c[2] in ("buy", "sell") and re.match(r"\d{4}\.", c[1]): op[c[3]] = (c[1], float(c[4]))
        elif len(c) >= 10 and c[2] in ("s/l", "t/p", "close") and c[3] in op and c[8]:
            try: pnl = float(c[8].replace(" ", ""))
            except ValueError: continue
            tm, sz = op.pop(c[3]); ts = int(datetime.datetime.strptime(tm, "%Y.%m.%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp()); trades.append((ts, pnl / sz))
bk = {}
for ts, pts in trades:
    f = feats(ts)
    if f:
        for k, v in f.items(): b = bk.setdefault((k, v), [0, 0.0]); b[0] += 1; b[1] += pts
N = len(trades); avg = sum(p for _, p in trades) / max(1, N)
GATE = {("gap", "gap_diverging"): ({"SlopeGapMode": 1}, "skip diverging SMA20/SMA50 slope gap"),
        ("stack", "stack_diverging"): ({"SlopeStackMode": 1}, "skip diverging SMA slope stack"),
        ("ssr", "extreme"): ({"SsrMode": 1}, "skip extreme/diverged SSR"), ("ssr", "opposite"): ({"SsrMode": 1}, "skip opposite-sign SSR"),
        ("flat", "flat_fast"): ({"SlopeStackAbsMin": 1.0}, "skip flat slopes"), ("atr", "atr_high"): ({"AtrCapPts": 60}, "tighter ATR cap"),
        ("atr", "atr_low"): ({"QuietRvolMax": 0}, None)}
worst = sorted([(s / c, k, c, s) for k, (c, s) in bk.items() if c >= 30 and s / c < avg - 5], key=lambda x: x[0])[:12]
ex_path = os.path.join(D, "extra_candidates.json"); ex = json.load(open(ex_path)); seen = {json.dumps({k: v for k, v in sorted(e["patch"].items())}, sort_keys=True) for e in ex}
newex = os.path.exists(r"C:\Users\endos\Desktop\mt4_tester2\MQL4\Experts\MR_RegimeSwitch_b58.ex4")
EXP = "MR_RegimeSwitch_b58" if newex else "MR_RegimeSwitch_b57"; add = []
for av, k, c, s in worst:
    if len(add) >= MAXC: break
    g = GATE.get(k)
    if k[0] == "hour4":
        h0 = int(k[1][6:8]); ok = [h for h in range(24) if not (h0 <= h <= h0 + 3)]; g = ({"HourFrom": (h0 + 4) % 24, "HourTo": (h0 - 1) % 24}, f"avoid server hours {h0}-{h0+3}")
    if not g or g[1] is None: continue
    p = dict(lp); p.update(g[0]); p["_expert"] = EXP; sg = json.dumps({a: b for a, b in sorted(p.items())}, sort_keys=True)
    if sg in seen: continue
    seen.add(sg); add.append({"name": f"th_{leader[:18]}_{k[1]}".replace(".", "p"), "why": f"loss protection from leader {leader}: {k[1]} avg {av:.0f} pts over {c} trades; {g[1]}", "patch": p})
if add: shutil.copy(ex_path, ex_path + ".bak4_14Oct2026"); json.dump(ex + add, open(ex_path, "w"), indent=1)
with open(os.path.join(D, "generation_log.md"), "a") as f:
    f.write(f"\n## theorize {datetime.datetime.now():%Y-%m-%d %H:%M}\nLeader {leader}: {N} trades, avg {avg:.1f} pts. Worst buckets: " + "; ".join(f"{k[1]} {av:.0f} pts x{c}" for av, k, c, s in worst[:6]) + f". Queued {len(add)} loss-protection candidates: {[x['name'] for x in add]}\n")
print(f"leader {leader}: {N} trades avg {avg:.1f}; worst buckets {[(k[1], round(av), c) for av, k, c, s in worst[:6]]}; queued {len(add)}")
