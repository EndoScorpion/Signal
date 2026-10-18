"""
EURUSD Cycle C53 — Stochastic Combos + Williams %R
C53a: Stoch K<60 × C48b (bar07_bearish)
C53b: Stoch K<60 × C25b (D1 slope<0)
C53c: Williams %R(14) at entry — range-position indicator
C53d: Stoch K<60 × RSI<55 intersection vs union — clarifying collinearity
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

# Williams %R(14): -100*(high14 - close)/(high14 - low14)
# Note: WR = -(100 - stoch_k), so WR = stoch_k - 100
# WR range: -100 (oversold) to 0 (overbought)
df['willr'] = -100 * (high14 - df['close']) / (high14 - low14).clip(lower=1e-9)
# WR near 0 = overbought, WR near -100 = oversold
# For our SHORT: we WANT oversold (WR < -50 means not overbought)

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
               'atr14','atr14_pct','ema120_slope','adx14','rsi14','stoch_k','stoch_d','willr','dow','month']]

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

print("="*65)
print("BASELINE")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))

print("\n"+"="*65)
print("C53a: Stoch K<60 × C48b (bar07_bearish)")
print("="*65)
sk60 = base & (entry['stoch_k'] < 60)
b07b = base & (entry['bar07_bearish'] == True)
sk60_b07b = base & (entry['stoch_k'] < 60) & (entry['bar07_bearish'] == True)
sk60_no_b07b = base & (entry['stoch_k'] < 60) & (entry['bar07_bearish'] == False)
sk_hi_b07b = base & (entry['stoch_k'] >= 60) & (entry['bar07_bearish'] == True)

print(f"\n  Stoch K<60: n={sk60.sum()}, bar07_bearish: n={b07b.sum()}")
print(f"  Both: n={sk60_b07b.sum()}, SK<60 only: n={sk60_no_b07b.sum()}, bar07b only: n={sk_hi_b07b.sum()}")
print()
pr("Stoch K<60 alone", run_on_mask(sk60))
pr("bar07_bearish alone", run_on_mask(b07b))
pr("Stoch K<60 + bar07_bearish", run_on_mask(sk60_b07b))
pr("Stoch K<60, bar07_bullish", run_on_mask(sk60_no_b07b))
pr("Stoch K>=60 + bar07_bearish", run_on_mask(sk_hi_b07b))

print("\n"+"="*65)
print("C53b: Stoch K<60 × C25b (D1 slope<0)")
print("="*65)
d1_neg = base & (entry['d1_slope'] < 0)
sk60_d1 = base & (entry['stoch_k'] < 60) & (entry['d1_slope'] < 0)
sk_hi_d1 = base & (entry['stoch_k'] >= 60) & (entry['d1_slope'] < 0)

print(f"\n  Stoch K<60: n={sk60.sum()}, D1 slope<0: n={d1_neg.sum()}")
print(f"  Both: n={sk60_d1.sum()}, SK>=60 + D1neg: n={sk_hi_d1.sum()}")
print()
pr("Stoch K<60 alone", run_on_mask(sk60))
pr("D1 slope<0 (C25b)", run_on_mask(d1_neg))
pr("Stoch K<60 + D1 slope<0", run_on_mask(sk60_d1))
pr("Stoch K>=60 + D1 slope<0", run_on_mask(sk_hi_d1))

print("\n"+"="*65)
print("C53c: WILLIAMS %R(14) AT ENTRY")
print("="*65)
wr_base = entry.loc[base, 'willr'].dropna()
print(f"\n  Williams %R on {base.sum()} qualifying trades:")
print(f"  mean={wr_base.mean():.1f}, median={wr_base.median():.1f}")
print(f"  <-70: {(wr_base<-70).sum()}, -70 to -50: {((wr_base>=-70)&(wr_base<-50)).sum()}, "
      f"-50 to -30: {((wr_base>=-50)&(wr_base<-30)).sum()}, >-30: {(wr_base>=-30).sum()}")

# WR: -100 to 0. WR < -50 means close in lower half = not overbought
# This is exactly (1 - stoch_k/100) * -100... let's verify
# WR = -100 * (H14 - C) / (H14 - L14) = stoch_k - 100
wr_lo = base & (entry['willr'] < -40)   # not overbought (lower 60% of range)
wr_hi = base & (entry['willr'] >= -40)  # overbought (upper 40% of range)
wr_50 = base & (entry['willr'] < -50)

print(f"\n  WR<-40: n={wr_lo.sum()}, WR>=-40: n={wr_hi.sum()}, WR<-50: n={wr_50.sum()}")
print()
pr("WR<-40 (not overbought)", run_on_mask(wr_lo))
pr("WR>=-40 (overbought)", run_on_mask(wr_hi))
pr("WR<-50 (midpoint)", run_on_mask(wr_50))

# Verify WR = StochK - 100 relationship
print("\n  Checking WR vs Stoch K correspondence:")
print(f"  WR<-40 ≈ StochK<60: WR<-40 has {wr_lo.sum()} trades, SK<60 has {sk60.sum()} trades")
overlap_wr_sk = (base & (entry['willr'] < -40) & (entry['stoch_k'] < 60)).sum()
print(f"  Overlap: {overlap_wr_sk} (should match WR<-40 if identical)")

print("\nDone.")
