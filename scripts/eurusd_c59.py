"""
EURUSD Cycle C59 — Asia velocity, H4 pre-entry bar, EMA30(H1) slope
C59a: Asia velocity (asia_net/asia_range) — directional quality of Asia rally
C59b: H4 pre-entry bar (04:00 H4) — bearish 4h bar before London open?
C59c: EMA30(H1) slope — faster intraday trend filter
C59d: Asia net magnitude tiers — does a larger Asia rally predict better SHORT?
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
df['ema30'] = df['close'].ewm(span=30, adjust=False).mean()
df['ema30_slope'] = df['ema30'].diff()

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

# Asia session
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']
# Velocity: fraction of range that was directional net movement
# 1.0 = moved straight up with no pullback; 0.0 = no net direction despite wide range
asia['asia_velocity'] = asia['asia_net'] / asia['asia_range'].clip(lower=1e-9)

# H4 pre-entry bar: resample to 4H, take the bar ending at 07:59 (04:00-07:59)
# Since we're UTC, H4 bars aligned to 00:00 UTC: 00-03, 04-07, 08-11, ...
# The 04:00 H4 bar is hours 4,5,6 (Asia close) — actually covers 04:00-07:59
# Let's use hours 4-6 only (pre-07:00 bars) since we don't have the 07:00 close yet
bar_h4_pre = df[df['hour'].between(4,6)].groupby('date').agg(
    h4_open=('open','first'),
    h4_close=('close','last'),
    h4_high=('high','max'),
    h4_low=('low','min')).reset_index()
bar_h4_pre['h4_bear'] = (bar_h4_pre['h4_close'] < bar_h4_pre['h4_open']).astype(int)
bar_h4_pre['h4_net_atr'] = (bar_h4_pre['h4_close'] - bar_h4_pre['h4_open'])

# EMA30 slope at 07:00 bar
bar07_ema30 = df[df['hour']==7][['date','ema30_slope']].rename(columns={'ema30_slope':'ema30_slope_07'})

# Close06
bar06 = df[df['hour']==6][['date','close']].rename(columns={'close':'close06'})

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','stoch_k','dow','month']]

intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = (bar07.merge(asia, on='date')
             .merge(bar06, on='date', how='left')
             .merge(bar_h4_pre, on='date', how='left')
             .merge(bar07_ema30, on='date', how='left'))
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)

entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['no_gap_up'] = entry['overnight_gap'] <= 0
entry['asia_net_atr'] = entry['asia_net'] / entry['atr14'].clip(lower=1e-9)

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
print("BASELINE + C53b")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))
pr("C53b (SK<60+D1slope<0)", run_on_mask(c53b))

print("\n"+"="*65)
print("C59a: ASIA VELOCITY (asia_net / asia_range)")
print("="*65)
vel_base = entry.loc[base, 'asia_velocity'].dropna()
print(f"\n  Asia velocity on {base.sum()} qualifying trades:")
print(f"  mean={vel_base.mean():.3f}, median={vel_base.median():.3f}")
print(f"  <0.2: {(vel_base<0.2).sum()}, 0.2-0.4: {((vel_base>=0.2)&(vel_base<0.4)).sum()}, "
      f"0.4-0.6: {((vel_base>=0.4)&(vel_base<0.6)).sum()}, >=0.6: {(vel_base>=0.6).sum()}")

# High velocity = directional Asia (good SHORT: momentum intact)
# Low velocity = choppy Asia that happened to close up
vel_hi = base & (entry['asia_velocity'] >= 0.4)
vel_lo = base & (entry['asia_velocity'] < 0.4)
vel_very_hi = base & (entry['asia_velocity'] >= 0.6)

print(f"\n  High velocity (>=0.4): n={vel_hi.sum()}, Low velocity (<0.4): n={vel_lo.sum()}")
print(f"  Very high (>=0.6): n={vel_very_hi.sum()}")
print()
pr("High Asia velocity (>=0.4)", run_on_mask(vel_hi))
pr("Low Asia velocity (<0.4)", run_on_mask(vel_lo))
pr("Very high velocity (>=0.6)", run_on_mask(vel_very_hi))
pr("C53b + high velocity", run_on_mask(c53b & vel_hi))
pr("C53b + low velocity", run_on_mask(c53b & vel_lo))
pr("no gap up + high velocity", run_on_mask(base & entry['no_gap_up'] & vel_hi))
pr("no gap up + low velocity", run_on_mask(base & entry['no_gap_up'] & vel_lo))

print("\n"+"="*65)
print("C59b: H4 PRE-ENTRY BAR (hours 4-6, before 07:00)")
print("="*65)
h4_base = entry.loc[base, 'h4_bear'].dropna()
print(f"\n  H4 pre-entry bar direction on {base.sum()} qualifying trades:")
print(f"  Bearish (close<open): {(h4_base==1).sum()}, Bullish: {(h4_base==0).sum()}")

h4_bear = base & (entry['h4_bear'] == 1)
h4_bull = base & (entry['h4_bear'] == 0)

print(f"\n  H4 bear (hrs 4-6 down): n={h4_bear.sum()}, H4 bull: n={h4_bull.sum()}")
print()
pr("H4 pre-entry bearish (hrs 4-6)", run_on_mask(h4_bear))
pr("H4 pre-entry bullish (hrs 4-6)", run_on_mask(h4_bull))
pr("C53b + H4 bear", run_on_mask(c53b & h4_bear))
pr("C53b + H4 bull", run_on_mask(c53b & h4_bull))
pr("no gap up + H4 bear", run_on_mask(base & entry['no_gap_up'] & h4_bear))
pr("no gap up + H4 bull", run_on_mask(base & entry['no_gap_up'] & h4_bull))

print("\n"+"="*65)
print("C59c: EMA30(H1) SLOPE AT 07:00")
print("="*65)
ema30_base = entry.loc[base, 'ema30_slope_07'].dropna()
print(f"\n  EMA30(H1) slope on {base.sum()} qualifying trades:")
print(f"  Negative: {(ema30_base<0).sum()}, Positive: {(ema30_base>=0).sum()}")
print(f"  mean={ema30_base.mean():.6f}, median={ema30_base.median():.6f}")

ema30_neg = base & (entry['ema30_slope_07'] < 0)
ema30_pos = base & (entry['ema30_slope_07'] >= 0)

print(f"\n  EMA30 slope negative: n={ema30_neg.sum()}, positive: n={ema30_pos.sum()}")
print()
pr("EMA30(H1) slope negative", run_on_mask(ema30_neg))
pr("EMA30(H1) slope positive", run_on_mask(ema30_pos))
pr("C53b + EMA30 neg", run_on_mask(c53b & ema30_neg))
pr("SK<60 + EMA30 neg", run_on_mask(base & (entry['stoch_k']<60) & ema30_neg))
pr("no gap up + EMA30 neg", run_on_mask(base & entry['no_gap_up'] & ema30_neg))

print("\n"+"="*65)
print("C59d: ASIA NET MAGNITUDE TIERS (asia_net / ATR)")
print("="*65)
anet_base = entry.loc[base, 'asia_net_atr'].dropna()
print(f"\n  Asia net/ATR on {base.sum()} qualifying trades:")
print(f"  mean={anet_base.mean():.3f}, median={anet_base.median():.3f}")
print(f"  0.25-0.4: {((anet_base>=0.25)&(anet_base<0.4)).sum()}, "
      f"0.4-0.6: {((anet_base>=0.4)&(anet_base<0.6)).sum()}, "
      f">=0.6: {(anet_base>=0.6).sum()}")

# Larger asia_net = stronger overnight rally = more to fade?
# Or larger rally = overdone = already exhausted?
anet_small = base & (entry['asia_net_atr'].between(0.25, 0.4))  # minimal qualifying
anet_mid = base & (entry['asia_net_atr'].between(0.4, 0.7))
anet_large = base & (entry['asia_net_atr'] >= 0.7)

print(f"\n  Small net (0.25-0.4×ATR): n={anet_small.sum()}, "
      f"Mid (0.4-0.7): n={anet_mid.sum()}, Large (>=0.7): n={anet_large.sum()}")
print()
pr("Asia net small (0.25-0.4×ATR)", run_on_mask(anet_small))
pr("Asia net mid (0.4-0.7×ATR)", run_on_mask(anet_mid))
pr("Asia net large (>=0.7×ATR)", run_on_mask(anet_large))
pr("C53b + large net", run_on_mask(c53b & anet_large))
pr("no gap up + large net", run_on_mask(base & entry['no_gap_up'] & anet_large))
pr("no gap up + small net", run_on_mask(base & entry['no_gap_up'] & anet_small))

print("\nDone.")
