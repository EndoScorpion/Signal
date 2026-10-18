"""
EURUSD Cycle C48 — Asia Final Bar + London Entry Bar Candle
C48a: Asia final bar (06:00) direction — last Asia hour bullish or bearish?
C48b: 07:00 entry bar candle — is the London open bar itself up or down?
C48c: Asia close position in range — where is 06:00 close relative to Asia H-L?
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

# Asia session: 00:00-06:00
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last'),
    asia_high=('high','max'), asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']
# Close position in Asia range (0=at low, 1=at high)
asia['asia_close_pct'] = np.where(
    asia['asia_range'] > 0,
    (asia['asia_close'] - asia['asia_low']) / asia['asia_range'],
    0.5)

# Asia final bar: 06:00
bar06 = df[df['hour']==6][['date','open','close']].copy()
bar06 = bar06.rename(columns={'open':'open06','close':'close06'})
bar06['bar06_bullish'] = bar06['close06'] > bar06['open06']
bar06['bar06_return'] = bar06['close06'] - bar06['open06']

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07['bar07_bullish'] = bar07['close07'] > bar07['open07']
bar07['bar07_return'] = bar07['close07'] - bar07['open07']
bar07 = bar07[['date','open07','high07','low07','close07','bar07_bullish','bar07_return',
               'atr14','atr14_pct','ema120_slope','adx14','dow','month']]

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
b06_b = e_base['bar06_bullish'].mean()
b07_b = e_base['bar07_bullish'].mean()
acp = e_base['asia_close_pct']
print(f"\nOn qualifying trades:")
print(f"  06:00 bar bullish: {b06_b*100:.1f}%")
print(f"  07:00 bar bullish: {b07_b*100:.1f}%")
print(f"  Asia close pct in range: mean={acp.mean():.3f}, p25={acp.quantile(0.25):.3f}, p75={acp.quantile(0.75):.3f}")

print("\n"+"="*65)
print("C48a: ASIA FINAL BAR (06:00) DIRECTION")
print("="*65)

bar06_bull = base & (entry['bar06_bullish']==True)
bar06_bear = base & (entry['bar06_bullish']==False)
bar06_na = base & entry['bar06_bullish'].isna()
print(f"\n  06:00 bullish: n={bar06_bull.sum()}, bearish: n={bar06_bear.sum()}, NA: n={bar06_na.sum()}")
print("\n--- 06:00 bar bullish (last Asia hour still rising — strong into London open) ---")
pr("06:00 bullish", run_on_mask(bar06_bull))
print("\n--- 06:00 bar bearish (last Asia hour faded — momentum losing steam) ---")
pr("06:00 bearish", run_on_mask(bar06_bear))

# Magnitude of 06:00 bar
entry['bar06_ret_atr'] = entry['bar06_return'] / entry['atr14']
print("\n06:00 bar magnitude (in ATR units):")
med_06 = entry.loc[base, 'bar06_ret_atr'].dropna().median()
print(f"  Median |06:00 return| / ATR = {med_06:.4f}")
for lo, hi, label in [(-99,-0.05,"big bear 06:00"),(-0.05,0,"small bear 06:00"),
                       (0,0.05,"small bull 06:00"),(0.05,99,"big bull 06:00")]:
    mask = base & (entry['bar06_ret_atr'] >= lo) & (entry['bar06_ret_atr'] < hi)
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\n"+"="*65)
print("C48b: 07:00 ENTRY BAR CANDLE DIRECTION")
print("="*65)
print("\n(This is related to C35 bear07, but checks if the bar itself is up or down)")

bar07_bull = base & (entry['bar07_bullish']==True)
bar07_bear = base & (entry['bar07_bullish']==False)
print(f"\n  07:00 bullish: n={bar07_bull.sum()}, bearish: n={bar07_bear.sum()}")
print("\n--- 07:00 bar bullish (entry bar closes higher — short into continuing up move) ---")
pr("07:00 bullish", run_on_mask(bar07_bull))
print("\n--- 07:00 bar bearish (entry bar closes lower — early sign of fade starting) ---")
pr("07:00 bearish", run_on_mask(bar07_bear))

print("\n"+"="*65)
print("C48c: ASIA CLOSE POSITION IN RANGE")
print("="*65)
print("\n(0 = closed at Asia low, 1 = closed at Asia high)")

acp_med = e_base['asia_close_pct'].median()
print(f"\nMedian asia_close_pct: {acp_med:.3f}")

# High in range (>0.75 = closed near Asia high) vs lower
top_quartile = base & (entry['asia_close_pct'] >= 0.75)
bottom_3q = base & (entry['asia_close_pct'] < 0.75)
print(f"\n  Close in top 25% of Asia range (>=0.75): n={top_quartile.sum()}")
print(f"  Close in bottom 75% of Asia range (<0.75): n={bottom_3q.sum()}")
print("\n--- Close near Asia high (>=0.75 pct): strong extension into London ---")
pr("Close near Asia high", run_on_mask(top_quartile))
print("\n--- Close not near Asia high (<0.75 pct): more room below ---")
pr("Close not near Asia high", run_on_mask(bottom_3q))

# Quartile breakdown
for lo, hi, label in [(0,0.25,"Q1 low 0-25%"),(0.25,0.50,"Q2 25-50%"),
                       (0.50,0.75,"Q3 50-75%"),(0.75,1.01,"Q4 75-100%")]:
    mask = base & (entry['asia_close_pct'] >= lo) & (entry['asia_close_pct'] < hi)
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\nDone.")
