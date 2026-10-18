"""
EURUSD Cycle C56 — Three-filter combos from C53b, Bar07 range size, Overnight gap
C56a: C53b (SK<60+D1) + third filter: C43, C46c (ATR>=7pip), skip Q2
C56b: Bar07 range relative to ATR — large vs small bar at entry
C56c: Overnight gap (close06 vs open07) — gap up favors short, gap down weakens
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
df['dow'] = df['ts'].dt.dayofweek
df['month'] = df['ts'].dt.month
df = df.sort_values('ts').reset_index(drop=True)

df['prev_close'] = df['close'].shift(1)
df['tr'] = pd.concat([df['high']-df['low'],(df['high']-df['prev_close']).abs(),
                       (df['low']-df['prev_close']).abs()],axis=1).max(axis=1)
df['atr14'] = df['tr'].ewm(span=14, adjust=False).mean()
df['atr14_pct'] = df['atr14'].rolling(252, min_periods=50).rank(pct=True)

df['ema120'] = df['close'].ewm(span=120, adjust=False).mean()
df['ema120_slope'] = df['ema120'].diff()

up = df['high'].diff(); dn = -df['low'].diff()
pdm = np.where((up > dn) & (up > 0), up, 0.0)
ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
atr_s = df['tr'].ewm(span=14, adjust=False).mean()
pdi = 100*pd.Series(pdm,index=df.index).ewm(span=14,adjust=False).mean()/atr_s
ndi = 100*pd.Series(ndm,index=df.index).ewm(span=14,adjust=False).mean()/atr_s
dx = 100*(pdi-ndi).abs()/(pdi+ndi).clip(lower=1e-9)
df['adx14'] = dx.ewm(span=14, adjust=False).mean()

# Stochastic(14,3)
low14 = df['low'].rolling(14).min()
high14 = df['high'].rolling(14).max()
df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14).clip(lower=1e-9)

# D1 EMA20 slope
d1 = df.set_index('ts').resample('1D').agg(
    close=('close','last')).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_up'] = (asia['asia_net'] > 0).astype(int)
asia['prior3_up'] = asia['asia_up'].shift(1) + asia['asia_up'].shift(2) + asia['asia_up'].shift(3)

# Close06 — last bar of Asia (hour 6)
bar06 = df[df['hour']==6][['date','close']].rename(columns={'close':'close06'})

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07['bar07_range_atr'] = (bar07['high07'] - bar07['low07']) / bar07['atr14'].clip(lower=1e-9)
bar07 = bar07[['date','open07','high07','low07','close07',
               'bar07_range_atr',
               'atr14','atr14_pct','ema120_slope','adx14','stoch_k','dow','month']]

intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = bar07.merge(asia, on='date').merge(bar06, on='date', how='left')
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)

# Overnight gap: open07 - close06 (positive = gap up = favors SHORT)
entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['overnight_gap_atr'] = entry['overnight_gap'] / entry['atr14'].clip(lower=1e-9)

def sim(ep, atr, date):
    stop_px = ep + 0.80*atr
    for hour, high, open_px in sorted(intra_dict.get(date, [])):
        if high >= stop_px: return stop_px, True
    return bar21_dict.get(date, ep), False

def run_on_mask(mask):
    results = []
    for _, row in entry[mask].iterrows():
        ep = row['open07']; atr = row['atr14']; date = row['date_key']
        exit_px, stopped = sim(ep, atr, date)
        pnl = (ep - exit_px) / ep - COST
        results.append({'year': row['year'], 'pnl': pnl})
    if not results: return {'n':0,'pf':0,'avg':0,'win':0,'by_year':{}}
    r = pd.DataFrame(results)
    w = r[r['pnl']>0]['pnl'].sum(); l = abs(r[r['pnl']<0]['pnl'].sum())
    pf = w/l if l>0 else float('inf')
    by_yr = {yr: round(g[g['pnl']>0]['pnl'].sum()/max(abs(g[g['pnl']<0]['pnl'].sum()),1e-10),2)
             for yr, g in r.groupby('year')}
    return {'n':len(r),'pf':round(pf,2),'avg':round(r['pnl'].mean()*100,3),
            'win':round((r['pnl']>0).mean()*100,1),'by_year':by_yr}

def pr(label, r):
    yr = ' | '.join(f"{y}: PF={v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%, win={r['win']}%")
    if yr: print(f"    {yr}")

base = ((entry['ema120_slope']<0)&(entry['adx14']<30)&(entry['atr14_pct']<0.75)&
        (entry['atr14']>=0.0005)&(entry['dow'].isin([2,3]))&
        (entry['asia_net']>=0.25*entry['atr14']))

c53b = base & (entry['stoch_k'] < 60) & (entry['d1_slope'] < 0)

print("="*65)
print("BASELINE")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))
pr("C53b (SK<60 + D1slope<0)", run_on_mask(c53b))

print("\n"+"="*65)
print("C56a: THREE-FILTER COMBOS FROM C53b")
print("="*65)
consec = base & (entry['prior3_up'] <= 1)
atr7pip = base & (entry['atr14'] >= 0.0007)
skipq2 = base & (entry['month'].isin([1,2,3,7,8,9,10,11,12]))

c53b_c43 = c53b & (entry['prior3_up'] <= 1)
c53b_atr7 = c53b & (entry['atr14'] >= 0.0007)
c53b_skipq2 = c53b & (entry['month'].isin([1,2,3,7,8,9,10,11,12]))

print(f"\n  C53b: n={c53b.sum()}")
print(f"  C53b + C43 (0-1 Asia up): n={c53b_c43.sum()}")
print(f"  C53b + ATR>=7pip: n={c53b_atr7.sum()}")
print(f"  C53b + skip Q2: n={c53b_skipq2.sum()}")
print()
pr("C53b (SK<60+D1)", run_on_mask(c53b))
pr("C53b + 0-1 prior Asia up (C43)", run_on_mask(c53b_c43))
pr("C53b + ATR>=7pip (C46c)", run_on_mask(c53b_atr7))
pr("C53b + skip Q2 (C42)", run_on_mask(c53b_skipq2))

print("\n"+"="*65)
print("C56b: BAR07 RANGE SIZE vs ATR")
print("="*65)
r07_base = entry.loc[base, 'bar07_range_atr'].dropna()
print(f"\n  Bar07 range/ATR on {base.sum()} qualifying trades:")
print(f"  mean={r07_base.mean():.3f}, median={r07_base.median():.3f}")
print(f"  <0.3: {(r07_base<0.3).sum()}, 0.3-0.5: {((r07_base>=0.3)&(r07_base<0.5)).sum()}, "
      f"0.5-0.8: {((r07_base>=0.5)&(r07_base<0.8)).sum()}, >=0.8: {(r07_base>=0.8).sum()}")

# Small bar = indecision, large bar = strong directional move
r07_small = base & (entry['bar07_range_atr'] < 0.4)
r07_large = base & (entry['bar07_range_atr'] >= 0.4)
r07_mid = base & (entry['bar07_range_atr'].between(0.3, 0.6))

print(f"\n  Small bar (<0.4×ATR): n={r07_small.sum()}, Large bar (>=0.4×ATR): n={r07_large.sum()}")
print()
pr("Small bar (<0.4×ATR)", run_on_mask(r07_small))
pr("Large bar (>=0.4×ATR)", run_on_mask(r07_large))
pr("SK<60 + small bar", run_on_mask(base & (entry['stoch_k']<60) & (entry['bar07_range_atr']<0.4)))
pr("SK<60 + large bar", run_on_mask(base & (entry['stoch_k']<60) & (entry['bar07_range_atr']>=0.4)))

print("\n"+"="*65)
print("C56c: OVERNIGHT GAP (close06 to open07)")
print("="*65)
gap_base = entry.loc[base, 'overnight_gap_atr'].dropna()
print(f"\n  Overnight gap/ATR on {base.sum()} qualifying trades:")
print(f"  mean={gap_base.mean():.4f}, median={gap_base.median():.4f}")
print(f"  negative (gap down): {(gap_base<0).sum()}, positive (gap up): {(gap_base>0).sum()}")
print(f"  >+0.05×ATR: {(gap_base>0.05).sum()}, <-0.05×ATR: {(gap_base<-0.05).sum()}")

gap_up = base & (entry['overnight_gap'] > 0)
gap_dn = base & (entry['overnight_gap'] < 0)
gap_up_sig = base & (entry['overnight_gap_atr'] > 0.05)  # meaningful gap up
gap_dn_sig = base & (entry['overnight_gap_atr'] < -0.05)  # meaningful gap down

print(f"\n  Gap up (any): n={gap_up.sum()}, Gap down: n={gap_dn.sum()}")
print(f"  Gap up >5%ATR: n={gap_up_sig.sum()}, Gap down >5%ATR: n={gap_dn_sig.sum()}")
print()
pr("Gap up (any)", run_on_mask(gap_up))
pr("Gap down (any)", run_on_mask(gap_dn))
pr("Gap up >5%ATR", run_on_mask(gap_up_sig))
pr("Gap down >5%ATR", run_on_mask(gap_dn_sig))
pr("SK<60 + gap up any", run_on_mask(base & (entry['stoch_k']<60) & (entry['overnight_gap']>0)))
pr("SK<60 + gap down any", run_on_mask(base & (entry['stoch_k']<60) & (entry['overnight_gap']<=0)))

print("\nDone.")
