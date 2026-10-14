"""market_patterns.py - per-year tracker of SMA/EMA slope patterns and Fibonacci retracements on EURUSD M15 (offline, derived data only).
SMA/EMA 20 and 50: mean slope, mean |slope| (pts/bar), fast-vs-slow slope agreement; zigzag swings (3x ATR14 threshold) and the share of
retracements landing near 0.382 / 0.5 / 0.618 (+-0.04). Joined with base per-year result from loop_state.json.
Output: data/MARKET_PATTERNS.md (overwritten each run). Run: python -I data/market_patterns.py
Backtest leads only, never live approval."""
import struct, json, os, math, datetime
from collections import defaultdict
HST = r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD15.hst"
D = r"C:\Users\endos\Signal\data"; LOT = 0.16; BAR = 60
data = open(HST, "rb").read()[148:]
n = len(data) // BAR
T, H, L, C = [], [], [], []
for i in range(n):
    t, o, h, l, c, tv, sp, rv = struct.unpack_from("<qddddqiq", data, i * BAR)
    T.append(t); H.append(h); L.append(l); C.append(c)
def year(t): return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).year
def ema(vals, p):
    k = 2 / (p + 1); e = vals[0]; out = [e]
    for v in vals[1:]:
        e = v * k + e * (1 - k); out.append(e)
    return out
def sma(vals, p):
    out = [None] * len(vals); s = 0.0
    for i, v in enumerate(vals):
        s += v
        if i >= p: s -= vals[i - p]
        if i >= p - 1: out[i] = s / p
    return out
lines = {"SMA20": sma(C, 20), "SMA50": sma(C, 50), "EMA20": ema(C, 20), "EMA50": ema(C, 50)}
st = defaultdict(lambda: defaultdict(lambda: [0, 0.0, 0.0, 0.0]))  # year -> line -> n, sum slope, sum |slope|, sum slope^2
cd = defaultdict(lambda: [0, 0, 0, 0.0, 0.0, 0.0])  # year -> n, converging, diverging, sum d, sum d^2, prev|d| (SMA20-SMA50 slope gap)
prevgap = None
agree = defaultdict(lambda: [0, 0])
for i in range(60, n):
    y = year(T[i]); sl = {}
    for k, v in lines.items():
        if v[i] is None or v[i - 1] is None: break
        s = (v[i] - v[i - 1]) * 100000; sl[k] = s
        a = st[y][k]; a[0] += 1; a[1] += s; a[2] += abs(s); a[3] += s * s
    else:
        gap = sl['SMA20'] - sl['SMA50']; c = cd[y]; c[0] += 1; c[3] += gap; c[4] += gap * gap
        if prevgap is not None:
            if abs(gap) < prevgap: c[1] += 1
            elif abs(gap) > prevgap: c[2] += 1
        prevgap = abs(gap)
        for fast, slow in (("SMA20", "SMA50"), ("EMA20", "EMA50")):
            agree[y][1] += 1
            if sl[fast] * sl[slow] > 0: agree[y][0] += 1
mr = defaultdict(lambda: [0, 0, 0.0, 0.0, 0.0])  # year -> events, reverted(48 bars), sum fade pts, gross win, gross loss
ac = defaultdict(lambda: [0, 0.0, 0.0, 0.0])  # year -> n, sum r1*r0, sum r0^2 (lag1 autocorr of M15 returns)
for i in range(60, n - 49):
    w = C[i - 9:i + 1]; m = sum(w) / 10; sd = math.sqrt(sum((x - m) ** 2 for x in w) / 10)
    y = year(T[i]); r0 = C[i] - C[i - 1]; r1 = C[i + 1] - C[i]
    a = ac[y]; a[0] += 1; a[1] += r0 * r1; a[2] += r0 * r0
    if sd == 0: continue
    z = (C[i] - m) / sd
    if abs(z) >= 2.25:
        side = -1 if z > 0 else 1; fade = side * (C[i + 48] - C[i]) * 100000
        e = mr[y]; e[0] += 1; e[2] += fade
        if fade > 0: e[1] += 1; e[3] += fade
        else: e[4] += -fade
atr = []
for i in range(n):
    tr = H[i] - L[i] if i == 0 else max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1]))
    atr.append(tr)
