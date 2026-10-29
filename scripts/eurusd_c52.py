"""
EURUSD Cycle C52 — RSI<55 Combos + Stochastic
C52a: RSI<55 × C48b (bar07_bearish) — two best standalone signals
C52b: RSI<55 × C25b (D1 EMA slope<0) — combining momentum filters
C52c: Stochastic(14,3) K and D at entry
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

# RSI(14)
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = (-delta).clip(lower=0)
avg_gain = gain.ewm(span=14, adjust=False).mean()
avg_loss = loss.ewm(span=14, adjust=False).mean()
rs = avg_gain / avg_loss.clip(lower=1e-9)
df['rsi14'] = 100 - 100 / (1 + rs)

# Stochastic(14,3)
low14 = df['low'].rolling(14).min()
high14 = df['high'].rolling(14).max()
df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14).clip(lower=1e-9)
df['stoch_d'] = df['stoch_k'].rolling(3).mean()

# D1 EMA20 slope
d1 = df.set_index('ts').resample('1D').agg(
    close=('close','last')).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07['bar07_bearish'] = bar07['close07'] < bar07['open07']
bar07 = bar07[['date','open07','high07','low07','close07','bar07_bearish',
               'atr14','atr14_pct','ema120_slope','adx14','rsi14','stoch_k','stoch_d','dow','month']]

intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = bar07.merge(asia, on='date')
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)

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

rsi_lo = base & (entry['rsi14'] < 55)
b07b = base & (entry['bar07_bearish'] == True)
d1_neg = base & (entry['d1_slope'] < 0)

print("="*65)
print("BASELINE")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))

print("\n"+"="*65)
print("C52a: RSI<55 × C48b (bar07_bearish)")
print("="*65)
rsi_lo_b07b = base & (entry['rsi14'] < 55) & (entry['bar07_bearish'] == True)
rsi_hi_b07b = base & (entry['rsi14'] >= 55) & (entry['bar07_bearish'] == True)
rsi_lo_no_b07b = base & (entry['rsi14'] < 55) & (entry['bar07_bearish'] == False)

print(f"\n  RSI<55 + bar07_bearish: n={rsi_lo_b07b.sum()}")
print(f"  RSI>=55 + bar07_bearish: n={rsi_hi_b07b.sum()}")
print(f"  RSI<55 + bar07_bullish: n={rsi_lo_no_b07b.sum()}")
print()
pr("RSI<55 (C51a)", run_on_mask(rsi_lo))
pr("bar07_bearish (C48b)", run_on_mask(b07b))
pr("RSI<55 + bar07_bearish", run_on_mask(rsi_lo_b07b))
pr("RSI>=55 + bar07_bearish", run_on_mask(rsi_hi_b07b))
pr("RSI<55 + bar07_bullish", run_on_mask(rsi_lo_no_b07b))

print("\n"+"="*65)
print("C52b: RSI<55 × C25b (D1 EMA slope<0)")
print("="*65)
rsi_lo_d1 = base & (entry['rsi14'] < 55) & (entry['d1_slope'] < 0)
rsi_hi_d1 = base & (entry['rsi14'] >= 55) & (entry['d1_slope'] < 0)

print(f"\n  D1 slope<0 alone: n={d1_neg.sum()}")
print(f"  RSI<55 alone: n={rsi_lo.sum()}")
print(f"  RSI<55 + D1 slope<0: n={rsi_lo_d1.sum()}")
print(f"  RSI>=55 + D1 slope<0: n={rsi_hi_d1.sum()}")
print()
pr("D1 slope<0 (C25b)", run_on_mask(d1_neg))
pr("RSI<55 (C51a)", run_on_mask(rsi_lo))
pr("RSI<55 + D1 slope<0", run_on_mask(rsi_lo_d1))
pr("RSI>=55 + D1 slope<0", run_on_mask(rsi_hi_d1))

print("\n"+"="*65)
print("C52c: STOCHASTIC(14,3) AT ENTRY")
print("="*65)
stoch_base = entry.loc[base, 'stoch_k'].dropna()
stoch_d_base = entry.loc[base, 'stoch_d'].dropna()
print(f"\n  Stoch K on {base.sum()} qualifying trades:")
print(f"  mean={stoch_base.mean():.1f}, median={stoch_base.median():.1f}")
print(f"  <30: {(stoch_base<30).sum()}, 30-50: {((stoch_base>=30)&(stoch_base<50)).sum()}, "
      f"50-70: {((stoch_base>=50)&(stoch_base<70)).sum()}, >=70: {(stoch_base>=70).sum()}")
print(f"  Stoch D mean={stoch_d_base.mean():.1f}, median={stoch_d_base.median():.1f}")

sk_lo = base & (entry['stoch_k'] < 50)
sk_hi = base & (entry['stoch_k'] >= 50)
sk_55 = base & (entry['stoch_k'] < 55)
sk_60 = base & (entry['stoch_k'] < 60)

print(f"\n  Stoch K<50: n={sk_lo.sum()}, K>=50: n={sk_hi.sum()}")
print(f"  Stoch K<55: n={sk_55.sum()}, K<60: n={sk_60.sum()}")
print()
pr("Stoch K<50", run_on_mask(sk_lo))
pr("Stoch K>=50", run_on_mask(sk_hi))
pr("Stoch K<55", run_on_mask(sk_55))
pr("Stoch K<60", run_on_mask(sk_60))

# Check if RSI and Stoch K are correlated
rsi_stoch_both = base & (entry['rsi14'] < 55) & (entry['stoch_k'] < 55)
print(f"\n  RSI<55 AND Stoch K<55: n={rsi_stoch_both.sum()}")
pr("RSI<55 AND Stoch K<55", run_on_mask(rsi_stoch_both))

print("\nDone.")
