"""
EURUSD Cycle C58 — Asia peak hour, Wed vs Thu, prior London direction
C58a: Asia peak hour — when did Asia reach its high? (early vs late peak)
C58b: Wed vs Thu breakdown — do both days contribute equally?
C58c: Prior London session direction — was yesterday 07:00-21:00 bearish?
C58d: Asia range width — wide vs narrow range relative to ATR
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

# Asia session: hours 0-6, find high, high hour, range
asia_bars = df[df['hour'].between(0,6)].copy()

# For each day find the hour of the Asia high
asia_high_hour = (asia_bars.sort_values(['date','high'], ascending=[True,False])
                  .groupby('date').first()[['hour']].rename(columns={'hour':'asia_peak_hour'}))

asia = asia_bars.groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']
asia['asia_up'] = (asia['asia_net'] > 0).astype(int)
asia = asia.merge(asia_high_hour, on='date', how='left')

# Prior London session direction: yesterday's open07 vs close21
bar07_raw = df[df['hour']==7][['date','open']].rename(columns={'open':'open07_london'})
bar21_raw = df[df['hour']==21][['date','open']].rename(columns={'open':'close21_london'})
london = bar07_raw.merge(bar21_raw, on='date', how='inner')
london['london_bear'] = (london['close21_london'] < london['open07_london']).astype(int)
london['date'] = pd.to_datetime(london['date'])
london['next_date'] = london['date'] + pd.Timedelta(days=1)
# Map prior day's London direction to next trading day
# We need: for each qualifying day, was the PREVIOUS day's London session bearish?
# Build a dict: date -> prior_london_bear
london_bear_dict = dict(zip(london['date'].dt.date, london['london_bear']))

# Close06 — last bar of Asia
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

entry = bar07.merge(asia, on='date').merge(bar06, on='date', how='left')
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)

entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['no_gap_up'] = entry['overnight_gap'] <= 0

# Prior London bear: was yesterday's 07:00-21:00 range bearish?
# Look up (date - 1 calendar day) in london_bear_dict
# Use prior business day: find previous date with a London session
import datetime
entry['prior_london_bear'] = entry['date_key'].apply(
    lambda d: london_bear_dict.get(d - datetime.timedelta(days=1),
              london_bear_dict.get(d - datetime.timedelta(days=2),
              london_bear_dict.get(d - datetime.timedelta(days=3), np.nan))))

# Asia range / ATR
entry['asia_range_atr'] = entry['asia_range'] / entry['atr14'].clip(lower=1e-9)

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
print("C58a: ASIA PEAK HOUR (when did Asia reach its high?)")
print("="*65)
peak_base = entry.loc[base, 'asia_peak_hour'].dropna()
print(f"\n  Asia peak hour on {base.sum()} qualifying trades:")
print(f"  mean={peak_base.mean():.1f}, median={peak_base.median():.1f}")
for h in sorted(peak_base.unique()):
    print(f"  Hour {h}: {(peak_base==h).sum()} trades")

# Early peak (hours 0-3) = Asia topped out early, consolidation before London
# Late peak (hours 4-6) = Asia still rising into the close, momentum fresh
peak_early = base & (entry['asia_peak_hour'] <= 3)  # peaked 00:00-03:59
peak_late = base & (entry['asia_peak_hour'] >= 4)   # peaked 04:00-06:59
peak_mid = base & (entry['asia_peak_hour'].between(2,4))

print(f"\n  Early peak (hrs 0-3): n={peak_early.sum()}, Late peak (hrs 4-6): n={peak_late.sum()}")
print()
pr("Asia peak early (hrs 0-3)", run_on_mask(peak_early))
pr("Asia peak late (hrs 4-6)", run_on_mask(peak_late))
pr("C53b + early peak", run_on_mask(c53b & peak_early))
pr("C53b + late peak", run_on_mask(c53b & peak_late))
pr("no gap up + early peak", run_on_mask(base & entry['no_gap_up'] & peak_early))
pr("no gap up + late peak", run_on_mask(base & entry['no_gap_up'] & peak_late))

print("\n"+"="*65)
print("C58b: WED vs THU BREAKDOWN")
print("="*65)
wed = base & (entry['dow'] == 2)
thu = base & (entry['dow'] == 3)
print(f"\n  Wednesday: n={wed.sum()}, Thursday: n={thu.sum()}")
print()
pr("Wednesday only", run_on_mask(wed))
pr("Thursday only", run_on_mask(thu))
pr("C53b Wed", run_on_mask(c53b & (entry['dow']==2)))
pr("C53b Thu", run_on_mask(c53b & (entry['dow']==3)))
pr("no gap up Wed", run_on_mask(base & entry['no_gap_up'] & (entry['dow']==2)))
pr("no gap up Thu", run_on_mask(base & entry['no_gap_up'] & (entry['dow']==3)))

print("\n"+"="*65)
print("C58c: PRIOR LONDON SESSION DIRECTION")
print("="*65)
# Prior day's 07:00-21:00: if bearish, confirms SHORT context
prior_bear = base & (entry['prior_london_bear'] == 1)
prior_bull = base & (entry['prior_london_bear'] == 0)
print(f"\n  Prior London bear: n={prior_bear.sum()}, bull: n={prior_bull.sum()}")
print(f"  Missing prior data: n={(entry['prior_london_bear'].isna() & base).sum()}")
print()
pr("Prior London bearish", run_on_mask(prior_bear))
pr("Prior London bullish", run_on_mask(prior_bull))
pr("C53b + prior bear", run_on_mask(c53b & (entry['prior_london_bear']==1)))
pr("C53b + prior bull", run_on_mask(c53b & (entry['prior_london_bear']==0)))
pr("no gap up + prior bear", run_on_mask(base & entry['no_gap_up'] & (entry['prior_london_bear']==1)))

print("\n"+"="*65)
print("C58d: ASIA RANGE WIDTH vs ATR")
print("="*65)
arange_base = entry.loc[base, 'asia_range_atr'].dropna()
print(f"\n  Asia range/ATR on {base.sum()} qualifying trades:")
print(f"  mean={arange_base.mean():.3f}, median={arange_base.median():.3f}")
print(f"  <0.5: {(arange_base<0.5).sum()}, 0.5-1.0: {((arange_base>=0.5)&(arange_base<1.0)).sum()}, "
      f">=1.0: {(arange_base>=1.0).sum()}")

# Wide Asia range = strong overnight conviction
# Narrow = choppy overnight, less reliable setup
arange_wide = base & (entry['asia_range_atr'] >= 0.8)
arange_narrow = base & (entry['asia_range_atr'] < 0.8)
arange_very_wide = base & (entry['asia_range_atr'] >= 1.2)

print(f"\n  Wide (>=0.8×ATR): n={arange_wide.sum()}, Narrow (<0.8×ATR): n={arange_narrow.sum()}")
print(f"  Very wide (>=1.2×ATR): n={arange_very_wide.sum()}")
print()
pr("Asia wide range (>=0.8×ATR)", run_on_mask(arange_wide))
pr("Asia narrow range (<0.8×ATR)", run_on_mask(arange_narrow))
pr("Asia very wide (>=1.2×ATR)", run_on_mask(arange_very_wide))
pr("C53b + wide range", run_on_mask(c53b & arange_wide))
pr("C53b + narrow range", run_on_mask(c53b & arange_narrow))
pr("no gap up + wide range", run_on_mask(base & entry['no_gap_up'] & arange_wide))
pr("no gap up + narrow range", run_on_mask(base & entry['no_gap_up'] & arange_narrow))

print("\nDone.")
