"""
analyze_hst.py  -  Offline metric analyzer for EURUSD M15
Computes ER (Kaufman Efficiency Ratio), MMR (Nasif Hossain), ATR,
slope/momentum features on every M15 bar and writes a CSV for candidate_gen.py.

MMR (c) Nasif Hossain 2019 - original concept, all rights reserved.
ER  (c) Perry Kaufman 1995 - Smarter Trading.

Run: python -I data/analyze_hst.py
Output: data/m15_metrics.csv
"""

import struct, os, datetime, csv, math

HST_DIR = r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server"
BAR_FMT = '<qddddqiq'
BAR_SIZE = 60
HDR_SIZE = 148

OUT_CSV  = r"C:\Users\endos\Signal\data\m15_metrics.csv"

# ── helpers ────────────────────────────────────────────────────────────────────

def read_hst(fname):
    path = os.path.join(HST_DIR, fname)
    with open(path, 'rb') as f:
        f.read(HDR_SIZE)
        data = f.read()
    bars = []
    n = len(data) // BAR_SIZE
    for i in range(n):
        t, o, h, l, c, tv, sp, rv = struct.unpack_from(BAR_FMT, data, i * BAR_SIZE)
        bars.append((t, o, h, l, c, tv))
    bars.sort(key=lambda x: x[0])
    print(f"  {fname}: {len(bars):,} bars  "
          f"{datetime.datetime.utcfromtimestamp(bars[0][0]).date()} -> "
          f"{datetime.datetime.utcfromtimestamp(bars[-1][0]).date()}")
    return bars

def sma(vals, n, i):
    if i < n - 1: return None
    return sum(vals[i-n+1:i+1]) / n

def slope_pts(closes, i, period=20):
    """Linear slope of closes[i-period+1..i] in points/bar (5-digit)."""
    if i < period - 1: return None
    x = list(range(period))
    y = closes[i-period+1:i+1]
    mx = sum(x)/period; my = sum(y)/period
    num = sum((x[j]-mx)*(y[j]-my) for j in range(period))
    den = sum((x[j]-mx)**2 for j in range(period))
    if den == 0: return None
    return (num/den) * 100000  # to points

def efficiency_ratio(closes, i, n=10):
    """
    Kaufman Efficiency Ratio over n bars.
    ER = |net change| / sum(|bar changes|)
    Range 0 (random) to 1 (perfectly directional).
    (c) Perry Kaufman 1995 - Smarter Trading.
    """
    if i < n: return None
    net = abs(closes[i] - closes[i-n])
    path = sum(abs(closes[j] - closes[j-1]) for j in range(i-n+1, i+1))
    if path == 0: return None
    return net / path

def mmr_metric(closes, i, periods=(6, 12, 18)):
    """
    MMR (Max/Min slope Ratio) - original concept by Nasif Hossain (c) 2019.
    Measures momentum quality: max MA slope / |min MA slope| across multiple
    lookback windows. High MMR = one direction dominates (entry quality signal).
    All rights reserved, Nasif Hossain.
    """
    if i < max(periods) + 5: return None
    slp = []
    for p in periods:
        s = slope_pts(closes, i, period=p)
        if s is not None: slp.append(s)
    if len(slp) < 2: return None
    mx = max(slp); mn = min(slp)
    if abs(mn) == 0: return None
    return mx / abs(mn)

def atr(highs, lows, closes, i, n=14):
    if i < n: return None
    trs = [max(highs[j]-lows[j],
               abs(highs[j]-closes[j-1]),
               abs(lows[j]-closes[j-1])) for j in range(i-n+1, i+1)]
    return sum(trs)/n * 100000  # points

def stoch_k(highs, lows, closes, i, n=14):
    if i < n-1: return None
    hi = max(highs[i-n+1:i+1]); lo = min(lows[i-n+1:i+1])
    if hi == lo: return 50.0
    return (closes[i]-lo)/(hi-lo)*100

# ── main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== analyze_hst.py ===\n")
    m15 = read_hst("EURUSD15.hst")

    times  = [b[0] for b in m15]
    opens  = [b[1] for b in m15]
    highs  = [b[2] for b in m15]
    lows   = [b[3] for b in m15]
    closes = [b[4] for b in m15]
    vols   = [b[5] for b in m15]

    print("\nComputing metrics on every M15 bar...")
    rows_written = 0
    WARMUP = 50  # skip first N bars while indicators settle

    with open(OUT_CSV, 'w', newline='') as fout:
        w = csv.writer(fout)
        w.writerow([
            'ts', 'dt',
            'close',
            'slope6', 'slope12', 'slope20',
            'er10', 'er20',
            'mmr_6_12_18',
            'atr14_pts',
            'stoch_k14',
            'vol_rel20',      # volume / 20-bar avg volume
            'close_above_sma20_pts',
        ])

        sma20_vol = None
        for i in range(WARMUP, len(m15)):
            if i % 100000 == 0:
                print(f"  {i:,}/{len(m15):,} ...", flush=True)

            slp6  = slope_pts(closes, i, 6)
            slp12 = slope_pts(closes, i, 12)
            slp20 = slope_pts(closes, i, 20)
            er10  = efficiency_ratio(closes, i, 10)
            er20  = efficiency_ratio(closes, i, 20)
            mmr   = mmr_metric(closes, i, (6, 12, 18))
            a14   = atr(highs, lows, closes, i, 14)
            k14   = stoch_k(highs, lows, closes, i, 14)

            # volume relative to 20-bar SMA
            if i >= 20:
                avg_vol = sum(vols[i-20:i]) / 20
                vol_rel = vols[i] / avg_vol if avg_vol > 0 else None
            else:
                vol_rel = None

            # close distance above SMA20 in points
            s20 = sma(closes, 20, i)
            above_sma = (closes[i] - s20) * 100000 if s20 else None

            if None in (slp6, slp12, slp20, er10, er20, mmr, a14, k14, vol_rel, above_sma):
                continue

            ts  = times[i]
            dt  = datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
            w.writerow([
                ts, dt,
                round(closes[i], 5),
                round(slp6, 3), round(slp12, 3), round(slp20, 3),
                round(er10, 4), round(er20, 4),
                round(mmr, 4),
                round(a14, 1),
                round(k14, 1),
                round(vol_rel, 4),
                round(above_sma, 1),
            ])
            rows_written += 1

    print(f"\nWrote {rows_written:,} rows -> {OUT_CSV}")
    print("Next: run candidate_gen.py to find ER/MMR gate thresholds.\n")

if __name__ == '__main__':
    main()
