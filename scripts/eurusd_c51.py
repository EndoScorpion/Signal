"""
EURUSD Cycle C51 — RSI at Entry, Pending Combo Tests, Asia-to-Entry Extension
C51a: RSI(14) at 07:00 — does high RSI (overbought euro) predict better fade?
C51b: C48b (bar07 bearish) × C46c (ATR≥7pip) — two pending candidates combined
C51c: Distance from Asia close (06:00) to 07:00 open, normalized by ATR
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

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07['bar07_bearish'] = bar07['close07'] < bar07['open07']
bar07 = bar07[['date','open07','high07','low07','close07','bar07_bearish',
               'atr14','atr14_pct','ema120_slope','adx14','rsi14','dow','month']]

# Intra-day monitoring
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
# Asia-to-07:00 extension: how far did price rise from asia_close to open07
entry['extend_pips'] = (entry['open07'] - entry['asia_close']) / 0.0001
entry['extend_atr'] = (entry['open07'] - entry['asia_close']) / entry['atr14']

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

# RSI distribution on qualifying trades
rsi_base = entry.loc[base, 'rsi14'].dropna()
print(f"\n  RSI(14) on {base.sum()} qualifying trades:")
print(f"  mean={rsi_base.mean():.1f}, median={rsi_base.median():.1f}, "
      f"min={rsi_base.min():.1f}, max={rsi_base.max():.1f}")
print(f"  <50: {(rsi_base<50).sum()}, 50-60: {((rsi_base>=50)&(rsi_base<60)).sum()}, "
      f"60-70: {((rsi_base>=60)&(rsi_base<70)).sum()}, >=70: {(rsi_base>=70).sum()}")

print("\n"+"="*65)
print("C51a: RSI(14) AT 07:00 ENTRY")
print("="*65)
print("\n(Short: fading Asia rally — does higher RSI = more overbought = better fade?)")

rsi50 = base & (entry['rsi14'] >= 50)
rsi60 = base & (entry['rsi14'] >= 60)
rsi65 = base & (entry['rsi14'] >= 65)
rsi70 = base & (entry['rsi14'] >= 70)
rsi_lo = base & (entry['rsi14'] < 55)
rsi_hi = base & (entry['rsi14'] >= 55)

print(f"\n  RSI>=50: n={rsi50.sum()}, RSI>=60: n={rsi60.sum()}, "
      f"RSI>=65: n={rsi65.sum()}, RSI>=70: n={rsi70.sum()}")
print(f"  RSI<55: n={rsi_lo.sum()}, RSI>=55: n={rsi_hi.sum()}")
print()
pr("RSI>=50", run_on_mask(rsi50))
pr("RSI>=55", run_on_mask(rsi_hi))
pr("RSI>=60", run_on_mask(rsi60))
pr("RSI>=65", run_on_mask(rsi65))
pr("RSI>=70", run_on_mask(rsi70))
pr("RSI<55 (low RSI)", run_on_mask(rsi_lo))

print("\n"+"="*65)
print("C51b: C48b (bar07_bearish) × C46c (ATR>=7pip) COMBO")
print("="*65)
print("\n(Both are pending candidates — testing their intersection)")
b07b = entry['bar07_bearish'] == True
atr7 = entry['atr14'] >= 0.0007

b07b_base = base & b07b
atr7_base = base & atr7
combo = base & b07b & atr7

print(f"\n  bar07_bearish alone: n={b07b_base.sum()}")
print(f"  ATR>=7pip alone: n={atr7_base.sum()}")
print(f"  Both together: n={combo.sum()}")
print()
pr("bar07_bearish (C48b)", run_on_mask(b07b_base))
pr("ATR>=7pip (C46c)", run_on_mask(atr7_base))
pr("C48b + C46c combo", run_on_mask(combo))

print("\n"+"="*65)
print("C51c: ASIA-TO-ENTRY EXTENSION")
print("="*65)
print("\n(How far did price rise from Asia close [06:00] to 07:00 open, in ATR units?)")

ext_base = entry.loc[base, 'extend_atr'].dropna()
print(f"\n  Extension in ATR on {base.sum()} qualifying trades:")
print(f"  mean={ext_base.mean():.3f}, median={ext_base.median():.3f}, "
      f"min={ext_base.min():.3f}, max={ext_base.max():.3f}")
pct25 = ext_base.quantile(0.25)
pct75 = ext_base.quantile(0.75)
print(f"  Q1={pct25:.3f}, Q3={pct75:.3f}")

# Buckets
ext_lo = base & (entry['extend_atr'] < 0.1)   # small extension
ext_mid = base & (entry['extend_atr'].between(0.1, 0.3))
ext_hi = base & (entry['extend_atr'] > 0.3)    # large extension

print(f"\n  extend<0.1×ATR: n={ext_lo.sum()}, 0.1-0.3: n={ext_mid.sum()}, >0.3: n={ext_hi.sum()}")

# Also try a split near median
med = ext_base.median()
ext_below = base & (entry['extend_atr'] < med)
ext_above = base & (entry['extend_atr'] >= med)
print(f"\n  Below median ({med:.3f}): n={ext_below.sum()}, Above median: n={ext_above.sum()}")
print()
pr("Extension <0.1×ATR", run_on_mask(ext_lo))
pr("Extension 0.1-0.3×ATR", run_on_mask(ext_mid))
pr("Extension >0.3×ATR", run_on_mask(ext_hi))
pr(f"Extension below median ({med:.3f})", run_on_mask(ext_below))
pr(f"Extension above median ({med:.3f})", run_on_mask(ext_above))

print("\nDone.")
