"""
EURUSD Cycles C32–C35 — FIXED stop logic (check all H1 bars 07-21 UTC)
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
df['weekday'] = df['ts'].dt.weekday
df = df.sort_values('ts').reset_index(drop=True)

df['prev_close'] = df['close'].shift(1)
df['tr'] = np.maximum(df['high'] - df['low'],
           np.maximum(abs(df['high'] - df['prev_close']), abs(df['low'] - df['prev_close'])))
df['atr14'] = df['tr'].ewm(span=14, adjust=False).mean()
df['atr14_pct'] = df['atr14'].rolling(252, min_periods=50).rank(pct=True)

for span in [60, 120, 200]:
    df[f'ema{span}'] = df['close'].ewm(span=span, adjust=False).mean()
    df[f'ema{span}_slope'] = df[f'ema{span}'] - df[f'ema{span}'].shift(5)

high, low, close = df['high'], df['low'], df['close']
plus_dm = (high - high.shift(1)).clip(lower=0)
minus_dm = (low.shift(1) - low).clip(lower=0)
mask_both = (plus_dm > 0) & (minus_dm > 0)
plus_dm[mask_both & (plus_dm <= minus_dm)] = 0
minus_dm[mask_both & (minus_dm < plus_dm)] = 0
atr14_s = df['tr'].ewm(span=14, adjust=False).mean()
plus_di = 100 * plus_dm.ewm(span=14, adjust=False).mean() / atr14_s
minus_di = 100 * minus_dm.ewm(span=14, adjust=False).mean() / atr14_s
dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
df['adx14'] = dx.ewm(span=14, adjust=False).mean()

# D1
d1 = df.groupby('date').agg(
    d1_open=('open','first'), d1_high=('high','max'),
    d1_low=('low','min'), d1_close=('close','last')).reset_index()
d1['ema20_d1'] = d1['d1_close'].ewm(span=20, adjust=False).mean()
d1['d1_slope'] = d1['ema20_d1'] - d1['ema20_d1'].shift(5)

# Asia
asia = df[df['hour'].between(0, 6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last'),
    asia_high=('high','max'), asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# 07:00 bar
bar07 = df[df['hour'] == 7].copy()
bar07_cols = {'open': 'open07', 'high': 'high07', 'low': 'low07', 'close': 'close07'}
bar07 = bar07.rename(columns=bar07_cols)
keep_cols = ['date', 'open07', 'high07', 'low07', 'close07',
             'atr14', 'atr14_pct', 'ema60', 'ema120', 'ema200',
             'ema60_slope', 'ema120_slope', 'ema200_slope', 'adx14', 'weekday']
bar07 = bar07[keep_cols]

# 08:00 bar
bar08 = df[df['hour'] == 8][['date', 'open', 'high', 'low', 'close']].copy()
bar08 = bar08.rename(columns={'open': 'open08', 'high': 'high08', 'low': 'low08', 'close': 'close08'})

# Intraday bars 07–20 for stop check; 21:00 open is the time-exit price
# Do NOT check 21:00 bar for stop — exit happens at its open
intra = df[df['hour'].between(7, 20)][['date', 'hour', 'high', 'low', 'open']].copy()
# Separately grab 21:00 opens for time-exit
bar21_opens = df[df['hour'] == 21][['date', 'open']].rename(columns={'open': 'open21'})
bar21_dict = dict(zip(bar21_opens['date'], bar21_opens['open21']))
# For 08:00 entries, only bars 08–20
intra08 = df[df['hour'].between(8, 20)][['date', 'hour', 'high', 'low', 'open']].copy()

entry = bar07.merge(asia, on='date').merge(bar08, on='date', how='left')
entry = entry.merge(d1[['date', 'd1_slope']], on='date', how='left')
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year

# Build date -> list of (hour, high, low, open) for quick lookup
intra_dict = {}
for row in intra.itertuples():
    d = row.date
    if d not in intra_dict:
        intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.low, row.open))

intra08_dict = {}
for row in intra08.itertuples():
    d = row.date
    if d not in intra08_dict:
        intra08_dict[d] = []
    intra08_dict[d].append((row.hour, row.high, row.low, row.open))

def sim_short(entry_px, atr, date, use_08_bars=False):
    """Simulate SHORT trade: check each hourly bar (7-20) for stop hit; exit at 21:00 open."""
    stop_px = entry_px + 0.80 * atr
    bars = (intra08_dict if use_08_bars else intra_dict).get(date, [])
    for hour, high, low, open_px in sorted(bars):
        if high >= stop_px:
            return stop_px, True  # stopped
    # Not stopped — use 21:00 open as exit
    exit_21 = bar21_dict.get(date, None)
    if exit_21 is None:
        if bars:
            exit_21 = sorted(bars)[-1][3]  # last bar's open as fallback
        else:
            exit_21 = entry_px
    return exit_21, False

def run_on_mask(mask, use_08_entry=False):
    results = []
    for _, row in entry[mask].iterrows():
        atr = row['atr14']
        if use_08_entry:
            if pd.isna(row['open08']): continue
            ep = row['open08']
            use_08 = True
        else:
            ep = row['open07']
            use_08 = False
        date = row['date'].date()
        exit_px, stopped = sim_short(ep, atr, date, use_08_bars=use_08)
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
        w = g[g['pnl']>0]['pnl'].sum(); l = abs(g[g['pnl']<0]['pnl'].sum())
        by_yr[yr] = round(w/l if l>0 else float('inf'), 2)
    return {
        'n': len(r), 'pf': round(pf, 2), 'avg': round(r['pnl'].mean()*100, 3),
        'win': round((r['pnl']>0).mean()*100, 1), 'by_year': by_yr
    }

def pr(label, r):
    yr = ' | '.join(f"{y}: PF={v}" for y, v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%, win={r['win']}%")
    if yr: print(f"    {yr}")

# Baseline mask
base = (
    (entry['ema120_slope'] < 0) & (entry['adx14'] < 30) &
    (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
    (entry['weekday'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14'])
)

print("=" * 65)
print("BASELINE CHECK (v2.3 with full intraday stop simulation)")
print("=" * 65)
r_base = run_on_mask(base)
pr("v2.3 baseline", r_base)

print("\n" + "=" * 65)
print("C32: CONDITION SENSITIVITY")
print("=" * 65)

no_ema = ((entry['adx14'] < 30) & (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
          (entry['weekday'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14']))
print("\n--- Without EMA120 slope ---")
pr("no EMA slope", run_on_mask(no_ema))

no_adx = ((entry['ema120_slope'] < 0) & (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
          (entry['weekday'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14']))
print("\n--- Without ADX ---")
pr("no ADX", run_on_mask(no_adx))

no_atrpct = ((entry['ema120_slope'] < 0) & (entry['adx14'] < 30) & (entry['atr14'] >= 0.0005) &
             (entry['weekday'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14']))
print("\n--- Without ATR percentile ---")
pr("no ATR pct", run_on_mask(no_atrpct))

no_dow = ((entry['ema120_slope'] < 0) & (entry['adx14'] < 30) &
          (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
          (entry['asia_net'] >= 0.25 * entry['atr14']))
print("\n--- Without DoW filter (all 5 days) ---")
pr("no DoW", run_on_mask(no_dow))

with_monf = ((entry['ema120_slope'] < 0) & (entry['adx14'] < 30) &
             (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
             (entry['weekday'].isin([0, 2, 3, 4])) & (entry['asia_net'] >= 0.25 * entry['atr14']))
print("\n--- Add Mon+Fri (Wed/Thu/Mon/Fri) ---")
pr("Mon+Wed+Thu+Fri", run_on_mask(with_monf))

print("\n" + "=" * 65)
print("C33: LONG SIDE — Asia moved DOWN >= 0.25xATR")
print("=" * 65)

long_mask = ((entry['ema120_slope'] > 0) & (entry['adx14'] < 30) &
             (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
             (entry['weekday'].isin([2, 3])) & (entry['asia_net'] <= -0.25 * entry['atr14']))

# LONG simulation
def sim_long(entry_px, atr, date):
    stop_px = entry_px - 0.80 * atr
    bars = intra_dict.get(date, [])
    for hour, high, low, open_px in sorted(bars):
        if low <= stop_px:
            return stop_px, True
    exit_21 = bar21_dict.get(date, None)
    if exit_21 is None:
        exit_21 = entry_px
    return exit_21, False

results_long = []
for _, row in entry[long_mask].iterrows():
    atr = row['atr14']
    ep = row['open07']
    date = row['date'].date()
    exit_px, stopped = sim_long(ep, atr, date)
    pnl = (exit_px - ep) / ep - COST
    results_long.append({'year': row['year'], 'pnl': pnl})

if results_long:
    rl = pd.DataFrame(results_long)
    w = rl[rl['pnl']>0]['pnl'].sum(); l = abs(rl[rl['pnl']<0]['pnl'].sum())
    print(f"\n  LONG (EMA>0, Asia down): n={len(rl)}, PF={w/l:.2f}, avg={rl['pnl'].mean()*100:+.3f}%, win={(rl['pnl']>0).mean()*100:.1f}%")
    for yr, g in rl.groupby('year'):
        w2 = g[g['pnl']>0]['pnl'].sum(); l2 = abs(g[g['pnl']<0]['pnl'].sum())
        print(f"    {yr}: n={len(g)}, PF={w2/l2:.2f}" if l2>0 else f"    {yr}: n={len(g)}, PF=inf")
else:
    print("  n=0")

print("\n" + "=" * 65)
print("C34: EMA PERIOD SENSITIVITY (60 / 200)")
print("=" * 65)
for span in [60, 200]:
    mask = ((entry[f'ema{span}_slope'] < 0) & (entry['adx14'] < 30) &
            (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
            (entry['weekday'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14']))
    print(f"\nEMA{span} slope<0:")
    pr(f"EMA{span}", run_on_mask(mask))

print("\n" + "=" * 65)
print("C35: 08:00 ENTRY (bear07 confirm — enter at 08:00 open)")
print("=" * 65)
bear07_mask = base & (entry['close07'] < entry['open07'])
print(f"\n07:00 bear confirm (08:00 entry):")
pr("bear07 08:00 entry", run_on_mask(bear07_mask, use_08_entry=True))

print("\nDone.")
