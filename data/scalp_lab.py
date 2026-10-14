"""
TIME NOTE: SPR hour keys are UTC hours (CSV clock) while the M15 .hst used here carries a mixed (patchwork) clock; the 20-22 rollover exclusion is approximate. Redo on the clean history (mt4_tester2, server clock UTC+2/+3 US DST).
scalp_lab.py - can 7-10 pt targets pay after a 5 pt commission + hourly spread? Offline, M15 high/low (conservative: stop checked before target
inside a bar). Entry = next bar open. Signals: z-fade (N10, |z|>=2 / 2.5), optionally in calm tape (rvol20<=29.6 & perm entropy<=0.945), and an
unconditional baseline. Cost per trade = 5 pts + mean spread of that server hour (2023-26). Hit rate needed to break even is printed next to
the achieved one. Lead only: real scalping needs tick data and the MT4 tester. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>."""
import struct, math, datetime, ctypes, sys
from collections import defaultdict
class M(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong * 5)]
m = M(); m.l = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
if m.ap / 2**30 < 0.8 and "--force" not in sys.argv: raise SystemExit(f"skipped: {m.ap/2**30:.2f} GB free")
raw = open(r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD15.hst", "rb").read()[148:]
n = len(raw) // 60; T, O, H, L, C = [], [], [], [], []
for k in range(n):
    t, o, h, l, c, tv, sp, rv = struct.unpack_from("<qddddqiq", raw, k * 60); T.append(t); O.append(o); H.append(h); L.append(l); C.append(c)
del raw
SPR = {0: 1.3, 1: 1.2, 2: 1.2, 3: 1.1, 4: 1.1, 5: 1.2, 6: 1.1, 7: 1.1, 8: 1.0, 9: 1.0, 10: 0.9, 11: 0.9, 12: 1.1, 13: 1.1, 14: 1.0, 15: 0.9, 16: 1.0, 17: 1.1, 18: 1.1, 19: 1.1, 20: 2.5, 21: 17.1, 22: 7.7, 23: 1.6}
HR = [datetime.datetime.utcfromtimestamp(t).hour for t in T]; YR = [datetime.datetime.utcfromtimestamp(t).year for t in T]
P1 = [0.0]; P2 = [0.0]; R1 = [0.0]; R2 = [0.0]
for i in range(n):
    P1.append(P1[-1] + C[i]); P2.append(P2[-1] + C[i] * C[i]); r = (C[i] - C[i - 1]) * 1e5 if i else 0.0; R1.append(R1[-1] + r); R2.append(R2[-1] + r * r)
def z10(i):
    mu = (P1[i + 1] - P1[i - 9]) / 10; v = (P2[i + 1] - P2[i - 9]) / 10 - mu * mu
    return (C[i] - mu) / math.sqrt(v) if v > 0 else 0.0
def rvol(i):
    mu = (R1[i + 1] - R1[i - 19]) / 20; return math.sqrt(max(0.0, (R2[i + 1] - R2[i - 19]) / 20 - mu * mu))
def pent(i, win=64):
    cnt = defaultdict(int); tot = 0
    for j in range(i - win + 1, i - 1):
        cnt[tuple(sorted(range(3), key=lambda q: C[j + q]))] += 1; tot += 1
    return -sum(v / tot * math.log(v / tot) for v in cnt.values()) / math.log(6)
K = 8
def sim(i, d, tp, sl):
    e = O[i + 1]; cost = 5 + SPR[HR[i + 1]]
    for j in range(i + 1, i + 1 + K):
        if d > 0:
            if L[j] <= e - sl * 1e-5: return -sl - cost, 0
            if H[j] >= e + tp * 1e-5: return tp - cost, 1
        else:
            if H[j] >= e + sl * 1e-5: return -sl - cost, 0
            if L[j] <= e - tp * 1e-5: return tp - cost, 1
    return (C[i + K] - e) * 1e5 * d - cost, 0
sig = {"fade z>=2": [], "fade z>=2 calm": [], "fade z>=2.5": [], "fade z>=2.5 calm": [], "baseline long": [], "baseline short": []}
for i in range(120, n - K - 2):
    if HR[i + 1] in (20, 21, 22) or T[i + K] - T[i] > K * 900 * 1.25: continue
    z = z10(i)
    if abs(z) >= 2:
        d = -1 if z > 0 else 1
        sig["fade z>=2"].append((i, d))
        calm = rvol(i) <= 29.6 and pent(i) <= 0.9452
        if calm: sig["fade z>=2 calm"].append((i, d))
        if abs(z) >= 2.5:
            sig["fade z>=2.5"].append((i, d))
            if calm: sig["fade z>=2.5 calm"].append((i, d))
    if i % 8 == 0: sig["baseline long"].append((i, 1)); sig["baseline short"].append((i, -1))
out = []
for name, lst in sig.items():
    for tp in (7, 10, 12, 15, 20, 30, 40):
        for sl in (10, 15, 20, 30, 50, 100):
            res = [(sim(i, d, tp, sl), YR[i]) for i, d in lst]
            if len(res) < 200: continue
            net = sum(r[0][0] for r in res) / len(res); hit = sum(r[0][1] for r in res) / len(res)
            yrs = defaultdict(float)
            for r in res: yrs[r[1]] += r[0][0]
            cost = 5 + 1.4; be = (sl + cost) / (tp + sl)
            out.append((net, name, tp, sl, len(res), hit, be, sum(1 for v in yrs.values() if v > 0), len(yrs)))
out.sort(reverse=True)
print("rank by avg net pts/trade (after 5 pt commission + hourly spread). hit = target reached before stop within 8 bars (2 h)")
print("signal | TP/SL | n | hit% | break-even hit% | avg net | years positive")
for net, name, tp, sl, nn, hit, be, yp, yn in out[:12]:
    print(f"{name:18} | {tp}/{sl} | {nn:6d} | {100*hit:5.1f} | {100*be:5.1f} | {net:+6.2f} | {yp}/{yn}")
print("\nworst for reference:", [(o[1], f"{o[2]}/{o[3]}", round(o[0], 2)) for o in out[-3:]])
