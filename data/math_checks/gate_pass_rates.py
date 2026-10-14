import numpy as np, struct, sys
from numpy.lib.stride_tricks import sliding_window_view as swv
P = r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server\EURUSD15.hst"
with open(P, 'rb') as f:
    h = f.read(148)
digits = struct.unpack('<i', h[84:88])[0]
Pt = 10.0 ** -digits
dt = np.dtype([('t', '<i8'), ('o', '<f8'), ('h', '<f8'), ('l', '<f8'), ('c', '<f8'), ('v', '<i8'), ('s', '<i4'), ('rv', '<i8')])
a = np.memmap(P, dtype=dt, mode='r', offset=148)
T = np.array(a['t']); C = np.array(a['c']); H = np.array(a['h']); L = np.array(a['l'])
N = len(C)
yr = T.astype('datetime64[s]').astype('datetime64[Y]').astype(int) + 1970
print('bars', N, 'digits', digits, file=sys.stderr)


def sma(p):
    cs = np.cumsum(np.insert(C, 0, 0.0))
    o = np.full(N, np.nan)
    o[p - 1:] = (cs[p:] - cs[:-p]) / p
    return o


def slope(p):
    s = np.full(N, np.nan)
    m = sma(p)
    s[1:] = (m[1:] - m[:-1]) / Pt
    return s


S = {p: slope(p) for p in (10, 20, 50, 100, 200)}
ret = np.zeros(N)
ret[1:] = (C[1:] - C[:-1]) / Pt
rv = np.full(N, np.nan)
rv[19:] = swv(ret, 20).std(axis=1)
tr = np.zeros(N)
tr[0] = H[0] - L[0]
tr[1:] = np.maximum(H[1:], C[:-1]) - np.minimum(L[1:], C[:-1])
atr = np.full(N, np.nan)
atr[13:] = swv(tr, 14).mean(axis=1) / Pt


