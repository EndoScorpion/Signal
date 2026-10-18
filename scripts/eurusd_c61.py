"""
EURUSD Cycle C61 — EMA30 slope magnitude, EMA50(H1), bars since EMA30 cross, H1 bar momentum score
C61a: EMA30(H1) slope magnitude — does steeper negative slope predict better outcome?
C61b: EMA50(H1) slope at 07:00 — a different H1 timescale (50-bar vs 30-bar)
C61c: Bars since EMA30(H1) last crossed zero — how long has the trend been negative?
C61d: H1 momentum score (count of bearish closes in last 5 H1 bars before entry)
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
df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
df['ema50_slope'] = df['ema50'].diff()

# EMA30 slope normalized by ATR (slope magnitude relative to current volatility)
df['ema30_slope_norm'] = df['ema30_slope'] / df['atr14'].clip(lower=1e-9)

# Bars since EMA30 last crossed zero (from negative to positive or vice versa)
# We want: for each row, how many bars ago did EMA30_slope last cross from pos to neg
# i.e., how long has the current negative trend been running
df['ema30_sign'] = np.sign(df['ema30_slope'])
df['ema30_sign_change'] = (df['ema30_sign'] != df['ema30_sign'].shift(1)).astype(int)
# For bars since last crossover: rolling count since last sign change
bars_since = []
count = 0
for i, row in df.iterrows():
    if row['ema30_sign_change'] == 1:
        count = 0
    else:
        count += 1
    bars_since.append(count)
df['bars_since_ema30_cross'] = bars_since

# H1 momentum score: count bearish closes in last 5 H1 bars before 07:00
# For each date, look at hours 2,3,4,5,6 (5 bars immediately before entry)
# A bar is bearish if close < open
h1_score = df[df['hour'].between(2,6)].copy()
h1_score['h1_bear'] = (h1_score['close'] < h1_score['open']).astype(int)
# Sort by date and hour, then for each date count bears in last 5 bars ending at hour 6
h1_score_grp = h1_score.groupby('date').agg(
    h1_mom_score=('h1_bear','sum'),
    h1_mom_n=('h1_bear','count')).reset_index()
# h1_mom_score = 0-5 (0=all bullish, 5=all bearish)

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

d1 = df.set_index('ts').resample('1D').agg(
    close=('close','last')).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']

# EMA30 slope, EMA50 slope, bars since cross at 07:00
bar07_ind = df[df['hour']==7][['date','ema30_slope','ema30_slope_norm','ema50_slope',
                                'bars_since_ema30_cross']].copy()
bar07_ind = bar07_ind.rename(columns={
    'ema30_slope':'ema30_slope_07',
    'ema30_slope_norm':'ema30_slope_norm_07',
    'ema50_slope':'ema50_slope_07',
    'bars_since_ema30_cross':'bars_since_cross_07'})

bar06 = df[df['hour']==6][['date','close']].rename(columns={'close':'close06'})

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
             .merge(bar07_ind, on='date', how='left')
             .merge(h1_score_grp, on='date', how='left'))
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
pr("C59c EMA30(H1)<0", run_on_mask(ema30_neg))
pr("C53b (SK<60+D1slope<0)", run_on_mask(c53b))

print("\n"+"="*65)
print("C61a: EMA30(H1) SLOPE MAGNITUDE (normalized by ATR)")
print("="*65)
slope_norm_base = entry.loc[base & (entry['ema30_slope_07']<0), 'ema30_slope_norm_07'].dropna()
print(f"\n  EMA30 slope/ATR on {(base & ema30_neg).sum()} negative-slope qualifying trades:")
print(f"  mean={slope_norm_base.mean():.4f}, median={slope_norm_base.median():.4f}")
print(f"  <-0.001: {(slope_norm_base<-0.001).sum()}, -0.001--0.0005: {((slope_norm_base>=-0.001)&(slope_norm_base<-0.0005)).sum()}, "
      f">-0.0005: {(slope_norm_base>=-0.0005).sum()}")

# Among negative-slope trades, is steeper slope better?
slope_steep = base & (entry['ema30_slope_07'] < 0) & (entry['ema30_slope_norm_07'] < -0.001)
slope_shallow = base & (entry['ema30_slope_07'] < 0) & (entry['ema30_slope_norm_07'] >= -0.001)
slope_flat = base & (entry['ema30_slope_07'] < 0) & (entry['ema30_slope_norm_07'] >= -0.0003)

print(f"\n  Steep (norm<-0.001): n={slope_steep.sum()}, Shallow (-0.001 to 0): n={slope_shallow.sum()}")
print(f"  Very shallow (norm>=-0.0003): n={slope_flat.sum()}")
print()
pr("EMA30 neg steep (norm<-0.001)", run_on_mask(slope_steep))
pr("EMA30 neg shallow (>-0.001)", run_on_mask(slope_shallow))
pr("C53b + steep slope", run_on_mask(c53b & slope_steep))
pr("C53b + shallow slope", run_on_mask(c53b & slope_shallow))

# Also look at slope magnitude directly (not normalized)
slope_base_raw = entry.loc[base & (entry['ema30_slope_07']<0), 'ema30_slope_07'].dropna()
print(f"\n  Raw slope on {(base & ema30_neg).sum()} neg trades:")
print(f"  mean={slope_base_raw.mean():.6f}, median={slope_base_raw.median():.6f}")
print(f"  p25={slope_base_raw.quantile(0.25):.6f}, p75={slope_base_raw.quantile(0.75):.6f}")

# Use median as split
median_slope = slope_base_raw.median()
slope_below_med = base & (entry['ema30_slope_07'] < median_slope)
slope_above_med = base & (entry['ema30_slope_07'].between(median_slope, 0, inclusive='left'))
print(f"\n  Below median (steeper negative, <{median_slope:.6f}): n={slope_below_med.sum()}")
print(f"  Above median (shallower, >={median_slope:.6f}, <0): n={(base & (entry['ema30_slope_07'] >= median_slope) & ema30_neg).sum()}")
print()
pr("EMA30 neg below median (steeper)", run_on_mask(slope_below_med))
pr("EMA30 neg above median (shallower)", run_on_mask(base & (entry['ema30_slope_07'] >= median_slope) & ema30_neg))

print("\n"+"="*65)
print("C61b: EMA50(H1) SLOPE AT 07:00")
print("="*65)
ema50_base = entry.loc[base, 'ema50_slope_07'].dropna()
print(f"\n  EMA50(H1) slope on {base.sum()} qualifying trades:")
print(f"  Negative: {(ema50_base<0).sum()}, Positive: {(ema50_base>=0).sum()}")
print(f"  mean={ema50_base.mean():.6f}, median={ema50_base.median():.6f}")

ema50_neg = base & (entry['ema50_slope_07'] < 0)
ema50_pos = base & (entry['ema50_slope_07'] >= 0)

print(f"\n  EMA50 neg: n={ema50_neg.sum()}, EMA50 pos: n={ema50_pos.sum()}")
print()
pr("EMA50(H1) slope negative", run_on_mask(ema50_neg))
pr("EMA50(H1) slope positive", run_on_mask(ema50_pos))
pr("EMA30 neg + EMA50 neg (both negative)", run_on_mask(ema30_neg & ema50_neg))
pr("EMA30 neg + EMA50 pos (divergence)", run_on_mask(ema30_neg & ema50_pos))
pr("C53b + EMA50 neg", run_on_mask(c53b & ema50_neg))
pr("C53b + EMA50 pos", run_on_mask(c53b & ema50_pos))
pr("No gap up + EMA50 neg", run_on_mask(base & entry['no_gap_up'] & ema50_neg))

print("\n"+"="*65)
print("C61c: BARS SINCE EMA30 LAST CROSSED ZERO")
print("="*65)
bars_base = entry.loc[base & ema30_neg, 'bars_since_cross_07'].dropna()
print(f"\n  Bars since EMA30 cross on {(base & ema30_neg).sum()} neg-slope trades:")
print(f"  mean={bars_base.mean():.1f}, median={bars_base.median():.1f}")
print(f"  <10: {(bars_base<10).sum()}, 10-30: {((bars_base>=10)&(bars_base<30)).sum()}, "
      f"30-70: {((bars_base>=30)&(bars_base<70)).sum()}, >=70: {(bars_base>=70).sum()}")

# Recent crossover (trend just turned negative) vs established trend
bars_fresh = base & ema30_neg & (entry['bars_since_cross_07'] < 15)
bars_estab = base & ema30_neg & (entry['bars_since_cross_07'] >= 15)
bars_old = base & ema30_neg & (entry['bars_since_cross_07'] >= 50)

print(f"\n  Fresh neg (<15 bars): n={bars_fresh.sum()}, Established (>=15): n={bars_estab.sum()}")
print(f"  Long-established (>=50): n={bars_old.sum()}")
print()
pr("EMA30 neg fresh (<15 bars)", run_on_mask(bars_fresh))
pr("EMA30 neg established (>=15)", run_on_mask(bars_estab))
pr("EMA30 neg long-estab (>=50)", run_on_mask(bars_old))
pr("C53b + fresh EMA30 neg", run_on_mask(c53b & bars_fresh))
pr("C53b + established EMA30 neg", run_on_mask(c53b & bars_estab))

print("\n"+"="*65)
print("C61d: H1 MOMENTUM SCORE (bearish bars in last 5 H1 bars hrs 2-6)")
print("="*65)
mom_base = entry.loc[base, 'h1_mom_score'].dropna()
print(f"\n  H1 momentum score (0=all bull, 5=all bear) on {base.sum()} qualifying trades:")
print(f"  mean={mom_base.mean():.2f}, median={mom_base.median():.1f}")
for s in range(6):
    print(f"  Score {s}: {(mom_base==s).sum()} trades")

# Low momentum score (mostly bullish bars in hrs 2-6) = Asia still bullish = bigger reversal potential?
# High momentum score (mostly bearish) = pre-entry hours already reversing = confirms SHORT
mom_low = base & (entry['h1_mom_score'] <= 1)    # 0-1 bear bars (mostly bullish)
mom_high = base & (entry['h1_mom_score'] >= 3)   # 3+ bear bars (mostly bearish)
mom_mid = base & (entry['h1_mom_score'] == 2)    # mixed

print(f"\n  Low score (<=1): n={mom_low.sum()}, Mid (==2): n={mom_mid.sum()}, High (>=3): n={mom_high.sum()}")
print()
pr("H1 momentum low (0-1 bear, mostly bullish)", run_on_mask(mom_low))
pr("H1 momentum high (>=3 bear)", run_on_mask(mom_high))
pr("H1 momentum mid (==2)", run_on_mask(mom_mid))
pr("EMA30 neg + low momentum", run_on_mask(ema30_neg & mom_low))
pr("EMA30 neg + high momentum", run_on_mask(ema30_neg & mom_high))
pr("C53b + low momentum", run_on_mask(c53b & mom_low))
pr("C53b + high momentum", run_on_mask(c53b & mom_high))
pr("No gap up + low momentum", run_on_mask(base & entry['no_gap_up'] & mom_low))

print("\nDone.")
