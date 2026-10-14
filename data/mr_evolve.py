"""mr_evolve.py - clone + mutate mean-reversion genomes over generations (offline, net of cost, no MT4).
Genome: N (z lookback), k (z trigger), H (hold bars), side, atr_cap (skip entries when ATR14 pts above cap), skip_nfp.
Fitness uses IS (2010-2017) only: avg net pts/trade, scaled by share of positive IS years. OOS (2018-2026) is reported, never selected on.
Cost excludes swap and stops (long holds) - results are leads for the MT4 tester. Run: python -I data/mr_evolve.py [cost] [gens]
Concepts (c) Nasif Hossain."""
import os, csv, sys, math, random, datetime, json
DATA = r"C:\Users\endos\Signal\data"
COST = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0; GENS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
ep, cl, atr, yr, nfp = [], [], [], [], []
for r in csv.DictReader(open(os.path.join(DATA, "m15_metrics.csv"))):
    t = int(r["ts"]); d = datetime.datetime.utcfromtimestamp(t)
    ep.append(t); cl.append(float(r["close"])); atr.append(float(r["atr14_pts"])); yr.append(d.year); nfp.append(d.weekday() == 4 and d.day <= 7)
n = len(cl); P1 = [0.0]; P2 = [0.0]
for c in cl: P1.append(P1[-1] + c); P2.append(P2[-1] + c * c)
def run(g):
    N, k, H, side, cap, sk = g; res = []; i = N + 1
    while i < n - H:
        m = (P1[i + 1] - P1[i + 1 - N]) / N; v = (P2[i + 1] - P2[i + 1 - N]) / N - m * m
        if v > 0 and not (sk and nfp[i]) and not (cap and atr[i] > cap) and ep[i + H] - ep[i] <= H * 900 * 1.25:
            z = (cl[i] - m) / math.sqrt(v); d = 0
            if z >= k and side != "buy": d = -1
            elif z <= -k and side != "sell": d = 1
            if d: res.append((yr[i], d * (cl[i + H] - cl[i]) * 1e5 - COST)); i += H; continue
        i += 1
    return res
def evaluate(g):
    rs = run(g); IS = [x for y, x in rs if y <= 2017]; OO = [x for y, x in rs if y >= 2018]
    ys = {}
    for y, x in rs:
        if y <= 2017: ys.setdefault(y, []).append(x)
    posshare = sum(sum(v) > 0 for v in ys.values()) / max(len(ys), 1)
    a = sum(IS) / len(IS) if IS else -99; b = sum(OO) / len(OO) if OO else -99
    fit = a * posshare if len(IS) >= 300 else -99
    return {"g": g, "fit": fit, "is": a, "n_is": len(IS), "oos": b, "n_oos": len(OO), "yrs+": round(posshare, 2)}
def mutate(g, rnd):
    N, k, H, side, cap, sk = g
    c = rnd.randint(0, 5)
    if c == 0: N = rnd.choice([8, 10, 14, 20, 30, 50, 70])
    elif c == 1: k = round(min(3.0, max(0.75, k + rnd.choice([-0.5, -0.25, 0.25, 0.5]))), 2)
    elif c == 2: H = rnd.choice([24, 32, 48, 64, 96])
    elif c == 3: side = rnd.choice(["both", "sell", "buy"])
    elif c == 4: cap = rnd.choice([None, 60, 90, 130])
    else: sk = not sk
    return (N, k, H, side, cap, sk)
rnd = random.Random(13)
seeds = [(10, 2.5, 48, "sell", None, False), (10, 2.0, 48, "sell", None, False), (50, 1.0, 48, "both", None, False),
         (20, 1.0, 48, "both", None, False), (20, 2.0, 48, "both", None, False), (10, 2.5, 48, "both", None, False)]
pop = [evaluate(g) for g in seeds]; seen = {tuple(p["g"]) for p in pop}; hist = []
def show(tag, ps):
    print(f"\n{tag}: genome (N,k,H,side,atr_cap,skip_nfp) | IS n avg | OOS n avg | IS yrs+ ")
    for p in ps: print(f"  {p['g']} | {p['n_is']:5d} {p['is']:+6.2f} | {p['n_oos']:5d} {p['oos']:+6.2f} | {p['yrs+']}")
show("Gen0 seeds", sorted(pop, key=lambda p: -p["fit"])[:5])
for gen in range(1, GENS + 1):
    top = sorted(pop, key=lambda p: -p["fit"])[:5]; kids = []
    for p in top:
        for _ in range(4):
            g = mutate(p["g"], rnd)
            if rnd.random() < .4: g = mutate(g, rnd)
            if tuple(g) in seen: continue
            seen.add(tuple(g)); kids.append(evaluate(g))
    pop = top + kids; hist.append(sorted(pop, key=lambda p: -p["fit"])[:5])
    show(f"Gen{gen} top 5 (cloned from top 5, {len(kids)} new children)", hist[-1])
best = max((p for h in hist for p in h), key=lambda p: p["fit"])
json.dump([[p["g"], p["fit"], p["is"], p["oos"]] for p in hist[-1]], open(os.path.join(DATA, "mr_evolve_last.json"), "w"))
print("\nBest by IS fitness:", best["g"], f"IS {best['is']:+.2f}  OOS {best['oos']:+.2f} (OOS never used for selection)")
