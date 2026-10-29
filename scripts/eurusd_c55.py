"""
EURUSD Cycle C55 — Stoch K<55 combos + Asia quality + Bar07 range position
C55a: Stoch K<55 + D1 slope<0 (analogous to C53b best combo at K<60)
C55b: Stoch K<55 + C43 (0-1 prior Asia up)
C55c: Asia quality — how much did Asia rally fade? asia_high - asia_close (overshoot)
C55d: Bar07 range position — open07 position within (low07,high07) range
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

# Asia session analysis (hours 0-6)
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_up'] = (asia['asia_net'] > 0).astype(int)
asia['prior3_up'] = asia['asia_up'].shift(1) + asia['asia_up'].shift(2) + asia['asia_up'].shift(3)
# Asia overshoot: how much did price pull back from the Asia high by session close
# High-to-close fade: positive = rally faded, negative = ended near high
asia['asia_hc_fade'] = asia['asia_high'] - asia['asia_close']
# Fade ratio: fraction of asia_net retraced from high
asia['asia_fade_ratio'] = asia['asia_hc_fade'] / asia['asia_net'].clip(lower=1e-9)
# Asia range as fraction of ATR (for normalization, use atr from 07:00 bar)

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07['bar07_range'] = bar07['high07'] - bar07['low07']
# Open position within bar range: 0=at low, 1=at high
bar07['open07_pos'] = (bar07['open07'] - bar07['low07']) / bar07['bar07_range'].clip(lower=1e-9)
bar07 = bar07[['date','open07','high07','low07','close07',
               'bar07_range','open07_pos',
               'atr14','atr14_pct','ema120_slope','adx14','stoch_k','dow','month']]

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
print("C55a: Stoch K<55 + D1 slope<0 (analogous to C53b)")
print("="*65)
sk55 = base & (entry['stoch_k'] < 55)
sk60 = base & (entry['stoch_k'] < 60)
d1_neg = base & (entry['d1_slope'] < 0)
sk55_d1 = base & (entry['stoch_k'] < 55) & (entry['d1_slope'] < 0)
sk60_d1 = base & (entry['stoch_k'] < 60) & (entry['d1_slope'] < 0)

print(f"\n  Stoch K<55: n={sk55.sum()}, K<60: n={sk60.sum()}, D1 slope<0: n={d1_neg.sum()}")
print(f"  K<55 + D1neg: n={sk55_d1.sum()}, K<60 + D1neg: n={sk60_d1.sum()}")
print()
pr("Stoch K<55 alone", run_on_mask(sk55))
pr("Stoch K<60 alone (C52c-b)", run_on_mask(sk60))
pr("D1 slope<0 (C25b)", run_on_mask(d1_neg))
pr("Stoch K<55 + D1 slope<0", run_on_mask(sk55_d1))
pr("Stoch K<60 + D1 slope<0 (C53b)", run_on_mask(sk60_d1))

print("\n"+"="*65)
print("C55b: Stoch K<55 + C43 (0-1 prior Asia up)")
print("="*65)
consec = base & (entry['prior3_up'] <= 1)
sk55_consec = base & (entry['stoch_k'] < 55) & (entry['prior3_up'] <= 1)

print(f"\n  Stoch K<55: n={sk55.sum()}, 0-1 prior Asia up: n={consec.sum()}")
print(f"  Both: n={sk55_consec.sum()}")
print()
pr("Stoch K<55 alone", run_on_mask(sk55))
pr("0-1 prior Asia up (C43)", run_on_mask(consec))
pr("Stoch K<55 + 0-1 consec", run_on_mask(sk55_consec))

print("\n"+"="*65)
print("C55c: ASIA SESSION QUALITY")
print("="*65)
# Asia high-to-close fade: how much did the Asia rally retrace before close?
# fade_ratio > 0.5 means price retraced more than half of the Asia gain by 06:00
fade_base = entry.loc[base, 'asia_fade_ratio'].dropna()
print(f"\n  Asia fade ratio on {base.sum()} qualifying trades:")
print(f"  mean={fade_base.mean():.3f}, median={fade_base.median():.3f}")
print(f"  <0.3: {(fade_base<0.3).sum()}, 0.3-0.5: {((fade_base>=0.3)&(fade_base<0.5)).sum()}, "
      f"0.5-1.0: {((fade_base>=0.5)&(fade_base<1.0)).sum()}, >1.0: {(fade_base>=1.0).sum()}")

# Low fade = Asia still firm at close (good for our SHORT: momentum intact)
# High fade = Asia already rolling over (also good? momentum may already be reversing)
asia_firm = base & (entry['asia_fade_ratio'] < 0.3)   # rally intact at 06:00
asia_mid = base & (entry['asia_fade_ratio'].between(0.3, 0.5))
asia_faded = base & (entry['asia_fade_ratio'] >= 0.5)   # rally already faded

print(f"\n  Asia firm (<30% fade): n={asia_firm.sum()}")
print(f"  Asia mid (30-50% fade): n={asia_mid.sum()}")
print(f"  Asia faded (>=50% fade): n={asia_faded.sum()}")
print()
pr("Asia firm (<30% fade)", run_on_mask(asia_firm))
pr("Asia mid (30-50%)", run_on_mask(asia_mid))
pr("Asia faded (>=50%)", run_on_mask(asia_faded))
pr("Asia very firm + Stoch K<60", run_on_mask(base & (entry['asia_fade_ratio']<0.3) & (entry['stoch_k']<60)))

print("\n"+"="*65)
print("C55d: BAR07 OPEN POSITION IN RANGE")
print("="*65)
# open07_pos: 0=open at low, 1=open at high of the 07:00 bar
# For a SHORT entry at open, high open07_pos means we're entering near the high (good for short)
open_base = entry.loc[base, 'open07_pos'].dropna()
print(f"\n  Bar07 open position on {base.sum()} qualifying trades:")
print(f"  mean={open_base.mean():.3f}, median={open_base.median():.3f}")
print(f"  <0.3: {(open_base<0.3).sum()}, 0.3-0.5: {((open_base>=0.3)&(open_base<0.5)).sum()}, "
      f"0.5-0.7: {((open_base>=0.5)&(open_base<0.7)).sum()}, >=0.7: {(open_base>=0.7).sum()}")

# High position = open near top of bar = good for short
op_hi = base & (entry['open07_pos'] >= 0.5)  # open in upper half
op_lo = base & (entry['open07_pos'] < 0.5)   # open in lower half
op_top = base & (entry['open07_pos'] >= 0.7)  # open near top
op_bot = base & (entry['open07_pos'] < 0.3)   # open near bottom

print(f"\n  Open upper half (pos>=0.5): n={op_hi.sum()}, Open lower half: n={op_lo.sum()}")
print(f"  Open top 30% (pos>=0.7): n={op_top.sum()}, Open bottom 30%: n={op_bot.sum()}")
print()
pr("Open upper half (pos>=0.5)", run_on_mask(op_hi))
pr("Open lower half (pos<0.5)", run_on_mask(op_lo))
pr("Open top 30% (pos>=0.7)", run_on_mask(op_top))
pr("Open bottom 30% (pos<0.3)", run_on_mask(op_bot))
pr("SK<60 + open upper half", run_on_mask(base & (entry['stoch_k']<60) & (entry['open07_pos']>=0.5)))

print("\nDone.")
