"""mr_lab.py - mean-reversion trigger lab on EURUSD M15 closes, net of cost (default 5 pts round trip).
Signal: z = (close - mean_N) / std_N. Fade: sell when z >= k, buy when z <= -k. Exit after H bars. Non-overlapping trades.
Selection on IS (2010-2017) only; the same cell is then reported on OOS (2018-2026). Edge must be positive in both and in most years.
Offline, no MT4. Run: python -I data/mr_lab.py [cost_pts]. Concepts (c) Nasif Hossain."""
import os, csv, sys, math
DATA = r"C:\Users\endos\Signal\data"; COST = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
ep, cl = [], []
for r in csv.DictReader(open(os.path.join(DATA, "m15_metrics.csv"))):
    ep.append(int(r["ts"])); cl.append(float(r["close"]))
n = len(cl); yr = [int(r["dt"][:4]) if False else 0 for r in ()]  # placeholder
import datetime
yr = [datetime.datetime.utcfromtimestamp(t).year for t in ep]
P1 = [0.0]; P2 = [0.0]
for c in cl: P1.append(P1[-1] + c); P2.append(P2[-1] + c * c)
def run(N, k, H, side):
    res = []; i = N + 1
    while i < n - H:
        m = (P1[i + 1] - P1[i + 1 - N]) / N; v = (P2[i + 1] - P2[i + 1 - N]) / N - m * m
        if v > 0:
            z = (cl[i] - m) / math.sqrt(v)
            if ep[i + H] - ep[i] <= H * 900 * 1.25:
                d = 0
                if z >= k and side in ("both", "sell"): d = -1
                elif z <= -k and side in ("both", "buy"): d = 1
                if d:
                    res.append((yr[i], d * (cl[i + H] - cl[i]) * 1e5 - COST)); i += H; continue
        i += 1
    return res
def stats(rs):
    if not rs: return (0, 0.0)
    return (len(rs), sum(x for _, x in rs) / len(rs))
rows = []
for N in (10, 20, 50, 100):
    for k in (1.0, 1.5, 2.0, 2.5):
        for H in (4, 16, 48):
            for side in ("both", "sell"):
                rs = run(N, k, H, side)
                IS = [r for r in rs if r[0] <= 2017]; OO = [r for r in rs if r[0] >= 2018]
                ys = {}
                for y, x in rs: ys.setdefault(y, []).append(x)
                pos = sum(1 for v in ys.values() if sum(v) > 0)
                rows.append((N, k, H, side, stats(IS), stats(OO), pos, len(ys)))
rows.sort(key=lambda r: -r[4][1])
print(f"cost {COST} pts. Ranked by IS avg net pts/trade; OOS shown. cols: N k H side | IS n avg | OOS n avg | yrs+/yrs")
for r in rows[:12]:
    print(f"N{r[0]} k{r[1]} H{r[2]} {r[3]:4}| IS {r[4][0]:5d} {r[4][1]:+6.2f} | OOS {r[5][0]:5d} {r[5][1]:+6.2f} | {r[6]}/{r[7]}")
surv = [r for r in rows if r[4][1] > 0 and r[5][1] > 0]
print(f"\ncells positive in BOTH IS and OOS: {len(surv)} of {len(rows)}")
for r in sorted(surv, key=lambda r: -(r[4][1] + r[5][1]))[:8]:
    print(f"N{r[0]} k{r[1]} H{r[2]} {r[3]:4}| IS {r[4][0]:5d} {r[4][1]:+6.2f} | OOS {r[5][0]:5d} {r[5][1]:+6.2f} | {r[6]}/{r[7]}")
