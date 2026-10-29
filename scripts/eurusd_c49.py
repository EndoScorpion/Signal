"""
EURUSD Cycle C49 — 08:00 Entry + Bar07 Combos
C49a: Enter at 08:00 open when 07:00 bar was bearish (C48b implementation)
C49b: Bar07_bearish + top combos (D1 slope, skip Q2, ATR expanding)
C49c: Bar07_bearish overlap with C35 (bear07 open gap)
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
df['week'] = df['ts'].dt.isocalendar().week.astype(int)
df['isoyear'] = df['ts'].dt.isocalendar().year.astype(int)
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

# D1 EMA20 slope (C25b): resample to daily, compute EMA20
d1 = df.set_index('ts').resample('1D').agg(
    open=('open','first'), high=('high','max'), low=('low','min'), close=('close','last')
).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# Prior 3 Asia days consecutive (C43)
asia['asia_up'] = (asia['asia_net'] > 0).astype(int)
asia['asia_up_1d'] = asia['asia_up'].shift(1)
asia['asia_up_2d'] = asia['asia_up'].shift(2)
asia['asia_up_3d'] = asia['asia_up'].shift(3)
asia['prior3_up'] = asia['asia_up_1d'] + asia['asia_up_2d'] + asia['asia_up_3d']

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07['bar07_bearish'] = bar07['close07'] < bar07['open07']
# Bear07 (C35): open07 < prev_close
bar07['bear07'] = bar07['open07'] < bar07['prev_close']
bar07 = bar07[['date','open07','high07','low07','close07','bar07_bearish','bear07',
               'atr14','atr14_pct','ema120_slope','adx14','atr14_5d_ago','dow','month']]

# 08:00 bar (for C49a alternative entry)
bar08 = df[df['hour']==8][['date','open']].rename(columns={'open':'open08'})

# Stop/exit: check from 09:00 for 08:00 entries (hour.between(9,20))
intra_s_09 = df[df['hour'].between(9,20)][['date','hour','high','open']].copy()
intra_dict_09 = {}
for row in intra_s_09.itertuples():
    d = row.date
    if d not in intra_dict_09: intra_dict_09[d] = []
    intra_dict_09[d].append((row.hour, row.high, row.open))

# Standard stop dict (from 08:00, for 07:00 entry)
intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = bar07.merge(asia, on='date').merge(bar08, on='date', how='left')
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['quarter'] = ((entry['month'] - 1) // 3 + 1)
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)
entry['atr_expanding'] = entry['atr14'] > entry['atr14_5d_ago']

def sim07(ep, atr, date):
    stop_px = ep + 0.80*atr
    for hour, high, open_px in sorted(intra_dict.get(date, [])):
        if high >= stop_px: return stop_px, True
    return bar21_dict.get(date, ep), False

def sim08(ep, atr, date):
    stop_px = ep + 0.80*atr
    for hour, high, open_px in sorted(intra_dict_09.get(date, [])):
        if high >= stop_px: return stop_px, True
    return bar21_dict.get(date, ep), False

def run_on_mask(mask, use_ep='open07'):
    results = []
    for _, row in entry[mask].iterrows():
        ep = row[use_ep]
        if pd.isna(ep): continue
        atr = row['atr14']; date = row['date_key']
        sim_fn = sim08 if use_ep == 'open08' else sim07
        exit_px, stopped = sim_fn(ep, atr, date)
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
print("BASELINE (07:00 entry)")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))

print("\n"+"="*65)
print("C49a: 08:00 ENTRY WHEN 07:00 BAR WAS BEARISH")
print("="*65)
print("\n(Waits for 07:00 bar to confirm bearish close, enters at 08:00 open)")
print("(Stop monitored from 09:00 in this variant)")

b07bear_08entry = base & (entry['bar07_bearish']==True)
print(f"\n  Qualifying trades with bar07 bearish: n={b07bear_08entry.sum()}")

print("\n--- 07:00 bar, baseline (reference) ---")
pr("07:00 entry, bar07 bearish (from C48b)", run_on_mask(b07bear_08entry, 'open07'))
print("\n--- 08:00 entry on same qualifying trades ---")
pr("08:00 entry, bar07 bearish", run_on_mask(b07bear_08entry, 'open08'))

print("\n"+"="*65)
print("C49b: BAR07_BEARISH COMBOS WITH TOP CANDIDATES")
print("="*65)

b07b = base & (entry['bar07_bearish']==True)

# D1 slope + bar07 bearish
d1_b07b = b07b & (entry['d1_slope'] < 0)
print(f"\n  D1 slope<0 + bar07_bearish: n={d1_b07b.sum()}")
pr("D1slope + bar07_bearish", run_on_mask(d1_b07b))

# Skip Q2 + bar07 bearish
skipq2_b07b = b07b & (entry['quarter'] != 2)
print(f"\n  Skip Q2 + bar07_bearish: n={skipq2_b07b.sum()}")
pr("SkipQ2 + bar07_bearish", run_on_mask(skipq2_b07b))

# ATR expanding + bar07 bearish
atr_exp_b07b = b07b & (entry['atr_expanding']==True)
print(f"\n  ATR expanding + bar07_bearish: n={atr_exp_b07b.sum()}")
pr("ATR_exp + bar07_bearish", run_on_mask(atr_exp_b07b))

# 0-1 prior Asia up + bar07 bearish
consec_b07b = b07b & (entry['prior3_up'] <= 1)
print(f"\n  0-1 prior Asia up + bar07_bearish: n={consec_b07b.sum()}")
pr("0-1consec + bar07_bearish", run_on_mask(consec_b07b))

print("\n"+"="*65)
print("C49c: BAR07_BEARISH OVERLAP WITH C35 (BEAR07)")
print("="*65)
print("\n(C35: open07 < prev_close; C48b: close07 < open07 — what's the overlap?)")

both = base & (entry['bar07_bearish']==True) & (entry['bear07']==True)
b07b_only = base & (entry['bar07_bearish']==True) & (entry['bear07']==False)
bear07_only = base & (entry['bar07_bearish']==False) & (entry['bear07']==True)
neither = base & (entry['bar07_bearish']==False) & (entry['bear07']==False)

print(f"\n  Both bar07_bearish AND bear07: n={both.sum()}")
print(f"  bar07_bearish only (not bear07): n={b07b_only.sum()}")
print(f"  bear07 only (not bar07_bearish): n={bear07_only.sum()}")
print(f"  Neither: n={neither.sum()}")
print()
pr("Both signals", run_on_mask(both))
pr("bar07_bearish only", run_on_mask(b07b_only))
pr("bear07 only", run_on_mask(bear07_only))
pr("Neither (both fail)", run_on_mask(neither))

print("\nDone.")
