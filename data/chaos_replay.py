"""chaos_replay.py - deconstruct base-EA sell entries with Bill Williams (%R, fractals, Alligator), chaos/complexity (Hurst R/S,
Katz fractal dimension, permutation entropy) and calculus (EMA velocity/acceleration phase-space quadrant). Offline, no MT4.
For each unseen year with base reports (2015, 2016, 2018, 2023, 2024; 2013/14 have too few trades): avg pnl/trade by feature bucket.
A pattern counts as consistent only if it has the same sign vs the all-trade average in >= 4 of the 5 years. Lead, not proof.
Williams indicators are Bill Williams' public work; MMR/slope concepts (c) Nasif Hossain <EndoScorpion@gmail.com>."""
import os, struct, math, datetime, importlib.util, ctypes, sys
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
med = [(Hh[i] + Ll[i]) / 2 for i in range(n)]
def smma(a, p):
    out = [a[0]] * len(a)
    for i in range(1, len(a)): out[i] = (out[i - 1] * (p - 1) + a[i]) / p
    return out
jaw, teeth, lips = smma(med, 13), smma(med, 8), smma(med, 5)
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
def perm_entropy(i, win=64, order=3):
    cnt = defaultdict(int); tot = 0
    for j in range(i - win + 1, i - order + 2):
        pat = tuple(sorted(range(order), key=lambda q: Cc[j + q])); cnt[pat] += 1; tot += 1
    return -sum(v / tot * math.log(v / tot) for v in cnt.values()) / math.log(6) if tot else None
def feats(i):
    f = {}
    hh = max(Hh[i - 13:i + 1]); ll = min(Ll[i - 13:i + 1]); f["williams %R(14)"] = -100 * (hh - Cc[i]) / (hh - ll) if hh > ll else None
    a, b, c3 = lips[i - 3], teeth[i - 5], jaw[i - 8]; spr = (max(a, b, c3) - min(a, b, c3)) * 1e5
    f["alligator"] = "asleep (<15pt)" if spr < 15 else ("awake down" if a < b < c3 else ("awake up" if a > b > c3 else "mixed"))
    up = dn = None
    for j in range(i - 2, i - 202, -1):
        if up is None and Hh[j] > max(Hh[j - 2], Hh[j - 1], Hh[j + 1], Hh[j + 2]): up = Hh[j]
        if dn is None and Ll[j] < min(Ll[j - 2], Ll[j - 1], Ll[j + 1], Ll[j + 2]): dn = Ll[j]
        if up is not None and dn is not None: break
    if up is not None and dn is not None:
        f["fractal position"] = "below last down-fractal" if Cc[i] < dn else ("above last up-fractal" if Cc[i] > up else "between fractals")
    f["hurst(128)"] = hurst(i); f["katz FD(50)"] = katz(i); f["perm entropy(64)"] = perm_entropy(i)
    v = (e8[i] - e8[i - 1]) * 1e5; acc = v - (e8[i - 1] - e8[i - 2]) * 1e5
    f["phase quadrant (EMA8 v,a)"] = ("up" if v > 0 else "down") + "/" + ("accelerating" if (v > 0) == (acc > 0) else "decelerating")
    return f
rows = {}
for y in ("2015", "2016", "2018", "2023", "2024"):
    p = os.path.join(HST, f"WIN_GEN1_{y}_sp5.htm")
    if not os.path.exists(p): continue
    for t, pnl in al.trades_from_report(p):
        i = idx.get((datetime.datetime.strptime(t, "%Y.%m.%d %H:%M") - datetime.timedelta(minutes=15 + datetime.datetime.strptime(t, "%Y.%m.%d %H:%M").minute % 15)).strftime("%Y.%m.%d %H:%M"))
        if i is None or i < 300: continue
        f = feats(i)
        if all(v is not None for v in f.values()): rows.setdefault(y, []).append((f, pnl))
allf = [r for v in rows.values() for r in v]
cuts = {}
for k in ("williams %R(14)", "hurst(128)", "katz FD(50)", "perm entropy(64)"):
    s = sorted(r[0][k] for r in allf); cuts[k] = (s[len(s) // 3], s[2 * len(s) // 3])
def bucket(k, v):
    if k in cuts: lo, hi = cuts[k]; return f"low (<{lo:.2f})" if v <= lo else (f"high (>{hi:.2f})" if v > hi else "mid")
    return v
ys = sorted(rows); avg = {y: sum(p for _, p in rows[y]) / len(rows[y]) for y in ys}
print("years:", ys, "trades:", {y: len(rows[y]) for y in ys}, "| all-trade avg pnl/trade:", {y: round(avg[y], 1) for y in ys})
for k in allf[0][0]:
    print(f"\n{k} (avg pnl/trade [n]) -> delta vs year avg; * = same sign in >=4/5 years")
    bs = sorted({bucket(k, r[0][k]) for r in allf})
    for b in bs:
        cells, signs = [], []
        for y in ys:
            rr = [p for f, p in rows[y] if bucket(k, f[k]) == b]
            if rr: a = sum(rr) / len(rr); cells.append(f"{a:+7.1f}[{len(rr):3d}]"); signs.append(1 if a > avg[y] else -1)
            else: cells.append("      -    ")
        cons = len(signs) >= 4 and abs(sum(signs)) >= 4
        print(f"  {b:26} " + " ".join(cells) + ("   * better" if cons and sum(signs) > 0 else ("   * worse" if cons else "")))
