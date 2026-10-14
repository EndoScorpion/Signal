"""alt_corr.py - alternative correlations: pairwise tercile interactions and ratios (smoothness vs volatility etc.) of base-EA sell entries.
Features per entry (M15, bar before entry): atr14, atr_ratio(14/100), vol_of_vol, rvol20, er10 (smoothness), katz FD, perm entropy, hurst, range20,
williams %R, ema8 accel, smooth_per_vol (er10 / atr14). Cells = tercile pairs. A cell 'passes' if >=4 of the years with n>=12 have the same sign of
(cell avg - year avg) and the mean |delta| >= 8 pts. Shuffle null (pnl permuted within year) estimates how many cells pass by luck.
Offline lead, not proof. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>."""
import os, struct, math, datetime, importlib.util, ctypes, sys, random, itertools
from collections import defaultdict
class M(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong * 5)]
m = M(); m.l = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
if m.ap / 2**30 < 0.8 and "--force" not in sys.argv: raise SystemExit(f"skipped: {m.ap/2**30:.2f} GB free")
DATA = r"C:\Users\endos\Signal\data"; HST = r"C:\Users\endos\Desktop\hst_out"
spec = importlib.util.spec_from_file_location("al", os.path.join(DATA, "auto_loop.py"))
al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
raw = open(r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD15.hst", "rb").read()[148:]
n = len(raw) // 60; T, Hh, Ll, Cc = [], [], [], []
for k in range(n):
    t, o, h, l, c, tv, sp, rv = struct.unpack_from("<qddddqiq", raw, k * 60); T.append(t); Hh.append(h); Ll.append(l); Cc.append(c)
del raw
idx = {datetime.datetime.utcfromtimestamp(t).strftime("%Y.%m.%d %H:%M"): i for i, t in enumerate(T)}
TR = [0.0] + [max(Hh[i] - Ll[i], abs(Hh[i] - Cc[i - 1]), abs(Ll[i] - Cc[i - 1])) for i in range(1, n)]
cs = [0.0]
for v in TR: cs.append(cs[-1] + v)
def atr(i, p): return (cs[i + 1] - cs[i + 1 - p]) / p * 1e5
def ema(a, p):
    k = 2 / (p + 1); out = [a[0]] * len(a)
    for i in range(1, len(a)): out[i] = out[i - 1] + k * (a[i] - out[i - 1])
    return out
e8 = ema(Cc, 8)
def hurst(i, win=128):
    r = [math.log(Cc[j] / Cc[j - 1]) for j in range(i - win + 1, i + 1)]; pts = []
    for ms in (8, 16, 32, 64):
        k = len(r) // ms; rs = []
        for c in range(k):
            ch = r[c * ms:(c + 1) * ms]; mu = sum(ch) / ms; y = 0; ys = []
            for v in ch: y += v - mu; ys.append(y)
            sd = math.sqrt(sum((v - mu) ** 2 for v in ch) / ms)
            if sd > 0: rs.append((max(ys) - min(ys)) / sd)
        if rs: pts.append((math.log(ms), math.log(sum(rs) / len(rs))))
    if len(pts) < 3: return None
    mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
    return sum((p[0] - mx) * (p[1] - my) for p in pts) / sum((p[0] - mx) ** 2 for p in pts)
def katz(i, N=50):
    w = Cc[i - N:i + 1]; L = sum(abs(w[j] - w[j - 1]) for j in range(1, len(w))); d = max(abs(v - w[0]) for v in w)
    return math.log10(N) / (math.log10(N) + math.log10(d / L)) if L > 0 and d > 0 else None
def pe(i, win=64, order=3):
    cnt = defaultdict(int); tot = 0
    for j in range(i - win + 1, i - order + 2):
        cnt[tuple(sorted(range(order), key=lambda q: Cc[j + q]))] += 1; tot += 1
    return -sum(v / tot * math.log(v / tot) for v in cnt.values()) / math.log(6)
def feats(i):
    a14, a100 = atr(i, 14), atr(i, 100)
    rets = [(Cc[j] - Cc[j - 1]) * 1e5 for j in range(i - 19, i + 1)]; mu = sum(rets) / 20
    path = sum(abs(Cc[j] - Cc[j - 1]) for j in range(i - 9, i + 1)); er = abs(Cc[i] - Cc[i - 10]) / path if path > 0 else 0
    atrs = [atr(j, 14) for j in range(i - 49, i + 1, 5)]; ma = sum(atrs) / len(atrs)
    hh = max(Hh[i - 13:i + 1]); ll = min(Ll[i - 13:i + 1])
    f = {"atr14": a14, "atr_ratio": a14 / a100 if a100 else None, "vol_of_vol": math.sqrt(sum((v - ma) ** 2 for v in atrs) / len(atrs)) / ma if ma else None,
         "rvol20": math.sqrt(sum((v - mu) ** 2 for v in rets) / 20), "er10_smooth": er, "katz_fd": katz(i), "perm_entropy": pe(i), "hurst": hurst(i),
         "range20": (max(Cc[i - 19:i + 1]) - min(Cc[i - 19:i + 1])) * 1e5, "williams_r": -100 * (hh - Cc[i]) / (hh - ll) if hh > ll else None,
         "ema8_accel": ((e8[i] - e8[i - 1]) - (e8[i - 1] - e8[i - 2])) * 1e5}
    f["smooth_per_vol"] = er / a14 * 100 if a14 else None
    return f
YEARS = ("2015", "2016", "2018", "2023", "2024"); rows = defaultdict(list)
for y in YEARS:
    p = os.path.join(HST, f"WIN_GEN1_{y}_sp5.htm")
    if not os.path.exists(p): continue
    for t, pnl in al.trades_from_report(p):
        d0 = datetime.datetime.strptime(t, "%Y.%m.%d %H:%M"); i = idx.get((d0 - datetime.timedelta(minutes=15 + d0.minute % 15)).strftime("%Y.%m.%d %H:%M"))
        if i is None or i < 300: continue
        f = feats(i)
        if all(v is not None for v in f.values()): rows[y].append((f, pnl))
names = list(next(iter(rows.values()))[0][0]); allr = [r for v in rows.values() for r in v]
cut = {}
for k in names:
    s = sorted(r[0][k] for r in allr); cut[k] = (s[len(s) // 3], s[2 * len(s) // 3])
if "--cuts" in sys.argv:
    for k in names: print(f"{k:16} low<={cut[k][0]:.5g}  high>{cut[k][1]:.5g}")
    raise SystemExit
def tb(k, v): return 0 if v <= cut[k][0] else (1 if v <= cut[k][1] else 2)
data = {y: [([tb(k, f[k]) for k in names], p) for f, p in rows[y]] for y in rows}
ys = sorted(data); yavg = {y: sum(p for _, p in data[y]) / len(data[y]) for y in ys}
def scan(dat, pnl_override=None):
    res = []
    for a, b in itertools.combinations(range(len(names)), 2):
        for ba in range(3):
            for bb in range(3):
                dl = []; tot = 0
                for y in ys:
                    cell = [(p if pnl_override is None else pnl_override[y][j]) for j, (bk, p) in enumerate(dat[y]) if bk[a] == ba and bk[b] == bb]
                    if len(cell) >= 12:
                        ya = sum((p if pnl_override is None else pnl_override[y][j]) for j, (bk, p) in enumerate(dat[y])) / len(dat[y])
                        dl.append(sum(cell) / len(cell) - ya); tot += len(cell)
                if len(dl) >= 4 and abs(sum(1 if v > 0 else -1 for v in dl)) >= len(dl) - 1 and abs(sum(dl) / len(dl)) >= 8:
                    res.append((sum(dl) / len(dl), names[a], ba, names[b], bb, tot, dl))
    return res
real = scan(data)
null = []
rnd = random.Random(7)
for _ in range(40):
    sh = {y: [p for _, p in data[y]] for y in ys}
    for y in ys: rnd.shuffle(sh[y])
    null.append(len(scan(data, sh)))
lab = ["low", "mid", "high"]
print("features:", names); print("trades per year:", {y: len(data[y]) for y in ys}, "| year avg pnl/trade:", {y: round(yavg[y], 1) for y in ys})
print(f"\ncells passing the consistency test: {len(real)} | shuffled-null average {sum(null)/len(null):.1f} (max {max(null)}) over 40 shuffles")
print("best cells: mean delta vs year avg (pts/trade) | pair | n | per-year deltas")
for d, a, ba, b, bb, tot, dl in sorted(real, key=lambda r: -abs(r[0]))[:14]:
    print(f"{d:+7.1f} | {a}={lab[ba]} & {b}={lab[bb]} | n={tot} | " + " ".join(f"{v:+.0f}" for v in dl))
