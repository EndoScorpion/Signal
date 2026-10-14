"""er_m1.py - read-only Kaufman ER regime study on a full M1 .hst. Pure Python (no numpy), streaming, ~150 MB RAM.
Usage: python -I er_m1.py HST OUT.txt   (cost = 5 pts commission + ~1 pt avg spread/2 = 6.0 pts round trip)
Per-year stability of mean-reversion edge by ER band, net of cost. Backtest research only; no trading authority."""
import sys, struct, array
COST = 6.0
f, out = sys.argv[1], sys.argv[2]
with open(f, "rb") as fh:
    hdr = fh.read(148); ver = struct.unpack_from("<i", hdr, 0)[0]
    fmt, size, ci = ("<iddddd", 44, 4) if ver == 400 else ("<qddddqiq", 60, 4)
    T = array.array("i"); C = array.array("d"); rec = struct.Struct(fmt)
    while True:
        buf = fh.read(size * 200000)
        if not buf: break
        for r in rec.iter_unpack(buf[:len(buf) // size * size]):
            T.append(r[0] & 0x7fffffff if r[0] < 2**31 else 0); C.append(r[ci])
n = len(T)
CS = array.array("d", [0.0]) * n
s = 0.0
for i in range(1, n):
    s += abs(C[i] - C[i - 1]); CS[i] = s
L = [f"{f}\nhst v{ver}, {n} bars, first {T[0]} last {T[-1]}, cost {COST} pts"]
BANDS = [(0, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .5), (.5, .7), (.7, 1.01)]
def band(e):
    for k, (lo, hi) in enumerate(BANDS):
        if lo <= e < hi: return k
    return len(BANDS) - 1
for N in (30, 120):
    HS = (60, 240); acc = {(h, k): {} for h in HS for k in range(len(BANDS))}
    for i in range(N, n - max(HS)):
        p = C[i] - C[i - N]
        if p == 0 or T[i] - T[i - N] > 90 * N: continue
        path = CS[i] - CS[i - N]
        if path <= 0: continue
        k = band(abs(p) / path); sg = -1.0 if p > 0 else 1.0; y = T[i] // 31556952 + 1970
        for h in HS:
            if T[i + h] - T[i] > 90 * h: continue
            d = acc[(h, k)].setdefault(y, [0.0, 0]); d[0] += sg * (C[i + h] - C[i]) / 1e-5; d[1] += 1
    for h in HS:
        L.append(f"\n=== ER{N} (M1), horizon {h} M1 bars: mean-reversion edge in pts, NET of {COST} cost; yrs+ = years with net>0 (years with >=2000 samples) ===")
        for k, (lo, hi) in enumerate(BANDS):
            d = acc[(h, k)]; tot = sum(v[1] for v in d.values())
            if tot < 5000: continue
            gross = sum(v[0] for v in d.values()) / tot
            ys = sorted((y, v[0] / v[1] - COST) for y, v in d.items() if v[1] >= 2000)
            L.append(f"ER {lo:.1f}-{min(hi,1):.1f}  N={tot:8d}  gross={gross:7.2f}  net={gross-COST:7.2f}  yrs+ {sum(1 for _,x in ys if x>0)}/{len(ys)}  " + " ".join(f"{y%100:02d}:{x:+.1f}" for y, x in ys))
open(out, "w").write("\n".join(L) + "\n")
print("\n".join(L))