fib = defaultdict(lambda: [0, 0, 0, 0, 0.0])  # year -> swings, ~0.382, ~0.5, ~0.618, sum ratio
pv, pi, d = C[0], 0, 0; sw = []
for i in range(14, n):
    a = sum(atr[i - 13:i + 1]) / 14 * 3
    if d >= 0:
        if H[i] > pv: pv, pi = H[i], i
        elif pv - L[i] > a: sw.append((pi, pv)); d, pv, pi = -1, L[i], i
    if d <= 0:
        if d == 0 and L[i] < pv: pv, pi = L[i], i
        elif d == -1 and L[i] < pv: pv, pi = L[i], i
        elif d == -1 and H[i] - pv > a: sw.append((pi, pv)); d, pv, pi = 1, H[i], i
    if d == 0 and H[i] - L[i] > a: d = 1 if C[i] > C[i - 1] else -1
for k in range(2, len(sw)):
    a, b, c = sw[k - 2][1], sw[k - 1][1], sw[k][1]
    if abs(b - a) < 1e-9: continue
    r = abs(c - b) / abs(b - a); f = fib[year(T[sw[k][0]])]
    f[0] += 1; f[4] += r
    for j, lv in enumerate((0.382, 0.5, 0.618)):
        if abs(r - lv) <= 0.04: f[1 + j] += 1
s = json.load(open(os.path.join(D, "loop_state.json"))); base = s.get("base_real") or s.get("base") or {}
def bp(y):
    v = base.get(str(y)); return "" if v is None else str(round((v["profit"] if isinstance(v, dict) else v) / LOT))
out = ["# Market patterns by year (auto-generated, EURUSD M15)", "",
       "Slopes in pts/bar. Agree = share of bars where fast and slow slopes have the same sign (convergence).", "",
       "| Year | SMA20 mean | SMA20 abs | SMA50 abs | EMA20 mean | EMA20 abs | EMA50 abs | Agree % | Base pts |", "|---|---|---|---|---|---|---|---|---|"]
for y in sorted(st):
    g = lambda k, j: st[y][k][j] / max(1, st[y][k][0])
    ag = 100 * agree[y][0] / max(1, agree[y][1])
    out.append(f"| {y} | {g('SMA20',1):.2f} | {g('SMA20',2):.2f} | {g('SMA50',2):.2f} | {g('EMA20',1):.2f} | {g('EMA20',2):.2f} | {g('EMA50',2):.2f} | {ag:.1f} | {bp(y)} |")
out += ["", "## Fibonacci retracements (zigzag 3x ATR14)", "", "| Year | Swings | mean retrace | near 0.382 % | near 0.5 % | near 0.618 % | Base pts |", "|---|---|---|---|---|---|---|"]
for y in sorted(fib):
    f = fib[y]
    if f[0] < 5: continue
    out.append(f"| {y} | {f[0]} | {f[4]/f[0]:.2f} | {100*f[1]/f[0]:.1f} | {100*f[2]/f[0]:.1f} | {100*f[3]/f[0]:.1f} | {bp(y)} |")
out += ["", "## SMA20 vs SMA50 slope gap: convergence, divergence, standard deviation", "", "| Year | converging % | diverging % | gap mean | gap sd | SMA20 slope sd | EMA20 slope sd | Base pts |", "|---|---|---|---|---|---|---|---|"]
for y in sorted(cd):
    c = cd[y]; m = c[3] / max(1, c[0]); sd = math.sqrt(max(0, c[4] / max(1, c[0]) - m * m))
    sm = st[y]['SMA20']; em = st[y]['EMA20']
    ssd = math.sqrt(max(0, sm[3] / max(1, sm[0]) - (sm[1] / max(1, sm[0])) ** 2)); esd = math.sqrt(max(0, em[3] / max(1, em[0]) - (em[1] / max(1, em[0])) ** 2))
    out.append(f"| {y} | {100*c[1]/max(1,c[0]):.1f} | {100*c[2]/max(1,c[0]):.1f} | {m:.2f} | {sd:.2f} | {ssd:.2f} | {esd:.2f} | {bp(y)} |")
out += ["", "## Mean reversion (z over 10 closes, |z| >= 2.25, fade held 48 bars, gross of cost)", "", "| Year | events | reverted % | mean fade pts | PF | lag1 autocorr | Base pts |", "|---|---|---|---|---|---|---|"]
for y in sorted(mr):
    e = mr[y]; a = ac[y]
    if e[0] < 5: continue
    pf = e[3] / e[4] if e[4] else float('inf')
    out.append(f"| {y} | {e[0]} | {100*e[1]/e[0]:.1f} | {e[2]/e[0]:.1f} | {pf:.2f} | {a[1]/max(1e-12,a[2]):.3f} | {bp(y)} |")
open(os.path.join(D, "MARKET_PATTERNS.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out[:12]))
