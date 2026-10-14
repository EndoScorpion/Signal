"""entry_diagnosis.py - why are there no entries? (1) data check of the tester's M15/H1 history, (2) bar-by-bar re-simulation of the b51 entry chain
(z fade N10 >= k, H1 SMA regime, ATR cap, rollover hours, one position, time exit, stop) validated against MT4's own trade counts,
(3) funnel counts per filter and expectancy per simplified variant. Offline, read-only. Params default to g2_ZTrigger_2p25."""
import struct, math, datetime, bisect, ctypes, sys, os, re, importlib.util
from collections import defaultdict
class M(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong * 5)]
m = M(); m.l = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
if m.ap / 2**30 < 0.6 and "--force" not in sys.argv: raise SystemExit(f"skipped: {m.ap/2**30:.2f} GB free")
D = r"C:\Users\endos\Desktop\mt4_tester\history\FXOpenEU-ECN Live Server"
def rd(name):
    raw = open(os.path.join(D, name), "rb").read()[148:]; n = len(raw) // 60; T = []; O = []; H = []; L = []; C = []
    for k in range(n):
        t, o, h, l, c, tv, sp, rv = struct.unpack_from("<qddddqiq", raw, k * 60); T.append(t); O.append(o); H.append(h); L.append(l); C.append(c)
    return T, O, H, L, C
T, O, H, L, C = rd("EURUSD15.hst"); T1, O1, H1, L1, C1 = rd("EURUSD60.hst")
dt = lambda t: datetime.datetime.utcfromtimestamp(t)
print(f"M15: {len(T):,} bars, first {dt(T[0]):%Y-%m-%d %H:%M}, last {dt(T[-1]):%Y-%m-%d %H:%M} | H1: {len(T1):,} bars, first {dt(T1[0]):%Y-%m-%d %H:%M}")
cnt = defaultdict(int); cnt1 = defaultdict(int)
for t in T: d = dt(t); cnt[(d.year, d.month)] += 1
for t in T1: d = dt(t); cnt1[(d.year, d.month)] += 1
print("2010 M15 bars per month (full month ~1,900-2,000):", {mo: cnt[(2010, mo)] for mo in range(1, 13)})
print("2010 H1 bars per month  (full month ~  475-500):", {mo: cnt1[(2010, mo)] for mo in range(1, 13)})
cum = 0; first_ok = None
for k, t in enumerate(T1):
    if k + 1 >= 2400 and first_ok is None: first_ok = dt(t)
print(f"H1 SMA(2400) first has a full window at {first_ok:%Y-%m-%d}: before that the regime value is not valid, so sells are not allowed")
# series for the simulation
n = len(T); P1 = [0.0]; P2 = [0.0]
for c in C: P1.append(P1[-1] + c); P2.append(P2[-1] + c * c)
TR = [0.0] + [max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1])) for i in range(1, n)]
cs = [0.0]
for v in TR: cs.append(cs[-1] + v)
c1 = [0.0]
for v in C1: c1.append(c1[-1] + v)
SPR = 5.0
def regime_ok(t):
    j = bisect.bisect_right(T1, t - 3600) - 1
    if j < 2399: return None
    return C1[j] < (c1[j + 1] - c1[j - 2399]) / 2400
Kz, ZN, HOLD, SL, ATRC = 2.25, 10, 48, 600, 60
for a in sys.argv[1:]:
    if a.startswith("z="): Kz = float(a[2:])
def sim(use_reg, use_atr, use_hour, years=None):
    trades = []; i = 9700; stage = defaultdict(int); next_free = 0
    while i < n - HOLD - 2:
        t = T[i]; y = dt(t).year
        if years and y not in years: i += 1; continue
        k = i - 1   # last closed M15 bar
        mu = (P1[k + 1] - P1[k + 1 - ZN]) / ZN; v = (P2[k + 1] - P2[k + 1 - ZN]) / ZN - mu * mu
        z = (C[k] - mu) / math.sqrt(v) if v > 0 else 0
        ok = z >= Kz
        if ok: stage[(y, "z")] += 1
        r = regime_ok(t) if use_reg else True
        if ok and r is None: stage[(y, "regime_warmup")] += 1
        if ok and use_reg and not r: ok = False
        elif ok and r is not None: stage[(y, "z+regime")] += 1
        if ok and use_atr and (cs[k + 1] - cs[k + 1 - 14]) / 14 * 1e5 > ATRC: ok = False
        elif ok: stage[(y, "z+regime+atr")] += 1
        if ok and use_hour and 20 <= dt(t).hour <= 22: ok = False
        elif ok: stage[(y, "z+regime+atr+hour")] += 1
        if ok and i >= next_free and r is not None:
            e = O[i]; ex = O[i + HOLD]; pnl = (e - ex) * 1e5 - SPR; j = i
            for q in range(i, i + HOLD):   # stop check on bar highs (ask = bid + spread)
                if H[q] + SPR * 1e-5 >= e + SL * 1e-5: pnl = -SL - SPR; j = q; break
            trades.append((y, pnl, dt(t), i, j)); next_free = max(i + HOLD, j + 1); i = next_free
        else: i += 1
    return trades, stage
