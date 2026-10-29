"""
EURUSD Cycle C60 — Three-filter combos with EMA30, H4 Stochastic, consecutive bearish H1 bars
C60a: C53b + EMA30(H1) + no gap up — three-filter test
C60b: Stochastic(14,3) on H4 timeframe at entry
C60c: Consecutive bearish H1 bars before 07:00 (bear momentum building into entry)
C60d: RSI(14) on H4 at 07:00 entry
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
df['ema30'] = df['close'].ewm(span=30, adjust=False).mean()
df['ema30_slope'] = df['ema30'].diff()

up = df['high'].diff(); dn = -df['low'].diff()
pdm = np.where((up > dn) & (up > 0), up, 0.0)
ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
atr_s = df['tr'].ewm(span=14, adjust=False).mean()
pdi = 100*pd.Series(pdm,index=df.index).ewm(span=14,adjust=False).mean()/atr_s
ndi = 100*pd.Series(ndm,index=df.index).ewm(span=14,adjust=False).mean()/atr_s
dx = 100*(pdi-ndi).abs()/(pdi+ndi).clip(lower=1e-9)
df['adx14'] = dx.ewm(span=14, adjust=False).mean()

# Stochastic(14,3) on H1
low14 = df['low'].rolling(14).min()
high14 = df['high'].rolling(14).max()
df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14).clip(lower=1e-9)
df['stoch_d'] = df['stoch_k'].rolling(3).mean()

# H4 Stochastic: resample to 4H, compute stoch(5,3) on H4 bars
# H4 bars aligned to 00:00 UTC: 00-03, 04-07, 08-11, ...
# For the pre-entry bar (00:00-03:59 H4 bar, i.e., hours 0-3), we use H4 close at bar 03:59
# Actually the 04:00 H4 bar opens at 04:00 — pre-entry is the 00:00-03:59 bar
# Let's resample to 4H and get the last bar before 07:00 (the 04:00 H4 bar = hours 4-7)
# For stoch, compute on H4 with period 5
h4 = df.set_index('ts').resample('4h').agg(
    open=('open','first'),
    high=('high','max'),
    low=('low','min'),
    close=('close','last')).dropna(subset=['close']).reset_index()
h4 = h4.sort_values('ts').reset_index(drop=True)
h4['h4_low5'] = h4['low'].rolling(5).min()
h4['h4_high5'] = h4['high'].rolling(5).max()
h4['h4_stoch_k'] = 100 * (h4['close'] - h4['h4_low5']) / (h4['h4_high5'] - h4['h4_low5']).clip(lower=1e-9)
h4['h4_stoch_d'] = h4['h4_stoch_k'].rolling(3).mean()

# H4 RSI(14)
h4_delta = h4['close'].diff()
h4_gain = np.where(h4_delta > 0, h4_delta, 0.0)
h4_loss = np.where(h4_delta < 0, -h4_delta, 0.0)
h4_avg_gain = pd.Series(h4_gain).ewm(span=14, adjust=False).mean()
h4_avg_loss = pd.Series(h4_loss).ewm(span=14, adjust=False).mean()
h4_rs = h4_avg_gain / h4_avg_loss.clip(lower=1e-9)
h4['h4_rsi'] = 100 - (100 / (1 + h4_rs))

# The H4 bar that starts at 04:00 covers hours 4-7, ending at 07:59 (before 08:00 next bar)
# We want the H4 stoch at the 04:00 bar since that's what's known at 07:00 entry
# The 04:00 bar has ts = 04:00 in resample (4H from midnight: 0, 4, 8, 12, ...)
h4['date'] = h4['ts'].dt.date
h4['h4_hour'] = h4['ts'].dt.hour

# The 04:00-07:59 bar: h4_hour == 4
h4_pre = h4[h4['h4_hour'] == 4][['date','h4_stoch_k','h4_stoch_d','h4_rsi']].copy()
h4_pre = h4_pre.rename(columns={'h4_stoch_k':'h4sk_04','h4_stoch_d':'h4sd_04','h4_rsi':'h4rsi_04'})

# D1 EMA20 slope
d1 = df.set_index('ts').resample('1D').agg(
    close=('close','last')).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

# Asia session
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']

# Consecutive bearish H1 bars at 07:00: count how many of the last N H1 bars (hrs 4,5,6) were bearish
# For each date, look at hours 4, 5, 6 — count bars where close < open
h1_pre = df[df['hour'].between(4,6)][['date','hour','open','close']].copy()
h1_pre['h1_bear'] = (h1_pre['close'] < h1_pre['open']).astype(int)
h1_pre_grp = h1_pre.groupby('date').agg(
    consec_bear_h1=('h1_bear','sum'),
    n_pre_bars=('h1_bear','count')).reset_index()
# Also check the final pre-entry H1 bar (hour 6) specifically
h1_h6 = df[df['hour']==6][['date','open','close']].copy()
h1_h6['h6_bear'] = (h1_h6['close'] < h1_h6['open']).astype(int)

# EMA30 slope at 07:00
bar07_ema30 = df[df['hour']==7][['date','ema30_slope']].rename(columns={'ema30_slope':'ema30_slope_07'})

# Close06
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

entry = (bar07.merge(asia, on='date')
             .merge(bar06, on='date', how='left')
             .merge(bar07_ema30, on='date', how='left')
             .merge(h1_pre_grp, on='date', how='left')
             .merge(h1_h6, on='date', how='left')
             .merge(h4_pre, on='date', how='left'))
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)

entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['no_gap_up'] = entry['overnight_gap'] <= 0
entry['asia_net_atr'] = entry['asia_net'] / entry['atr14'].clip(lower=1e-9)

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
ema30_neg = base & (entry['ema30_slope_07'] < 0)

print("="*65)
print("BASELINE + KEY REFERENCES")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))
pr("C53b (SK<60+D1slope<0)", run_on_mask(c53b))
pr("C59c EMA30(H1)<0", run_on_mask(ema30_neg))
pr("No gap up", run_on_mask(base & entry['no_gap_up']))

print("\n"+"="*65)
print("C60a: THREE-FILTER COMBOS WITH EMA30")
print("="*65)
print(f"\n  C53b+EMA30neg: n={(c53b & ema30_neg).sum()}")
print(f"  No gap up + EMA30neg: n={(base & entry['no_gap_up'] & ema30_neg).sum()}")
print(f"  C53b + no gap up + EMA30neg: n={(c53b & entry['no_gap_up'] & ema30_neg).sum()}")
print(f"  SK<60 + EMA30neg: n={(base & (entry['stoch_k']<60) & ema30_neg).sum()}")
print(f"  SK<60 + EMA30neg + no gap up: n={(base & (entry['stoch_k']<60) & ema30_neg & entry['no_gap_up']).sum()}")
print()
pr("C53b + EMA30 neg", run_on_mask(c53b & ema30_neg))
pr("No gap up + EMA30 neg", run_on_mask(base & entry['no_gap_up'] & ema30_neg))
pr("C53b + no gap up + EMA30 neg", run_on_mask(c53b & entry['no_gap_up'] & ema30_neg))
pr("SK<60 + EMA30 neg", run_on_mask(base & (entry['stoch_k']<60) & ema30_neg))
pr("SK<60 + EMA30 neg + no gap up", run_on_mask(base & (entry['stoch_k']<60) & ema30_neg & entry['no_gap_up']))
pr("EMA30 neg + D1slope<0", run_on_mask(base & ema30_neg & (entry['d1_slope']<0)))
pr("EMA30 neg + D1slope<0 + no gap up", run_on_mask(base & ema30_neg & (entry['d1_slope']<0) & entry['no_gap_up']))

print("\n"+"="*65)
print("C60b: H4 STOCHASTIC(5,3) AT 04:00-07:59 BAR")
print("="*65)
h4sk_base = entry.loc[base, 'h4sk_04'].dropna()
print(f"\n  H4 Stoch K on {base.sum()} qualifying trades:")
print(f"  Available: {h4sk_base.count()}, mean={h4sk_base.mean():.1f}, median={h4sk_base.median():.1f}")
print(f"  <30: {(h4sk_base<30).sum()}, 30-50: {((h4sk_base>=30)&(h4sk_base<50)).sum()}, "
      f"50-70: {((h4sk_base>=50)&(h4sk_base<70)).sum()}, >=70: {(h4sk_base>=70).sum()}")

h4sk_lo = base & (entry['h4sk_04'] < 50)
h4sk_hi = base & (entry['h4sk_04'] >= 50)
h4sk_vlo = base & (entry['h4sk_04'] < 30)

print(f"\n  H4 SK<50 (oversold/neutral): n={h4sk_lo.sum()}, H4 SK>=50: n={h4sk_hi.sum()}")
print(f"  H4 SK<30: n={h4sk_vlo.sum()}")
print()
pr("H4 SK<50 at 04:00 bar", run_on_mask(h4sk_lo))
pr("H4 SK>=50 at 04:00 bar", run_on_mask(h4sk_hi))
pr("H4 SK<30 at 04:00 bar", run_on_mask(h4sk_vlo))
pr("C53b + H4 SK<50", run_on_mask(c53b & h4sk_lo))
pr("C53b + H4 SK>=50", run_on_mask(c53b & h4sk_hi))
pr("EMA30 neg + H4 SK<50", run_on_mask(ema30_neg & h4sk_lo))
pr("EMA30 neg + H4 SK>=50", run_on_mask(ema30_neg & h4sk_hi))
pr("No gap up + H4 SK<50", run_on_mask(base & entry['no_gap_up'] & h4sk_lo))
pr("No gap up + H4 SK>=50", run_on_mask(base & entry['no_gap_up'] & h4sk_hi))

print("\n"+"="*65)
print("C60b2: H4 RSI(14) AT 04:00-07:59 BAR")
print("="*65)
h4rsi_base = entry.loc[base, 'h4rsi_04'].dropna()
print(f"\n  H4 RSI(14) on {base.sum()} qualifying trades:")
print(f"  Available: {h4rsi_base.count()}, mean={h4rsi_base.mean():.1f}, median={h4rsi_base.median():.1f}")
print(f"  <40: {(h4rsi_base<40).sum()}, 40-50: {((h4rsi_base>=40)&(h4rsi_base<50)).sum()}, "
      f"50-60: {((h4rsi_base>=50)&(h4rsi_base<60)).sum()}, >=60: {(h4rsi_base>=60).sum()}")

h4rsi_lo = base & (entry['h4rsi_04'] < 50)
h4rsi_hi = base & (entry['h4rsi_04'] >= 50)
h4rsi_vlo = base & (entry['h4rsi_04'] < 40)

print(f"\n  H4 RSI<50: n={h4rsi_lo.sum()}, H4 RSI>=50: n={h4rsi_hi.sum()}")
print()
pr("H4 RSI<50 at 04:00 bar", run_on_mask(h4rsi_lo))
pr("H4 RSI>=50 at 04:00 bar", run_on_mask(h4rsi_hi))
pr("H4 RSI<40 at 04:00 bar", run_on_mask(h4rsi_vlo))
pr("C53b + H4 RSI<50", run_on_mask(c53b & h4rsi_lo))
pr("EMA30 neg + H4 RSI<50", run_on_mask(ema30_neg & h4rsi_lo))
pr("EMA30 neg + H4 RSI>=50", run_on_mask(ema30_neg & h4rsi_hi))

print("\n"+"="*65)
print("C60c: CONSECUTIVE BEARISH H1 BARS (hrs 4-6 before entry)")
print("="*65)
consec_base = entry.loc[base, 'consec_bear_h1'].dropna()
print(f"\n  Consecutive bear H1 bars (hrs 4-6) on {base.sum()} qualifying trades:")
print(f"  0 bear: {(consec_base==0).sum()}, 1 bear: {(consec_base==1).sum()}, "
      f"2 bear: {(consec_base==2).sum()}, 3 bear (all): {(consec_base==3).sum()}")
print(f"  mean={consec_base.mean():.2f}")
h6_bear_base = entry.loc[base, 'h6_bear'].dropna()
print(f"  H6 (last Asia bar) bearish: {(h6_bear_base==1).sum()}, bullish: {(h6_bear_base==0).sum()}")

# >=2 bear bars in the 3 pre-entry hours = bear momentum building
consec2 = base & (entry['consec_bear_h1'] >= 2)
consec3 = base & (entry['consec_bear_h1'] == 3)
consec0 = base & (entry['consec_bear_h1'] == 0)
h6_bear = base & (entry['h6_bear'] == 1)
h6_bull = base & (entry['h6_bear'] == 0)

print(f"\n  >=2/3 bear hrs: n={consec2.sum()}, all 3 bear: n={consec3.sum()}, 0 bear: n={consec0.sum()}")
print()
pr(">=2 of 3 pre-entry hrs bearish", run_on_mask(consec2))
pr("All 3 pre-entry hrs bearish", run_on_mask(consec3))
pr("0 pre-entry hrs bearish", run_on_mask(consec0))
pr("H6 bar bearish", run_on_mask(h6_bear))
pr("H6 bar bullish", run_on_mask(h6_bull))
pr("C53b + >=2 bear hrs", run_on_mask(c53b & consec2))
pr("EMA30 neg + >=2 bear hrs", run_on_mask(ema30_neg & consec2))
pr("EMA30 neg + H6 bearish", run_on_mask(ema30_neg & h6_bear))
pr("EMA30 neg + H6 bullish", run_on_mask(ema30_neg & h6_bull))
pr("No gap up + H6 bearish", run_on_mask(base & entry['no_gap_up'] & h6_bear))

print("\nDone.")
