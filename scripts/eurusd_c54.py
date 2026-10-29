"""
EURUSD Cycle C54 — MACD, Stoch K<60 combos, EMA50 context
C54a: MACD(12,26,9) histogram at 07:00 — is momentum already negative?
C54b: Stoch K<60 × C43 (0-1 prior Asia up days)
C54c: Stoch K<60 × C42 (skip Q2)
C54d: H1 close vs EMA50 at 07:00 entry
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
df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()

up = df['high'].diff(); dn = -df['low'].diff()
pdm = np.where((up > dn) & (up > 0), up, 0.0)
ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
atr_s = df['tr'].ewm(span=14, adjust=False).mean()
pdi = 100*pd.Series(pdm,index=df.index).ewm(span=14,adjust=False).mean()/atr_s
ndi = 100*pd.Series(ndm,index=df.index).ewm(span=14,adjust=False).mean()/atr_s
dx = 100*(pdi-ndi).abs()/(pdi+ndi).clip(lower=1e-9)
df['adx14'] = dx.ewm(span=14, adjust=False).mean()

# MACD(12,26,9)
ema12 = df['close'].ewm(span=12, adjust=False).mean()
ema26 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = ema12 - ema26
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
df['macd_hist'] = df['macd'] - df['macd_signal']

# Stochastic(14,3)
low14 = df['low'].rolling(14).min()
high14 = df['high'].rolling(14).max()
df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14).clip(lower=1e-9)

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_up'] = (asia['asia_net'] > 0).astype(int)
asia['prior3_up'] = asia['asia_up'].shift(1) + asia['asia_up'].shift(2) + asia['asia_up'].shift(3)

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07['above_ema50'] = bar07['close07'] > bar07['ema50']
bar07 = bar07[['date','open07','high07','low07','close07','above_ema50',
               'atr14','atr14_pct','ema120_slope','adx14','stoch_k',
               'macd','macd_signal','macd_hist','dow','month']]

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
print("C54a: MACD(12,26,9) HISTOGRAM AT ENTRY")
print("="*65)
macd_base = entry.loc[base, 'macd_hist'].dropna()
print(f"\n  MACD hist on {base.sum()} qualifying trades:")
print(f"  mean={macd_base.mean():.6f}, median={macd_base.median():.6f}")
print(f"  negative: {(macd_base<0).sum()}, positive: {(macd_base>0).sum()}")

macd_neg = base & (entry['macd_hist'] < 0)
macd_pos = base & (entry['macd_hist'] > 0)
macd_falling = base & (entry['macd_hist'] < entry['macd_hist'].shift(1))

print(f"\n  MACD hist<0: n={macd_neg.sum()}, MACD hist>0: n={macd_pos.sum()}")
print(f"  MACD hist falling (vs prev bar): n={macd_falling.sum()}")
print()
pr("MACD hist < 0", run_on_mask(macd_neg))
pr("MACD hist > 0", run_on_mask(macd_pos))
pr("MACD hist falling", run_on_mask(macd_falling))

print("\n"+"="*65)
print("C54b: Stoch K<60 × C43 (0-1 prior Asia up days)")
print("="*65)
sk60 = base & (entry['stoch_k'] < 60)
consec = base & (entry['prior3_up'] <= 1)
sk60_consec = base & (entry['stoch_k'] < 60) & (entry['prior3_up'] <= 1)

print(f"\n  Stoch K<60: n={sk60.sum()}, 0-1 prior Asia up: n={consec.sum()}")
print(f"  Both: n={sk60_consec.sum()}")
print()
pr("Stoch K<60 alone", run_on_mask(sk60))
pr("0-1 prior Asia up (C43)", run_on_mask(consec))
pr("Stoch K<60 + 0-1 consec", run_on_mask(sk60_consec))

print("\n"+"="*65)
print("C54c: Stoch K<60 × C42 (skip Q2)")
print("="*65)
skip_q2 = base & (entry['month'].isin([1,2,3,7,8,9,10,11,12]))  # not Apr-Jun
sk60_skipq2 = base & (entry['stoch_k'] < 60) & (entry['month'].isin([1,2,3,7,8,9,10,11,12]))

print(f"\n  Skip Q2 (C42): n={skip_q2.sum()}, Stoch K<60 + skip Q2: n={sk60_skipq2.sum()}")
print()
pr("Skip Q2 (C42)", run_on_mask(skip_q2))
pr("Stoch K<60 + skip Q2", run_on_mask(sk60_skipq2))

print("\n"+"="*65)
print("C54d: H1 CLOSE vs EMA50 AT ENTRY")
print("="*65)
ema50_base = entry.loc[base, 'above_ema50']
print(f"\n  Above EMA50: {ema50_base.sum()}, Below EMA50: {(~ema50_base).sum()}")
above = base & (entry['above_ema50'] == True)
below = base & (entry['above_ema50'] == False)
sk60_below_ema = base & (entry['stoch_k'] < 60) & (entry['above_ema50'] == False)

print()
pr("Above EMA50 at entry", run_on_mask(above))
pr("Below EMA50 at entry", run_on_mask(below))
pr("Stoch K<60 + below EMA50", run_on_mask(sk60_below_ema))

print("\nDone.")
