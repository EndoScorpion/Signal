"""
EURUSD Cycles C36–C38
C36: Price-EMA120 gap — how far above EMA120 is price at entry?
C37: ATR trend — is volatility expanding or contracting?
C38: Asia bar consistency — fraction of 7 Asia bars that moved up
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
df = df.sort_values('ts').reset_index(drop=True)

df['prev_close'] = df['close'].shift(1)
df['tr'] = pd.concat([df['high']-df['low'],(df['high']-df['prev_close']).abs(),
                       (df['low']-df['prev_close']).abs()],axis=1).max(axis=1)
df['atr14'] = df['tr'].ewm(span=14, adjust=False).mean()
df['atr14_pct'] = df['atr14'].rolling(252, min_periods=50).rank(pct=True)
df['atr14_5d_ago'] = df['atr14'].shift(5)  # for ATR expansion check

df['ema120'] = df['close'].ewm(span=120, adjust=False).mean()
df['ema120_slope'] = df['ema120'].diff()
df['price_vs_ema'] = (df['close'] - df['ema120']) / df['atr14']  # in ATR units

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

# Asia bar consistency: fraction of 7 hourly bars (0-6) where close > open
def asia_consistency(grp):
    bulls = (grp['close'] > grp['open']).sum()
    return bulls / max(len(grp), 1)

asia_bars = df[df['hour'].between(0, 6)].copy()
asia_bars['bull_bar'] = (asia_bars['close'] > asia_bars['open']).astype(float)
asia_consist = asia_bars.groupby('date').agg(
    asia_bull_frac=('bull_bar', 'mean')).reset_index()

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','atr14_5d_ago','ema120_slope','adx14','price_vs_ema','dow']]

intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = bar07.merge(asia, on='date').merge(asia_consist, on='date', how='left')
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
            'win':round((r['pnl']>0).mean()*100,1),'by_year':by_yr,
            'stop_rate':round(r['stopped'].mean()*100,1)}

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
print("C36: PRICE-EMA120 GAP (in ATR units at entry)")
print("="*65)
print("(price > EMA120 = bullish price but bearish trend = stronger fade?)\n")

# Distribution of price_vs_ema on qualifying trades
e_base = entry[base]
pve = e_base['price_vs_ema']
print(f"  price_vs_ema distribution: mean={pve.mean():.2f}, median={pve.median():.2f}, "
      f"min={pve.min():.2f}, max={pve.max():.2f}")

# Test: price > EMA120 (i.e., above it despite downslope)
above_ema = base & (entry['price_vs_ema'] > 0)
below_ema = base & (entry['price_vs_ema'] <= 0)
print("\n--- Price above EMA120 (bullish divergence, fade candidate) ---")
pr("price > EMA", run_on_mask(above_ema))
print("\n--- Price below EMA120 (aligned with downtrend) ---")
pr("price < EMA", run_on_mask(below_ema))

# Threshold tests
for thresh in [0.5, 1.0, 1.5, 2.0]:
    mask_gt = base & (entry['price_vs_ema'] > thresh)
    mask_lt = base & (entry['price_vs_ema'] <= thresh)
    print(f"\n  price_vs_ema > {thresh}: n={mask_gt.sum()}, PF={run_on_mask(mask_gt)['pf']}")
    print(f"  price_vs_ema ≤ {thresh}: n={mask_lt.sum()}, PF={run_on_mask(mask_lt)['pf']}")

print("\n"+"="*65)
print("C37: ATR TREND (expanding vs contracting volatility)")
print("="*65)

e_base['atr_ratio'] = e_base['atr14'] / e_base['atr14_5d_ago']
print(f"\nATR ratio (current/5d ago): mean={e_base['atr_ratio'].mean():.3f}, "
      f"median={e_base['atr_ratio'].median():.3f}")

atr_expanding = base & (entry['atr14'] > entry['atr14_5d_ago'])
atr_contracting = base & (entry['atr14'] <= entry['atr14_5d_ago'])
print("\n--- ATR expanding (current > 5d ago) ---")
pr("ATR expanding", run_on_mask(atr_expanding))
print("\n--- ATR contracting (current <= 5d ago) ---")
pr("ATR contracting", run_on_mask(atr_contracting))

print("\n"+"="*65)
print("C38: ASIA BAR CONSISTENCY (fraction of 7 bars bullish)")
print("="*65)

e_base2 = entry[base]
abf = e_base2['asia_bull_frac']
print(f"\nAsia bull fraction distribution: mean={abf.mean():.2f}, "
      f"min={abf.min():.2f}, max={abf.max():.2f}")
print(f">=4/7 (>0.57): {(abf>0.571).sum()}, >=5/7 (>0.71): {(abf>0.714).sum()}, "
      f">=6/7 (>0.857): {(abf>0.857).sum()}, =7/7: {(abf>=1.0).sum()}")

for thresh_label, thresh in [(">=4/7", 0.571), (">=5/7", 0.714), (">=6/7", 0.857)]:
    mask_high = base & (entry['asia_bull_frac'] > thresh)
    mask_low = base & (entry['asia_bull_frac'] <= thresh)
    rh = run_on_mask(mask_high); rl = run_on_mask(mask_low)
    print(f"\n  Asia consistent up {thresh_label}: n={rh['n']}, PF={rh['pf']}, avg={rh['avg']:+.3f}%")
    if rh['by_year']: print(f"    {' | '.join(f'{y}: PF={v}' for y,v in sorted(rh['by_year'].items()))}")
    print(f"  Asia mixed/down (<= {thresh_label}): n={rl['n']}, PF={rl['pf']}, avg={rl['avg']:+.3f}%")

print("\nDone.")
