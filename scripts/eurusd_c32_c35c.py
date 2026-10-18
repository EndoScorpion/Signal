"""
EURUSD Cycles C32–C35 — corrected stop logic
Key fix: stop checked from hour 8 (not 7). Entry at 07:00 open; stop monitored h8-h20; exit h21 open.
Same as eurusd_fade_backtest_v23.py: day_bars = hours 8..exit_hour
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

DATA = "/mnt/project-files/data/eurusd_fxopen_h1.csv"
COST = 0.00008

df = pd.read_csv(DATA)
df['ts'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
df['date'] = df['ts'].dt.date
df['hour'] = df['ts'].dt.hour
df['dow'] = df['ts'].dt.dayofweek   # 0=Mon,2=Wed,3=Thu
df = df.sort_values('ts').reset_index(drop=True)

df['prev_close'] = df['close'].shift(1)
df['tr'] = pd.concat([df['high']-df['low'],(df['high']-df['prev_close']).abs(),
                       (df['low']-df['prev_close']).abs()], axis=1).max(axis=1)
df['atr14'] = df['tr'].ewm(span=14, adjust=False).mean()
df['atr14_pct'] = df['atr14'].rolling(252, min_periods=50).rank(pct=True)

# EMA slopes using .diff() to match v23 script
for span in [60, 120, 200]:
    df[f'ema{span}'] = df['close'].ewm(span=span, adjust=False).mean()
    df[f'ema{span}_slope'] = df[f'ema{span}'].diff()

# ADX
high, low = df['high'], df['low']
up = high.diff(); dn = -low.diff()
pdm = np.where((up > dn) & (up > 0), up, 0.0)
ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
atr_s = df['tr'].ewm(span=14, adjust=False).mean()
pdi = 100 * pd.Series(pdm, index=df.index).ewm(span=14, adjust=False).mean() / atr_s
ndi = 100 * pd.Series(ndm, index=df.index).ewm(span=14, adjust=False).mean() / atr_s
dx = 100 * (pdi - ndi).abs() / (pdi + ndi).clip(lower=1e-9)
df['adx14'] = dx.ewm(span=14, adjust=False).mean()

# D1 EMA20 slope
d1 = df.groupby('date').agg(d1_close=('close', 'last')).reset_index()
d1['ema20_d1'] = d1['d1_close'].ewm(span=20, adjust=False).mean()
d1['d1_slope'] = d1['ema20_d1'].diff()

# Asia bars (0-6): net = close - open
asia = df[df['hour'].between(0, 6)].groupby('date').agg(
    asia_open=('open', 'first'), asia_close=('close', 'last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# 07:00 bar
bar07 = df[df['hour'] == 7].copy()
bar07 = bar07.rename(columns={'open': 'open07', 'high': 'high07', 'low': 'low07', 'close': 'close07'})
bar07 = bar07[['date', 'open07', 'high07', 'low07', 'close07',
               'atr14', 'atr14_pct', 'ema60_slope', 'ema120_slope', 'ema200_slope', 'adx14', 'dow']]

# 08:00 bar open (for 08:00 entries)
bar08 = df[df['hour'] == 8][['date', 'open']].rename(columns={'open': 'open08'})

entry = bar07.merge(asia, on='date').merge(bar08, on='date', how='left')
entry = entry.merge(d1[['date', 'd1_slope']], on='date', how='left')
entry['date_key'] = entry['date']  # keep as date for lookup
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year

# Build intraday dict: date -> sorted list of (hour, high, open) for hours 8-20
# Stop check on SHORT: high >= stop_px
intra_short = df[df['hour'].between(8, 20)][['date', 'hour', 'high', 'open']].copy()
intra_dict = {}
for row in intra_short.itertuples():
    d = row.date
    if d not in intra_dict:
        intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))

# 21:00 exit opens
bar21 = df[df['hour'] == 21][['date', 'open']].rename(columns={'open': 'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

# For LONG: stop check uses low
intra_long = df[df['hour'].between(8, 20)][['date', 'hour', 'low', 'open']].copy()
intra_long_dict = {}
for row in intra_long.itertuples():
    d = row.date
    if d not in intra_long_dict:
        intra_long_dict[d] = []
    intra_long_dict[d].append((row.hour, row.low, row.open))

def sim_short(ep, atr, date):
    stop_px = ep + 0.80 * atr
    bars = intra_dict.get(date, [])
    for hour, high, open_px in sorted(bars):
        if high >= stop_px:
            return stop_px, True
    exit_px = bar21_dict.get(date, None)
    if exit_px is None:
        exit_px = bars[-1][2] if bars else ep
    return exit_px, False

def sim_short_08(ep, atr, date):
    """08:00 entry: check bars 8-20 for stop, but entry is open08"""
    stop_px = ep + 0.80 * atr
    bars = intra_dict.get(date, [])
    # Skip the 08:00 bar's open check; still check its high for stop
    for hour, high, open_px in sorted(bars):
        if high >= stop_px:
            return stop_px, True
    exit_px = bar21_dict.get(date, None)
    if exit_px is None:
        exit_px = bars[-1][2] if bars else ep
    return exit_px, False

def sim_long(ep, atr, date):
    stop_px = ep - 0.80 * atr
    bars = intra_long_dict.get(date, [])
    for hour, low, open_px in sorted(bars):
        if low <= stop_px:
            return stop_px, True
    exit_px = bar21_dict.get(date, None)
    if exit_px is None:
        exit_px = ep
    return exit_px, False

def run_on_mask(mask, use_08_entry=False, long=False):
    results = []
    for _, row in entry[mask].iterrows():
        atr = row['atr14']
        date = row['date_key']
        if use_08_entry:
            if pd.isna(row['open08']): continue
            ep = row['open08']
        else:
            ep = row['open07']
        if long:
            exit_px, stopped = sim_long(ep, atr, date)
            pnl = (exit_px - ep) / ep - COST
        elif use_08_entry:
            exit_px, stopped = sim_short_08(ep, atr, date)
            pnl = (ep - exit_px) / ep - COST
        else:
            exit_px, stopped = sim_short(ep, atr, date)
            pnl = (ep - exit_px) / ep - COST
        results.append({'year': row['year'], 'pnl': pnl, 'stopped': stopped})
    if not results:
        return {'n': 0, 'pf': 0, 'avg': 0, 'win': 0, 'by_year': {}}
    r = pd.DataFrame(results)
    wins = r[r['pnl'] > 0]['pnl'].sum()
    losses = abs(r[r['pnl'] < 0]['pnl'].sum())
    pf = wins / losses if losses > 0 else float('inf')
    by_yr = {}
    for yr, g in r.groupby('year'):
        w = g[g['pnl'] > 0]['pnl'].sum(); l = abs(g[g['pnl'] < 0]['pnl'].sum())
        by_yr[yr] = round(w / l if l > 0 else float('inf'), 2)
    stop_rate = r['stopped'].mean() * 100
    return {'n': len(r), 'pf': round(pf, 2), 'avg': round(r['pnl'].mean()*100, 3),
            'win': round((r['pnl'] > 0).mean()*100, 1), 'by_year': by_yr,
            'stop_rate': round(stop_rate, 1)}

def pr(label, r):
    yr = ' | '.join(f"{y}: PF={v}" for y, v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%, win={r['win']}% (stop={r.get('stop_rate','?')}%)")
    if yr: print(f"    {yr}")

# v2.3 base mask (Wed/Thu only = dow 2,3)
base = (
    (entry['ema120_slope'] < 0) & (entry['adx14'] < 30) &
    (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
    (entry['dow'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14'])
)

print("=" * 65)
print("BASELINE CHECK (v2.3, stop checked from h8)")
print("=" * 65)
r_base = run_on_mask(base)
pr("v2.3 baseline", r_base)

print("\n" + "=" * 65)
print("C32: CONDITION SENSITIVITY (remove one condition at a time)")
print("=" * 65)

tests = [
    ("no EMA slope", (entry['adx14'] < 30) & (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
     (entry['dow'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14'])),
    ("no ADX", (entry['ema120_slope'] < 0) & (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
     (entry['dow'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14'])),
    ("no ATR pct", (entry['ema120_slope'] < 0) & (entry['adx14'] < 30) & (entry['atr14'] >= 0.0005) &
     (entry['dow'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14'])),
    ("all 5 days", (entry['ema120_slope'] < 0) & (entry['adx14'] < 30) &
     (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) & (entry['asia_net'] >= 0.25 * entry['atr14'])),
    ("Mon+Wed+Thu+Fri", (entry['ema120_slope'] < 0) & (entry['adx14'] < 30) &
     (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
     (entry['dow'].isin([0, 2, 3, 4])) & (entry['asia_net'] >= 0.25 * entry['atr14'])),
]
for label, mask in tests:
    print(f"\n--- {label} ---")
    pr(label, run_on_mask(mask))

print("\n" + "=" * 65)
print("C33: LONG SIDE — Asia moved DOWN, EMA>0, Wed/Thu")
print("=" * 65)
long_mask = ((entry['ema120_slope'] > 0) & (entry['adx14'] < 30) &
             (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
             (entry['dow'].isin([2, 3])) & (entry['asia_net'] <= -0.25 * entry['atr14']))
print("\nLONG (Asia down, EMA>0):")
pr("LONG EMA>0", run_on_mask(long_mask, long=True))

print("\n" + "=" * 65)
print("C34: EMA PERIOD SENSITIVITY (60 / 200 vs 120)")
print("=" * 65)
for span, col in [(60, 'ema60_slope'), (200, 'ema200_slope')]:
    mask = ((entry[col] < 0) & (entry['adx14'] < 30) & (entry['atr14_pct'] < 0.75) &
            (entry['atr14'] >= 0.0005) & (entry['dow'].isin([2, 3])) &
            (entry['asia_net'] >= 0.25 * entry['atr14']))
    print(f"\nEMA{span}:")
    pr(f"EMA{span} slope<0", run_on_mask(mask))

print("\n" + "=" * 65)
print("C35: 08:00 ENTRY (bear07 confirmation)")
print("=" * 65)
bear07_mask = base & (entry['close07'] < entry['open07'])
print("\n08:00 entry, bear07 confirm:")
pr("bear07 08:00 entry", run_on_mask(bear07_mask, use_08_entry=True))
# Compare: 07:00 entry bear07 subset
print("\n07:00 entry, bear07 subset (for comparison):")
pr("bear07 07:00 entry", run_on_mask(bear07_mask, use_08_entry=False))

print("\nDone.")
