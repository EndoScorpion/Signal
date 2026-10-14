"""
TIME NOTE: SPR hour keys are UTC hours (CSV clock) while the M15 .hst used here carries a mixed (patchwork) clock; hour-based costs are approximate. Redo on the clean history (mt4_tester2, server clock UTC+2/+3 US DST).
shadow_audit.py - silent audit of ALTERNATIVE entry logic. Never blocks, gates or feeds back into the test loop.
Replays EURUSD M15 history and logs what other triggers would have done (fixed H-bar exit, net of 5 pts commission + hourly spread),
per trigger per year, plus how often each trigger fires where the base EA was flat (complement) on years with base reports.
Outputs: data/shadow_audit.csv (append-only ledger, one block per run), data/ALT_WIN_LOGIC.md (auto summary).
Triggers: z-score fades (N 10/20/50, k 2/2.5, H 16/48, buy/sell), stochastic extremes fade, z continuation (momentum).
Offline, no MT4; skips itself if RAM is tight. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>."""
import os, csv, sys, math, datetime, importlib.util, ctypes
DATA = r"C:\Users\endos\Signal\data"; HST = r"C:\Users\endos\Desktop\hst_out"
class M(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong * 5)]
m = M(); m.l = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
if m.ap / 2**30 < 0.9 and "--force" not in sys.argv: raise SystemExit(f"skipped: only {m.ap/2**30:.2f} GB free")
SPR = {0: 1.3, 1: 1.2, 2: 1.2, 3: 1.1, 4: 1.1, 5: 1.2, 6: 1.1, 7: 1.1, 8: 1.0, 9: 1.0, 10: 0.9, 11: 0.9, 12: 1.1, 13: 1.1, 14: 1.0, 15: 0.9,
       16: 1.0, 17: 1.1, 18: 1.1, 19: 1.1, 20: 2.5, 21: 17.1, 22: 7.7, 23: 1.6}   # mean spread pts by server hour 2023-26
COMM = 5.0
ep, cl, k14, yr, hr = [], [], [], [], []
for r in csv.DictReader(open(os.path.join(DATA, "m15_metrics.csv"))):
    t = int(r["ts"]); d = datetime.datetime.utcfromtimestamp(t)
    ep.append(t); cl.append(float(r["close"])); k14.append(float(r["stoch_k14"])); yr.append(d.year); hr.append(d.hour)
n = len(cl); P1 = [0.0]; P2 = [0.0]
for c in cl: P1.append(P1[-1] + c); P2.append(P2[-1] + c * c)
def zs(i, N):
    mu = (P1[i + 1] - P1[i + 1 - N]) / N; v = (P2[i + 1] - P2[i + 1 - N]) / N - mu * mu
    return (cl[i] - mu) / math.sqrt(v) if v > 0 else 0.0
def run(sig, H):
    out = []; i = 60
    while i < n - H:
        d = sig(i)
        if d and ep[i + H] - ep[i] <= H * 900 * 1.25:
            out.append((i, d * (cl[i + H] - cl[i]) * 1e5 - COMM - SPR[hr[i]])); i += H
        else: i += 1
    return out
trig = []
for N in (10, 20, 50):
    for k in (2.0, 2.5):
        for H in (16, 48):
            trig.append((f"zfade_N{N}_k{k}_H{H}_sell", H, lambda i, N=N, k=k: -1 if zs(i, N) >= k else 0))
            trig.append((f"zfade_N{N}_k{k}_H{H}_buy", H, lambda i, N=N, k=k: 1 if zs(i, N) <= -k else 0))
for H in (16, 48):
    trig.append((f"stoch_fade_H{H}_sell", H, lambda i: -1 if k14[i] > 80 else 0))
    trig.append((f"stoch_fade_H{H}_buy", H, lambda i: 1 if k14[i] < 20 else 0))
    trig.append((f"zmomentum_N20_H{H}_sell", H, lambda i: -1 if zs(i, 20) <= -2 else 0))
    trig.append((f"zmomentum_N20_H{H}_buy", H, lambda i: 1 if zs(i, 20) >= 2 else 0))
spec = importlib.util.spec_from_file_location("al", os.path.join(DATA, "auto_loop.py"))
al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
idx = {datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d %H:%M"): i for i, t in enumerate(ep)}
base = {}
for y in ("2013", "2014", "2015", "2016", "2018", "2023", "2024"):
    p = os.path.join(HST, f"WIN_GEN1_{y}_sp5.htm")
    if os.path.exists(p):
        s = set()
        for t, _ in al.trades_from_report(p):
            i = idx.get(datetime.datetime.strptime(t, "%Y.%m.%d %H:%M").strftime("%Y-%m-%d %H:%M"))
            if i is not None: s.add(i // 96)    # base active in this ~day bucket
        base[int(y)] = s
stamp = f"{datetime.datetime.now():%Y-%m-%d %H:%M}"; ledger = os.path.join(DATA, "shadow_audit.csv"); new = not os.path.exists(ledger)
rows = []; summ = {}
for name, H, sig in trig:
    res = run(sig, H); ys = {}
    for i, x in res: ys.setdefault(yr[i], []).append((i, x))
    for y, v in sorted(ys.items()):
        comp = [x for i, x in v if y in base and (i // 96) not in base[y]]
        rows.append([stamp, name, y, len(v), round(sum(x for _, x in v), 1), round(sum(x for _, x in v) / len(v), 2),
                     (len(comp) if y in base else ""), (round(sum(comp) / len(comp), 2) if comp else "")])
    allx = [x for v in ys.values() for _, x in v]
    if allx: summ[name] = (len(allx), sum(allx) / len(allx), sum(sum(x for _, x in v) > 0 for v in ys.values()), len(ys))
with open(ledger, "a", newline="") as f:
    w = csv.writer(f)
    if new: w.writerow(["run", "trigger", "year", "n", "net_pts_total", "avg_net_pts", "n_when_base_flat", "avg_when_base_flat"])
    w.writerows(rows)
alts = sorted(summ.items(), key=lambda kv: -kv[1][1])
with open(os.path.join(DATA, "ALT_WIN_LOGIC.md"), "w") as f:
    f.write(f"# Alternative win logic (silent shadow audit, {stamp})\nNever blocked or pruned: every trigger is logged each run in shadow_audit.csv. Net of 5 pt commission + hourly spread; fixed H-bar exit, no stops/swap.\n\n")
    f.write("| trigger | trades | avg net pts | years positive |\n|---|---|---|---|\n")
    for k, (c, a, yp, yn) in alts: f.write(f"| {k} | {c} | {a:+.2f} | {yp}/{yn} |\n")
    f.write("\nWatch list = avg > 0 and positive in most years. Confirm only via MT4 tester + proof gate; replay is a lead, not a win.\n")
print(f"audit {stamp}: {len(trig)} triggers, {len(rows)} ledger rows")
for k, (c, a, yp, yn) in alts[:8]: print(f"{k:34} n={c:5d} avg={a:+6.2f} yrs+ {yp}/{yn}")
