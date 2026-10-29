"""
EURUSD Cycle C63 — London open momentum, prior week trend, signal combination stress test
C63a: London open direction (first 2 H1 bars 07-08) — does early London confirm SHORT?
C63b: Prior week direction (Mon-Fri close vs open of prior week) — weekly trend context
C63c: Combining best new signals (no gap up + prior day bear + EMA30 neg)
C63d: RSI(5) at 07:00 — faster RSI on H1 as overbought filter
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

low14 = df['low'].rolling(14).min()
high14 = df['high'].rolling(14).max()
df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14).clip(lower=1e-9)

# RSI(5) on H1
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
df['rsi5'] = 100 - (100 / (1 + gain.ewm(span=5, adjust=False).mean() / loss.ewm(span=5, adjust=False).mean().clip(lower=1e-9)))

# D1 EMA20 slope
d1 = df.set_index('ts').resample('1D').agg(
    close=('close','last')).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

# Daily open/close per date (all hours)
daily_oc = df.groupby('date').agg(
    day_open=('open','first'),
    day_close=('close','last')).reset_index()
daily_oc['day_bear'] = (daily_oc['day_close'] < daily_oc['day_open']).astype(int)
daily_oc['date'] = pd.to_datetime(daily_oc['date'])
daily_oc = daily_oc.sort_values('date').reset_index(drop=True)
daily_oc['prior_day_bear'] = daily_oc['day_bear'].shift(1)
daily_oc['date_key'] = daily_oc['date'].dt.date
prior_day_map = dict(zip(daily_oc['date_key'], daily_oc['prior_day_bear']))

# Prior week direction: Monday open to Friday close of PRIOR week
# Use ISO week grouping
df['iso_week'] = df['ts'].dt.isocalendar().week.astype(int)
df['iso_year'] = df['ts'].dt.isocalendar().year.astype(int)
df['week_id'] = df['iso_year'].astype(str) + '-' + df['iso_week'].astype(str).str.zfill(2)
weekly = df.groupby('week_id').agg(
    week_open=('open','first'),
    week_close=('close','last')).reset_index()
weekly['week_bear'] = (weekly['week_close'] < weekly['week_open']).astype(int)
weekly = weekly.sort_values('week_id').reset_index(drop=True)
weekly['prior_week_bear'] = weekly['week_bear'].shift(1)
prior_week_map = dict(zip(weekly['week_id'], weekly['prior_week_bear']))

# Asia session
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']

# EMA30 slope at 07:00
bar07_ema30 = df[df['hour']==7][['date','ema30_slope']].rename(columns={'ema30_slope':'ema30_slope_07'})
# RSI5 at 07:00
bar07_rsi5 = df[df['hour']==7][['date','rsi5']].rename(columns={'rsi5':'rsi5_07'})

# Close06
bar06 = df[df['hour']==6][['date','close']].rename(columns={'close':'close06'})

# H1 momentum score: bearish closes in hrs 2-6
h1_score = df[df['hour'].between(2,6)].copy()
h1_score['h1_bear'] = (h1_score['close'] < h1_score['open']).astype(int)
h1_score_grp = h1_score.groupby('date').agg(
    h1_mom_score=('h1_bear','sum')).reset_index()

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
             .merge(bar07_rsi5, on='date', how='left')
             .merge(h1_score_grp, on='date', how='left'))
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)
entry['prior_day_bear'] = entry['date_key'].map(prior_day_map)
entry['week_id'] = entry['date'].dt.isocalendar().year.astype(int).astype(str) + '-' + entry['date'].dt.isocalendar().week.astype(int).astype(str).str.zfill(2)
entry['prior_week_bear'] = entry['week_id'].map(prior_week_map)

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
pr("EMA30(H1)<0", run_on_mask(ema30_neg))
pr("C53b (SK<60+D1slope<0)", run_on_mask(c53b))

print("\n"+"="*65)
print("C63a: PRIOR WEEK DIRECTION")
print("="*65)
pw_base = entry.loc[base, 'prior_week_bear'].dropna()
print(f"\n  Prior week direction on {base.sum()} qualifying trades:")
print(f"  Prior week bearish (close<open): {(pw_base==1).sum()}")
print(f"  Prior week bullish: {(pw_base==0).sum()}")

prior_week_bear = base & (entry['prior_week_bear'] == 1)
prior_week_bull = base & (entry['prior_week_bear'] == 0)

print(f"\n  Prior week bear: n={prior_week_bear.sum()}, Prior week bull: n={prior_week_bull.sum()}")
print()
pr("Prior week bearish", run_on_mask(prior_week_bear))
pr("Prior week bullish", run_on_mask(prior_week_bull))
pr("EMA30 neg + prior week bear", run_on_mask(ema30_neg & prior_week_bear))
pr("EMA30 neg + prior week bull", run_on_mask(ema30_neg & prior_week_bull))
pr("No gap up + prior week bear", run_on_mask(base & entry['no_gap_up'] & prior_week_bear))
pr("C53b + prior week bear", run_on_mask(c53b & prior_week_bear))
pr("Prior day bear + prior week bear", run_on_mask(base & (entry['prior_day_bear']==1) & prior_week_bear))

print("\n"+"="*65)
print("C63b: RSI(5) AT 07:00 ON H1")
print("="*65)
rsi_base = entry.loc[base, 'rsi5_07'].dropna()
print(f"\n  RSI(5) H1 at 07:00 on {base.sum()} qualifying trades:")
print(f"  mean={rsi_base.mean():.1f}, median={rsi_base.median():.1f}")
print(f"  <50: {(rsi_base<50).sum()}, 50-60: {((rsi_base>=50)&(rsi_base<60)).sum()}, "
      f"60-70: {((rsi_base>=60)&(rsi_base<70)).sum()}, >=70: {(rsi_base>=70).sum()}")

rsi5_lo = base & (entry['rsi5_07'] < 60)
rsi5_hi = base & (entry['rsi5_07'] >= 60)
rsi5_overbought = base & (entry['rsi5_07'] >= 70)
rsi5_very_lo = base & (entry['rsi5_07'] < 50)

print(f"\n  RSI5<60: n={rsi5_lo.sum()}, RSI5>=60: n={rsi5_hi.sum()}")
print(f"  RSI5>=70 (overbought): n={rsi5_overbought.sum()}, RSI5<50: n={rsi5_very_lo.sum()}")
print()
pr("RSI5(H1) < 60", run_on_mask(rsi5_lo))
pr("RSI5(H1) >= 60", run_on_mask(rsi5_hi))
pr("RSI5(H1) >= 70 (overbought)", run_on_mask(rsi5_overbought))
pr("RSI5(H1) < 50", run_on_mask(rsi5_very_lo))
pr("EMA30 neg + RSI5 < 60", run_on_mask(ema30_neg & rsi5_lo))
pr("EMA30 neg + RSI5 >= 60", run_on_mask(ema30_neg & rsi5_hi))
pr("No gap up + RSI5 < 60", run_on_mask(base & entry['no_gap_up'] & rsi5_lo))
pr("C53b + RSI5 < 60", run_on_mask(c53b & rsi5_lo))

print("\n"+"="*65)
print("C63c: MULTI-SIGNAL COMBINATIONS")
print("="*65)
no_gap = entry['no_gap_up']
prior_bear = entry['prior_day_bear'] == 1
mom_ge2 = entry['h1_mom_score'] >= 2
ema30n = entry['ema30_slope_07'] < 0
d1neg = entry['d1_slope'] < 0
sk60 = entry['stoch_k'] < 60

print()
# Prior signals combined
pr("No gap + prior day bear + EMA30 neg", run_on_mask(base & no_gap & prior_bear & ema30n))
pr("No gap + prior day bear + mom>=2", run_on_mask(base & no_gap & prior_bear & mom_ge2))
pr("No gap + EMA30 neg + mom>=2 (C62d-b)", run_on_mask(base & no_gap & ema30n & mom_ge2))
pr("No gap + prior day bear + EMA30 neg + mom>=2", run_on_mask(base & no_gap & prior_bear & ema30n & mom_ge2))
pr("C53b + no gap up (C60a-related)", run_on_mask(c53b & no_gap))
pr("C53b + EMA30 neg (C59c-b)", run_on_mask(c53b & ema30n))
pr("C53b + prior day bear", run_on_mask(c53b & prior_bear))
pr("SK<60 + EMA30 neg + prior day bear", run_on_mask(base & sk60 & ema30n & prior_bear))
pr("EMA30 neg + prior week bear", run_on_mask(ema30_neg & (entry['prior_week_bear']==1)))

print("\n# Count active signals per trade:")
# How many of (no_gap, ema30n, prior_bear, mom>=2) are active?
entry_base = entry[base].copy()
entry_base['sig_no_gap'] = no_gap[base].astype(int)
entry_base['sig_ema30'] = ema30n[base].astype(int)
entry_base['sig_prior_bear'] = prior_bear[base].astype(int)
entry_base['sig_mom2'] = mom_ge2[base].astype(int)
entry_base['sig_count'] = entry_base[['sig_no_gap','sig_ema30','sig_prior_bear','sig_mom2']].sum(axis=1)
for c in sorted(entry_base['sig_count'].unique()):
    mask_c = base.copy(); mask_c[:] = False
    idx = entry_base[entry_base['sig_count']==c].index
    mask_c.iloc[entry[base].index.get_indexer(idx)] = True
    sub = entry[base].loc[entry_base[entry_base['sig_count']==c].index]
    # simpler approach
    r2 = run_on_mask(base & (entry.index.isin(entry_base[entry_base['sig_count']==c].index)))
    print(f"  Signal count={c}: n={r2['n']}, PF={r2['pf']}, avg={r2['avg']:+.3f}%, win={r2['win']}%")
    yr = ' | '.join(f"{y}: PF={v}" for y,v in sorted(r2['by_year'].items()))
    if yr: print(f"    {yr}")

print("\nDone.")
