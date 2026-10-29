"""
EURUSD Cycle C57 — Overnight gap deeper analysis + C53b+gap combo
C57a: No-gap-up as standalone baseline modifier
C57b: C53b + no gap up (combining best combo with new negative signal)
C57c: Gap direction breakdown — zero/up/down × Stoch K thresholds
C57d: Asia close position — how close to day's high is the 06:00 close?
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

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_up'] = (asia['asia_net'] > 0).astype(int)

# Asia close position vs Asia high: how near was 06:00 close to the Asia high?
# 0 = closed at the low, 1 = closed at the high
asia['asia_close_pos'] = (asia['asia_close'] - asia['asia_low']) / (asia['asia_high'] - asia['asia_low']).clip(lower=1e-9)

# Close06 — last close of Asia
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
entry['no_gap_up'] = entry['overnight_gap'] <= 0  # flat or gap down

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
print("C57a: NO-GAP-UP AS STANDALONE BASELINE MODIFIER")
print("="*65)
no_gap_up = base & (entry['no_gap_up'])
gap_up_only = base & ~entry['no_gap_up']
gap_zero = base & (entry['overnight_gap'] == 0)
gap_dn_only = base & (entry['overnight_gap'] < 0)

print(f"\n  Baseline n={base.sum()}")
print(f"  No gap up (flat+down): n={no_gap_up.sum()}, Gap up: n={gap_up_only.sum()}")
print(f"  Exactly flat: n={gap_zero.sum()}, Gap down only: n={gap_dn_only.sum()}")
print()
pr("No gap up (open07<=close06)", run_on_mask(no_gap_up))
pr("Gap up only (open07>close06)", run_on_mask(gap_up_only))
pr("Exactly flat (open07=close06)", run_on_mask(gap_zero))
pr("Gap down only (open07<close06)", run_on_mask(gap_dn_only))

print("\n"+"="*65)
print("C57b: C53b + NO GAP UP")
print("="*65)
c53b_no_gap = c53b & entry['no_gap_up']
c53b_gap_dn = c53b & (entry['overnight_gap'] < 0)
c53b_gap_zero = c53b & (entry['overnight_gap'] == 0)

print(f"\n  C53b: n={c53b.sum()}, C53b+no gap up: n={c53b_no_gap.sum()}")
print(f"  C53b+gap down only: n={c53b_gap_dn.sum()}, C53b+exactly flat: n={c53b_gap_zero.sum()}")
print()
pr("C53b (SK<60+D1slope<0)", run_on_mask(c53b))
pr("C53b + no gap up", run_on_mask(c53b_no_gap))
pr("C53b + gap down only", run_on_mask(c53b_gap_dn))
pr("C53b + exactly flat", run_on_mask(c53b_gap_zero))

print("\n"+"="*65)
print("C57c: GAP DIRECTION × STOCH K THRESHOLDS")
print("="*65)
sk60 = base & (entry['stoch_k'] < 60)
sk_hi = base & (entry['stoch_k'] >= 60)

print(f"\n  SK<60 gap up: n={(sk60 & ~entry['no_gap_up']).sum()}")
print(f"  SK<60 no gap up: n={(sk60 & entry['no_gap_up']).sum()}")
print(f"  SK>=60 no gap up: n={(sk_hi & entry['no_gap_up']).sum()}")
print(f"  SK>=60 gap up: n={(sk_hi & ~entry['no_gap_up']).sum()}")
print()
pr("SK<60 + no gap up", run_on_mask(sk60 & entry['no_gap_up']))
pr("SK<60 + gap up", run_on_mask(sk60 & ~entry['no_gap_up']))
pr("SK>=60 + no gap up", run_on_mask(sk_hi & entry['no_gap_up']))
pr("SK>=60 + gap up", run_on_mask(sk_hi & ~entry['no_gap_up']))

print("\n"+"="*65)
print("C57d: ASIA CLOSE POSITION (how near to Asia high?)")
print("="*65)
acp_base = entry.loc[base, 'asia_close_pos'].dropna()
print(f"\n  Asia close pos on {base.sum()} qualifying trades:")
print(f"  mean={acp_base.mean():.3f}, median={acp_base.median():.3f}")
print(f"  <0.5: {(acp_base<0.5).sum()}, 0.5-0.7: {((acp_base>=0.5)&(acp_base<0.7)).sum()}, "
      f">=0.7: {(acp_base>=0.7).sum()}")

# High close pos = Asia closed near range high (momentum intact) = good for SHORT
acp_hi = base & (entry['asia_close_pos'] >= 0.7)  # closed near top
acp_mid = base & (entry['asia_close_pos'].between(0.5, 0.7))
acp_lo = base & (entry['asia_close_pos'] < 0.5)   # faded from highs

print(f"\n  Asia close high (pos>=0.7): n={acp_hi.sum()}")
print(f"  Asia close mid (0.5-0.7): n={acp_mid.sum()}")
print(f"  Asia close low (<0.5): n={acp_lo.sum()}")
print()
pr("Asia close high (pos>=0.7)", run_on_mask(acp_hi))
pr("Asia close mid (0.5-0.7)", run_on_mask(acp_mid))
pr("Asia close low (<0.5)", run_on_mask(acp_lo))
pr("SK<60 + Asia close high", run_on_mask(base & (entry['stoch_k']<60) & (entry['asia_close_pos']>=0.7)))
pr("SK<60 + Asia close low", run_on_mask(base & (entry['stoch_k']<60) & (entry['asia_close_pos']<0.5)))

print("\nDone.")
