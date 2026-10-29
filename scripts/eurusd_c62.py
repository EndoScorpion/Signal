"""
EURUSD Cycle C62 — Prior day close direction, weekly trend, session range ratio
C62a: Prior day close direction — did Monday/Tuesday close down before Wed/Thu entry?
C62b: Weekly open vs current price — is price above or below weekly open at entry?
C62c: Asia range / prior day range ratio — compact Asia after large prior day
C62d: EMA30 neg + H1 momentum score >= 2 combo
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
df['week'] = df['ts'].dt.isocalendar().week.astype(int)
df['year_num'] = df['ts'].dt.year
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
    day_close=('close','last'),
    day_high=('high','max'),
    day_low=('low','min')).reset_index()
daily_oc['day_range'] = daily_oc['day_high'] - daily_oc['day_low']
daily_oc['day_bear'] = (daily_oc['day_close'] < daily_oc['day_open']).astype(int)
daily_oc['date'] = pd.to_datetime(daily_oc['date'])
# prior day close direction: shift 1
daily_oc = daily_oc.sort_values('date').reset_index(drop=True)
daily_oc['prior_day_bear'] = daily_oc['day_bear'].shift(1)
daily_oc['prior_day_range'] = daily_oc['day_range'].shift(1)
daily_oc['date_key'] = daily_oc['date'].dt.date
prior_day_map = dict(zip(daily_oc['date_key'], daily_oc['prior_day_bear']))
prior_range_map = dict(zip(daily_oc['date_key'], daily_oc['prior_day_range']))

# Weekly open: first bar of each ISO week
df['week_year'] = df['year_num'].astype(str) + '-' + df['week'].astype(str).str.zfill(2)
weekly_open = df.groupby('week_year').agg(week_open=('open','first')).reset_index()
week_open_map = dict(zip(weekly_open['week_year'], weekly_open['week_open']))

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

# Close06
bar06 = df[df['hour']==6][['date','close']].rename(columns={'close':'close06'})

# H1 momentum score: bearish closes in hrs 2-6
h1_score = df[df['hour'].between(2,6)].copy()
h1_score['h1_bear'] = (h1_score['close'] < h1_score['open']).astype(int)
h1_score_grp = h1_score.groupby('date').agg(
    h1_mom_score=('h1_bear','sum'),
    h1_mom_n=('h1_bear','count')).reset_index()

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','stoch_k','dow','month','week','year_num']]

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
             .merge(h1_score_grp, on='date', how='left'))
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)

entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['no_gap_up'] = entry['overnight_gap'] <= 0
entry['asia_net_atr'] = entry['asia_net'] / entry['atr14'].clip(lower=1e-9)

# Prior day direction
entry['prior_day_bear'] = entry['date_key'].map(prior_day_map)
entry['prior_day_range'] = entry['date_key'].map(prior_range_map)

# Weekly open vs entry price
entry['week_year'] = entry['year'].astype(str) + '-' + entry['date'].dt.isocalendar().week.astype(int).astype(str).str.zfill(2)
entry['week_open'] = entry['week_year'].map(week_open_map)
entry['above_week_open'] = (entry['open07'] > entry['week_open']).astype(int)

# Asia range / prior day range
entry['asia_compact'] = entry['asia_range'] / entry['prior_day_range'].clip(lower=1e-9)

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
print("C62a: PRIOR DAY CLOSE DIRECTION")
print("="*65)
prior_base = entry.loc[base, 'prior_day_bear'].dropna()
print(f"\n  Prior day close direction on {base.sum()} qualifying trades:")
print(f"  Prior day bearish (close<open): {(prior_base==1).sum()}")
print(f"  Prior day bullish: {(prior_base==0).sum()}")

prior_bear = base & (entry['prior_day_bear'] == 1)
prior_bull = base & (entry['prior_day_bear'] == 0)

print(f"\n  Prior day bear: n={prior_bear.sum()}, Prior day bull: n={prior_bull.sum()}")
print()
pr("Prior day bearish", run_on_mask(prior_bear))
pr("Prior day bullish", run_on_mask(prior_bull))
pr("EMA30 neg + prior day bear", run_on_mask(ema30_neg & prior_bear))
pr("EMA30 neg + prior day bull", run_on_mask(ema30_neg & prior_bull))
pr("C53b + prior day bear", run_on_mask(c53b & prior_bear))
pr("No gap up + prior day bear", run_on_mask(base & entry['no_gap_up'] & prior_bear))
pr("No gap up + prior day bull", run_on_mask(base & entry['no_gap_up'] & prior_bull))

print("\n"+"="*65)
print("C62b: PRICE ABOVE/BELOW WEEKLY OPEN AT ENTRY")
print("="*65)
wo_base = entry.loc[base, 'above_week_open'].dropna()
print(f"\n  Price vs weekly open on {base.sum()} qualifying trades:")
print(f"  Above weekly open (bearish context): {(wo_base==1).sum()}")
print(f"  Below weekly open: {(wo_base==0).sum()}")

above_wo = base & (entry['above_week_open'] == 1)
below_wo = base & (entry['above_week_open'] == 0)

print(f"\n  Above weekly open: n={above_wo.sum()}, Below: n={below_wo.sum()}")
print()
pr("Above weekly open", run_on_mask(above_wo))
pr("Below weekly open", run_on_mask(below_wo))
pr("EMA30 neg + above weekly open", run_on_mask(ema30_neg & above_wo))
pr("EMA30 neg + below weekly open", run_on_mask(ema30_neg & below_wo))
pr("C53b + above weekly open", run_on_mask(c53b & above_wo))
pr("No gap up + above weekly open", run_on_mask(base & entry['no_gap_up'] & above_wo))
pr("No gap up + below weekly open", run_on_mask(base & entry['no_gap_up'] & below_wo))

print("\n"+"="*65)
print("C62c: ASIA RANGE / PRIOR DAY RANGE RATIO (compact Asia)")
print("="*65)
compact_base = entry.loc[base, 'asia_compact'].dropna()
print(f"\n  Asia/prior day range ratio on {base.sum()} qualifying trades:")
print(f"  mean={compact_base.mean():.3f}, median={compact_base.median():.3f}")
print(f"  <0.5: {(compact_base<0.5).sum()}, 0.5-1.0: {((compact_base>=0.5)&(compact_base<1.0)).sum()}, >=1.0: {(compact_base>=1.0).sum()}")

compact = base & (entry['asia_compact'] < 0.6)
wide = base & (entry['asia_compact'] >= 0.6)
very_compact = base & (entry['asia_compact'] < 0.4)

print(f"\n  Compact Asia (<0.6 of prior day): n={compact.sum()}, Wide (>=0.6): n={wide.sum()}")
print(f"  Very compact (<0.4): n={very_compact.sum()}")
print()
pr("Asia compact (<0.6)", run_on_mask(compact))
pr("Asia wide (>=0.6)", run_on_mask(wide))
pr("Very compact (<0.4)", run_on_mask(very_compact))
pr("EMA30 neg + compact", run_on_mask(ema30_neg & compact))
pr("EMA30 neg + wide", run_on_mask(ema30_neg & wide))
pr("C53b + compact", run_on_mask(c53b & compact))
pr("No gap up + compact", run_on_mask(base & entry['no_gap_up'] & compact))

print("\n"+"="*65)
print("C62d: EMA30 NEG + H1 MOMENTUM COMBOS")
print("="*65)
mom_base = entry.loc[base, 'h1_mom_score'].dropna()
print(f"\n  H1 momentum score on {base.sum()} qualifying trades:")
for s in range(6):
    print(f"  Score {s}: {(mom_base==s).sum()} trades")

mom_hi = base & (entry['h1_mom_score'] >= 3)
mom_ge2 = base & (entry['h1_mom_score'] >= 2)
mom_lo = base & (entry['h1_mom_score'] <= 1)

print(f"\n  Score>=3: n={mom_hi.sum()}, Score>=2: n={mom_ge2.sum()}, Score<=1: n={mom_lo.sum()}")
print()
pr("H1 mom >=2 (broader)", run_on_mask(mom_ge2))
pr("EMA30 neg + mom >=2", run_on_mask(ema30_neg & mom_ge2))
pr("EMA30 neg + mom >=3", run_on_mask(ema30_neg & mom_hi))
pr("No gap up + mom >=2", run_on_mask(base & entry['no_gap_up'] & mom_ge2))
pr("No gap up + mom >=3", run_on_mask(base & entry['no_gap_up'] & mom_hi))
pr("EMA30 neg + no gap up + mom>=2", run_on_mask(ema30_neg & entry['no_gap_up'] & mom_ge2))
pr("C53b + mom >=2", run_on_mask(c53b & mom_ge2))
pr("Above weekly open + mom >=2", run_on_mask(above_wo & mom_ge2))
pr("Above weekly open + EMA30 neg", run_on_mask(above_wo & ema30_neg))

print("\nDone.")