def adx(n=14):
    up = np.zeros(N); dn = np.zeros(N)
    up[1:] = H[1:] - H[:-1]; dn[1:] = L[:-1] - L[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    out = np.full(N, np.nan)
    sp = sm = st = 0.0; ax = 0.0; dxs = []
    for i in range(1, N):
        if i <= n:
            sp += pdm[i]; sm += mdm[i]; st += tr[i]
        else:
            sp = sp - sp / n + pdm[i]; sm = sm - sm / n + mdm[i]; st = st - st / n + tr[i]
        if i >= n:
            pdi = 100 * sp / st if st > 0 else 0
            mdi = 100 * sm / st if st > 0 else 0
            dx = 100 * abs(pdi - mdi) / (pdi + mdi) if pdi + mdi > 0 else 0
            if i < 2 * n:
                dxs.append(dx)
            if i == 2 * n - 1:
                ax = sum(dxs) / n; out[i] = ax
            elif i >= 2 * n:
                ax = (ax * (n - 1) + dx) / n; out[i] = ax
    return out


ADX = adx()
ad = np.abs(np.diff(C, prepend=C[0]))
path = np.full(N, np.nan); path[19:] = swv(ad, 20).sum(axis=1)
net = np.full(N, np.nan); net[20:] = np.abs(C[20:] - C[:-20])
ER = net / np.where(path > 0, path, np.nan)
S20w = np.full(N, np.nan); S20w[19:] = swv(S[20], 20).std(axis=1)
SSD = np.stack([S[p] for p in (10, 20, 50, 100, 200)], 0).std(axis=0)
SSR = np.where(np.abs(S[200]) < 0.05, np.nan, np.clip(S[20] / np.where(S[200] == 0, np.nan, S[200]), -10, 10))


def katz(I):
    w = C[I[:, None] + np.arange(-63, 1)]
    Ln = (np.abs(np.diff(w, axis=1)) / Pt).sum(1)
    d = (np.abs(w[:, 1:] - w[:, :1]) / Pt).max(1)
    n = 63.0
    ok = (Ln > 0) & (d > 0)
    return np.where(ok, np.log10(n) / (np.log10(n) + np.log10(np.where(ok, d, 1) / np.where(ok, Ln, 1))), 1.0)


def hurst(I):
    r = np.diff(C[I[:, None] + np.arange(-128, 1)], axis=1)
    lx = []; ly = []
    for n in (8, 16, 32, 64):
        b = r.reshape(len(I), 128 // n, n)
        d = b - b.mean(2, keepdims=True)
        cum = np.cumsum(d, 2)
        R = np.maximum(cum.max(2), 0) - np.minimum(cum.min(2), 0)
        sd = np.sqrt((d ** 2).mean(2)); ok = sd > 0
        rs = np.where(ok, R / np.where(ok, sd, 1), 0).sum(1) / np.maximum(ok.sum(1), 1)
        lx.append(np.log(n)); ly.append(np.log(np.where(rs > 0, rs, np.nan)))
    lx = np.array(lx); ly = np.stack(ly, 1)
    return ((lx - lx.mean()) * (ly - ly.mean(1, keepdims=True))).sum(1) / ((lx - lx.mean()) ** 2).sum()


def vov(I):
    w = rv[I[:, None] + np.arange(-9, 1)]
    m = w.mean(1)
    return np.where(m > 0, w.std(1) / np.where(m > 0, m, 1), 0)


def acf(I):
    a_ = ret[I[:, None] + np.arange(-59, 1)]
    b_ = ret[I[:, None] + np.arange(-60, 0)]
    s1 = (a_ * a_).sum(1)
    return np.where(s1 > 0, (a_ * b_).sum(1) / np.where(s1 > 0, s1, 1), np.nan)


def ou(I):
    w = C[I[:, None] + np.arange(-100, 1)] / Pt
    x = w[:, :-1]; dx = np.diff(w, axis=1)
    xm = x - x.mean(1, keepdims=True)
    b = (xm * (dx - dx.mean(1, keepdims=True))).sum(1) / (xm * xm).sum(1)
    hl = np.full(len(I), 9999.0)
    ok = (b < 0) & (b > -1)
    hl[ok] = -np.log(2) / np.log(1 + b[ok])
    return hl


def lyap1(i):
    x = C[i - 104:i + 1] / Pt
    n, m, K = 100, 3, 5
    M = n - m
    E = np.stack([x[t:t + M] for t in range(m)], 1)
    F = np.stack([x[K + t:K + t + M] for t in range(m)], 1)
    D = np.sqrt(((E[:, None, :] - E[None, :, :]) ** 2).sum(2))
    ii = np.arange(M)
    D[np.abs(ii[:, None] - ii[None, :]) < 4] = np.inf
    D[D <= 0] = np.inf
    bj = D.argmin(1); best = D[ii, bj]; ok = np.isfinite(best)
    dk = np.sqrt(((F - F[bj]) ** 2).sum(1)); ok &= dk > 0
    return (np.log(dk[ok] / best[ok]) / K).mean() if ok.any() else 0.0


def chunks(I, f, cs=4000):
    return np.concatenate([f(I[k:k + cs]) for k in range(0, len(I), cs)])


YEARS = [2010, 2013, 2014, 2015, 2016, 2018, 2023, 2024]
G = {}


def put(k, y, v):
    G.setdefault(k, {})[y] = np.asarray(v, float)


for y in YEARS:
    I = np.where(yr == y)[0]
    I = I[I >= 300]
    if len(I) == 0:
        print('no bars', y, file=sys.stderr); continue
    print('year', y, len(I), file=sys.stderr)
    put('FD', y, chunks(I, katz)); put('Hurst', y, chunks(I, hurst)); put('Vov', y, chunks(I, vov))
    put('AC1', y, chunks(I, acf)); put('OUhalf', y, chunks(I, ou))
    put('ADX', y, ADX[I]); put('ER20', y, ER[I]); put('SlopeStackSd', y, SSD[I]); put('SlopeSd', y, S20w[I])
    put('SSR', y, SSR[I]); put('Rvol20', y, rv[I]); put('ATR14', y, atr[I])
    put('Lyap', y, [lyap1(i) for i in I[::10]])
YEARS = [y for y in YEARS if y in G['FD']]


def pct(v, q):
    v = v[np.isfinite(v)]
    return np.percentile(v, q) if len(v) else np.nan


def passr(v, f):
    with np.errstate(invalid='ignore'):
        ok = f(v)
    return 100.0 * np.sum(ok & np.isfinite(v)) / len(v)


def verdict(p):
    return 'INERT' if (p > 97 or p < 3) else 'TIGHT' if p < 15 else 'LOOSE' if p > 85 else 'USEFUL'


spec = [
    ('FD', 'Katz FD (64)', [('FdMax 1.5', lambda v: v <= 1.5)], 'max'),
    ('Lyap', 'Lyapunov (every 10th bar)', [('LyapMax 0.15', lambda v: v <= 0.15)], 'max'),
    ('Hurst', 'Hurst R/S 128', [('HurstMax 0.5', lambda v: v <= 0.5)], 'max'),
    ('Vov', 'Vol-of-vol', [('VovMax 0.35', lambda v: v <= 0.35)], 'max'),
    ('ADX', 'ADX(14)', [('AdxMax 25 (<=)', lambda v: v <= 25), ('AdxMin 20 (>=)', lambda v: v >= 20)], 'both'),
    ('ER20', 'ER20', [('ErMax 0.25 (<=)', lambda v: v <= 0.25), ('ErMin 0.30 (>=)', lambda v: v >= 0.30),
                      ('ErMin 0.30 and ErMax 0.25 together', lambda v: (v >= 0.30) & (v <= 0.25))], 'both'),
    ('SlopeStackSd', 'Slope-stack SD (pts/bar)', [('SlopeStackSdMax 3', lambda v: v <= 3)], 'max'),
    ('SlopeSd', 'SMA20 slope SD 20 bars (pts/bar)', [('SlopeSdMax 12', lambda v: v <= 12)], 'max'),
    ('SSR', 'SSR slope(SMA20)/slope(SMA200)', [('inside 0.2..5 (SsrMode1)', lambda v: (v >= 0.2) & (v <= 5)),
                                               ('outside band (SsrMode2; NaN fails)', lambda v: ((v < 0.2) | (v > 5)))], 'ssr'),
    ('OUhalf', 'OU half-life (bars; 9999 = no reversion)', [('4..40', lambda v: (v >= 4) & (v <= 40)), ('2..20', lambda v: (v >= 2) & (v <= 20))], 'ou'),
    ('AC1', 'Lag-1 autocorr 60 returns', [('AcMax 0 as queued (EA: guard is >0, so gate OFF)', lambda v: np.ones_like(v, bool)),
                                          ('hypothetical ac<=0', lambda v: v <= 0)], 'max'),
    ('Rvol20', 'Rolling return SD 20 (pts)', [('RvolNow<=29.6', lambda v: v <= 29.6), ('RvolNow<=45.6', lambda v: v <= 45.6)], 'max'),
    ('ATR14', 'ATR14 (pts)', [('cap 48', lambda v: v <= 48), ('cap 60', lambda v: v <= 60), ('cap 90', lambda v: v <= 90), ('cap 120', lambda v: v <= 120)], 'max'),
]
out = ['# Gate pass rates (M15, clean history EURUSD15.hst, Point=%g)' % Pt, '',
       'Computed at the last closed bar (shift 1) of each M15 bar. NaN/undefined counts as FAIL. Verdict: INERT >97% or <3%, TIGHT <15%, USEFUL 15-85%, LOOSE >85%.',
       'Script: gate_pass_rates.py (same folder). ADX = Wilder smoothing (MT4 iADX near-identical). Lyapunov sampled every 10th bar.', '']
rec = []
for key, lab, tests, kind in spec:
    out += ['## ' + lab, '', '| year | n | p5 | p25 | p50 | p75 | p95 | ' + ' | '.join('pass% ' + t[0] for t in tests) + ' |',
            '|' + '---|' * (7 + len(tests))]
    allv = np.concatenate([G[key][y] for y in YEARS])
    for y in YEARS + ['ALL']:
        v = allv if y == 'ALL' else G[key][y]
        ps = [pct(v, q) for q in (5, 25, 50, 75, 95)]
        out.append('| %s | %d | ' % (y, len(v)) + ' | '.join('%.4g' % p for p in ps) + ' | ' + ' | '.join('%.1f' % passr(v, f) for _, f in tests) + ' |')
    out += ['', 'Verdicts:', '']
    for lbl, f in tests:
        py = [passr(G[key][y], f) for y in YEARS]
        pa = passr(allv, f)
        out.append('- %s: pooled %.1f%% -> **%s**; per-year %.1f..%.1f%%' % (lbl, pa, verdict(pa), min(py), max(py)))
    fin = allv[np.isfinite(allv)]
    if kind in ('max', 'both'):
        t = np.percentile(fin, 45)
        r = '<= %.4g (~45%% pass)' % t
        if key == 'ADX':
            r = 'AdxMax %.1f (~45%% pass) ; AdxMin %.1f (~45%% pass)' % (t, np.percentile(fin, 55))
        if key == 'ER20':
            r = 'ErMax %.3f (~45%% pass) ; ErMin %.3f (~45%% pass); keep ErMin < ErMax' % (t, np.percentile(fin, 55))
        if key == 'ATR14':
            r = 'AtrCapPts %.1f (~45%%); 30%%: %.1f; 60%%: %.1f' % (t, np.percentile(fin, 30), np.percentile(fin, 60))
        if key == 'Rvol20':
            r = 'CalmRvolMax %.1f (~45%%); 30%%: %.1f; 60%%: %.1f' % (t, np.percentile(fin, 30), np.percentile(fin, 60))
        if key == 'AC1':
            r = 'AcMax is inactive unless >0 (code line 271); with the guard fixed use AcMax %.3f (~45%% pass)' % t
        if key not in ('ADX', 'ER20'):
            prr = [passr(G[key][y], lambda v, t=t: v <= t) for y in YEARS]
            r += '; per-year pass %.0f..%.0f%%' % (min(prr), max(prr))
        rec.append((lab, r))
    elif kind == 'ssr':
        for hi in (5, 8, 10):
            rec.append((lab, 'band 0.2..%g -> %.1f%% pass' % (hi, passr(allv, lambda v, hi=hi: (v >= 0.2) & (v <= hi)))))
        rec.append((lab, 'share undefined (|slope SMA200|<0.05 pts/bar, fails): %.1f%%' % (100 * np.mean(~np.isfinite(allv)))))
    elif kind == 'ou':
        for lo, hi in ((4, 40), (2, 20), (3, 60), (2, 100), (2, 200)):
            rec.append((lab, '%g..%g -> %.1f%% pass' % (lo, hi, passr(allv, lambda x, lo=lo, hi=hi: (x >= lo) & (x <= hi)))))
        rec.append((lab, 'share with no reversion (9999): %.1f%%' % (100 * np.mean(allv >= 9999))))
    out.append('')
out += ['# Recommended thresholds (target 30-60% pass, EA input units)', '']
for l, r in rec:
    out.append('- **%s**: %s' % (l, r))
open(r'C:\Users\endos\Signal\data\math_checks\gate_pass_rates.md', 'w').write('\n'.join(out) + '\n')
print('done')
