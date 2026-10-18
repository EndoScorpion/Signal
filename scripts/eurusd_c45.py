"""
EURUSD Cycle C45 — ADX Threshold + Asia Net Strength Gradient
C45a: ADX threshold sweep (relax or tighten) to understand sensitivity + find more n
C45b: Asia net strength tiers (threshold above 0.25×ATR = stronger signal?)
C45c: Prior day direction (was yesterday bullish/bearish for EURUSD at 21:00?)
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
df['atr14_5d_ago'] = df['atr14'].shift(5)

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

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# Prior day: use the 21:00 bar (which is the exit bar; compare to prior day's 07:00 open)
# "Prior day direction" = was yesterday's session (07:00 to 21:00) bullish or bearish?
# Use: yesterday's 21:00 open vs yesterday's 07:00 open
bar07_all = df[df['hour']==7][['date','open']].rename(columns={'open':'open07_raw'})
bar21_all = df[df['hour']==21][['date','open']].rename(columns={'open':'open21_raw'})
day_dir = bar07_all.merge(bar21_all, on='date', how='inner')
day_dir['session_return'] = day_dir['open21_raw'] - day_dir['open07_raw']  # positive = EUR went up during session
day_dir['date_dt'] = pd.to_datetime(day_dir['date'])
day_dir = day_dir.sort_values('date_dt').reset_index(drop=True)
day_dir['prev_session_return'] = day_dir['session_return'].shift(1)
day_dir['prev_session_bearish'] = day_dir['prev_session_return'] < 0  # yesterday's session sold off

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','dow','month','atr14_5d_ago']]

intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = bar07.merge(asia, on='date').merge(
    day_dir[['date','prev_session_return','prev_session_bearish']], on='date', how='left')
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year

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
        results.append({'year': row['year'], 'pnl': pnl, 'stopped': stopped})
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

print("="*65)
print("BASELINE")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))

e_base = entry[base]
print(f"\nADX distribution on qualifying trades:")
print(f"  mean={e_base['adx14'].mean():.1f}, min={e_base['adx14'].min():.1f}, "
      f"max={e_base['adx14'].max():.1f}, p25={e_base['adx14'].quantile(0.25):.1f}, "
      f"p75={e_base['adx14'].quantile(0.75):.1f}")

print("\n"+"="*65)
print("C45a: ADX THRESHOLD SWEEP")
print("="*65)
print("\n(Base without ADX, to see full trade universe:)")
no_adx = ((entry['ema120_slope']<0)&(entry['atr14_pct']<0.75)&
          (entry['atr14']>=0.0005)&(entry['dow'].isin([2,3]))&
          (entry['asia_net']>=0.25*entry['atr14']))
r_no_adx = run_on_mask(no_adx)
pr("No ADX filter", r_no_adx)

print("\nADX threshold sweep (all other conditions same):")
for thresh in [15, 20, 25, 30, 35, 40, 45]:
    mask = ((entry['ema120_slope']<0)&(entry['adx14']<thresh)&(entry['atr14_pct']<0.75)&
            (entry['atr14']>=0.0005)&(entry['dow'].isin([2,3]))&
            (entry['asia_net']>=0.25*entry['atr14']))
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  ADX<{thresh}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\n(Excluded trades — ADX 30-45 only:)")
adx_high = ((entry['ema120_slope']<0)&(entry['adx14']>=30)&(entry['adx14']<45)&
            (entry['atr14_pct']<0.75)&(entry['atr14']>=0.0005)&(entry['dow'].isin([2,3]))&
            (entry['asia_net']>=0.25*entry['atr14']))
pr("ADX 30-45 (excluded zone)", run_on_mask(adx_high))

print("\n"+"="*65)
print("C45b: ASIA NET STRENGTH GRADIENT")
print("="*65)
print("\n(Base without asia_net threshold, for context:)")
no_asia = ((entry['ema120_slope']<0)&(entry['adx14']<30)&(entry['atr14_pct']<0.75)&
           (entry['atr14']>=0.0005)&(entry['dow'].isin([2,3]))&(entry['asia_net']>0))
pr("asia_net>0 (any positive)", run_on_mask(no_asia))

print("\nAsia net threshold sweep (multiples of ATR):")
for mult in [0.10, 0.15, 0.25, 0.35, 0.50, 0.75]:
    mask = ((entry['ema120_slope']<0)&(entry['adx14']<30)&(entry['atr14_pct']<0.75)&
            (entry['atr14']>=0.0005)&(entry['dow'].isin([2,3]))&
            (entry['asia_net']>=mult*entry['atr14']))
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  asia_net>={mult:.2f}xATR: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

# Tiers: strong vs moderate vs weak Asia move
strong = base & (entry['asia_net'] >= 0.50*entry['atr14'])
moderate = base & (entry['asia_net'] >= 0.25*entry['atr14']) & (entry['asia_net'] < 0.50*entry['atr14'])
print(f"\n  Strong Asia (>=0.5×ATR): n={strong.sum()}, moderate (0.25-0.5): n={moderate.sum()}")
pr("Strong Asia (>=0.5xATR)", run_on_mask(strong))
pr("Moderate Asia (0.25-0.5xATR)", run_on_mask(moderate))

print("\n"+"="*65)
print("C45c: PRIOR SESSION DIRECTION")
print("="*65)
e_base2 = entry[base]
psr = e_base2['prev_session_return']
print(f"\nPrior session return on qualifying trades: mean={psr.mean():.5f}, "
      f"pct_negative={(psr<0).mean()*100:.1f}%")

prev_bear = base & (entry['prev_session_bearish']==True)
prev_bull = base & (entry['prev_session_bearish']==False)
print(f"\n  Prev session bearish: n={prev_bear.sum()}, bullish: n={prev_bull.sum()}")
print("\n--- Prior session bearish (EUR fell yesterday 07:00-21:00) ---")
pr("prev session bearish", run_on_mask(prev_bear))
print("\n--- Prior session bullish (EUR rose yesterday 07:00-21:00) ---")
pr("prev session bullish", run_on_mask(prev_bull))

# Strength of prior session
print("\n  Prior session magnitude buckets:")
for mult_label, lo, hi in [("small",0,0.0003),("med",0.0003,0.0006),("large",0.0006,99)]:
    mask_bull_prev = base & (entry['prev_session_return'] >= lo) & (entry['prev_session_return'] < hi)
    r = run_on_mask(mask_bull_prev)
    print(f"    prev_return {lo:.4f} to {hi}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%")

print("\nDone.")
