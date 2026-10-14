"""er_analyze.py - Kaufman Efficiency Ratio regime study on an MT4 .hst file (read-only, backtest research only).
Usage: python3 -I scripts/er_analyze.py FILE.hst [ER_PERIOD=10] [HORIZON=12] [COST_PTS=0.6]
For each ER bucket, measures forward return over HORIZON bars against the prior-ER-window direction:
  mr_edge = mean(-sign(prior move) * fwd move) in points; positive = mean-reverting, negative = trending.
ER method: Perry Kaufman, ER = |P[t]-P[t-n]| / sum(|P[i]-P[i-1]|)."""
import struct, sys, collections
import numpy as np
def read_hst(path):
    d = open(path, "rb").read()
    ver = struct.unpack_from("<i", d, 0)[0]
    if ver == 400: dt = np.dtype([("t","<i4"),("o","<f8"),("l","<f8"),("h","<f8"),("c","<f8"),("v","<f8")]); off = 148
    else: dt = np.dtype([("t","<i8"),("o","<f8"),("h","<f8"),("l","<f8"),("c","<f8"),("v","<i8"),("sp","<i4"),("rv","<i8")]); off = 148
    n = (len(d) - off) // dt.itemsize
    return np.frombuffer(d, dt, n, off), ver
def er(c, n):
    out = np.full(len(c), np.nan)
    path = np.convolve(np.abs(np.diff(c)), np.ones(n), "valid")      # sum |diff| over n steps
    net = np.abs(c[n:] - c[:-n])
    out[n:] = np.where(path > 0, net / path, np.nan)
    return out
def main():
    f = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 12; cost = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
    b, ver = read_hst(f); c = b["c"]; t = b["t"].astype("int64")
    pt = 1e-5 if c.mean() < 10 else 1e-3
    e = er(c, n); prior = np.full(len(c), np.nan); prior[n:] = c[n:] - c[:-n]
    fwd = np.full(len(c), np.nan); fwd[:-h] = c[h:] - c[:-h]
    ok = ~np.isnan(e) & ~np.isnan(fwd) & (prior != 0)
    # drop windows spanning data gaps / weekends (span > 1.5x nominal bar time) so jumps do not fake edge
    bar = int(np.median(np.diff(t))); gl = np.zeros(len(c), bool)
    gl[h:] |= False
    span_f = np.full(len(c), np.inf); span_f[:-h] = t[h:] - t[:-h]
    span_p = np.full(len(c), np.inf); span_p[n:] = t[n:] - t[:-n]
    ok &= (span_f <= 1.5 * h * bar) & (span_p <= 1.5 * n * bar)
    edge = -np.sign(prior) * fwd / pt
    yr = (t // 31556952 + 1970).astype(int)
    print(f"{f}: hst v{ver}, {len(c)} bars, ER{n}, horizon {h}, cost {cost} pts")
    edges = [0, .1, .2, .3, .4, .5, .7, 1.01]
    print("ER bucket      N     mr_edge_pts  net_of_cost  hit%")
    for lo, hi in zip(edges, edges[1:]):
        m = ok & (e >= lo) & (e < hi)
        if m.sum() < 50: continue
        x = edge[m]; print(f"{lo:.1f}-{min(hi,1):.1f}  {m.sum():9d}  {x.mean():10.2f}  {x.mean()-cost:10.2f}  {100*(x>0).mean():5.1f}")
    print("\nBy year, ER<0.3 (mean-revert regime) mr_edge_pts / N, versus ER>=0.5:")
    for y in sorted(set(yr[ok])):
        lo = ok & (yr == y) & (e < .3); hi_ = ok & (yr == y) & (e >= .5)
        if lo.sum() > 50: print(y, f"{edge[lo].mean():7.2f} /{lo.sum():7d}   |  " + (f"{edge[hi_].mean():7.2f} /{hi_.sum():6d}" if hi_.sum() > 50 else "n/a"))
if __name__ == "__main__": main()