UNSEEN = {2010, 2013, 2014, 2015, 2016, 2018, 2023, 2024}
full, st = sim(True, True, True)
rep = {}
H_ = r"C:\Users\endos\Desktop\hst_out"
spec = importlib.util.spec_from_file_location("al", r"C:\Users\endos\Signal\data\auto_loop.py"); al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
for y in sorted(UNSEEN):
    p = os.path.join(H_, f"LOOP_g2_ZTrigger_2p25_{y}_sp5.htm")
    if os.path.exists(p): rep[y] = len(al.trades_from_report(p))
print(f"\nENTRY FUNNEL per year (z>={Kz}, N{ZN}, regime H1 SMA2400, ATR<={ATRC}, no hours 20-22): bars passing each stage, simulated trades vs MT4 trades")
print("year | z only | +regime | +ATR | +hour | regime warm-up skips | SIM trades (pts) | MT4 trades")
for y in sorted(UNSEEN):
    tr = [x for x in full if x[0] == y]
    print(f"{y} | {st[(y,'z')]:6d} | {st[(y,'z+regime')]:7d} | {st[(y,'z+regime+atr')]:4d} | {st[(y,'z+regime+atr+hour')]:5d} | {st[(y,'regime_warmup')]:6d} | {len(tr):3d} ({sum(x[1] for x in tr):+.0f}) | {rep.get(y,'-')}")
if "--detail" in sys.argv:
    print("\nDETAIL: simulated entries that MT4 did not take (sim-only) and outliers")
    for y in (2013, 2014, 2015, 2016, 2024):
        p = os.path.join(H_, f"LOOP_g2_ZTrigger_2p25_{y}_sp5.htm")
        mt = {datetime.datetime.strptime(t, "%Y.%m.%d %H:%M").strftime("%m-%d") for t, _ in al.trades_from_report(p)} if os.path.exists(p) else set()
        sim_tr = [x for x in full if x[0] == y]
        only = [x for x in sim_tr if x[2].strftime("%m-%d") not in mt]
        print(f"{y}: sim {len(sim_tr)} MT4 {len(mt)} | sim-only dates: " + ", ".join(f"{x[2]:%m-%d %H:%M}({x[1]:+.0f})" for x in only))
    for x in full:
        if abs(x[1]) > 700 or (T[x[3] + HOLD] - T[x[3]]) > HOLD * 900 * 1.5:
            i = x[3]; print(f"OUTLIER {x[2]:%Y-%m-%d %H:%M}: pnl {x[1]:+.0f} pts, open {O[i]:.5f}, exit-bar open {O[i+HOLD]:.5f}, hours between {((T[i+HOLD]-T[i])/3600):.1f}, window hi {max(H[i:i+HOLD]):.5f} lo {min(L[i:i+HOLD]):.5f}")
print("\n2010 simulated entries by month:", {f'{x[2]:%b}': round(x[1]) for x in full if x[0] == 2010})
print("\nSIMPLIFIED VARIANTS over the 8 unseen years (non-overlapping, same exit/stop, cost 5 pts): trades | total pts | pts per trade | win%")
for name, a in (("z only", (False, False, False)), ("z + regime", (True, False, False)), ("z + ATR cap", (False, True, False)), ("z + hours", (False, False, True)), ("z + regime + ATR", (True, True, False)), ("FULL (regime+ATR+hours)", (True, True, True))):
    tr, _ = sim(*a, years=UNSEEN)
    if tr: print(f"{name:26} {len(tr):5d} | {sum(x[1] for x in tr):+9.0f} | {sum(x[1] for x in tr)/len(tr):+7.1f} | {100*sum(1 for x in tr if x[1]>0)/len(tr):4.1f}")
