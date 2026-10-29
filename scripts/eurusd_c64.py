"""
EURUSD Cycle C64 — RSI5 combos, Williams %R(H1), MACD histogram direction
C64a: RSI5(H1)<60 + prior day bear — does prior day direction add to RSI5?
C64b: RSI5(H1)<60 + EMA30 neg + no gap — strongest 3-filter from C63 candidates
C64c: Williams %R(14) on H1 at 07:00 — oversold/overbought at entry
C64d: MACD histogram direction at 07:00 (12/26/9) — momentum confirmation
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

# RSI(5) on H1
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
df['rsi5'] = 100 - (100 / (1 + gain.ewm(span=5, adjust=False).mean() /
                    loss.ewm(span=5, adjust=False).mean().clip(lower=1e-9)))

# Williams %R(14) on H1
low14_w = df['low'].rolling(14).min()
high14_w = df['high'].rolling(14).max()
df['willr14'] = -100 * (high14_w - df['close']) / (high14_w - low14_w).clip(lower=1e-9)

# MACD (12/26/9) histogram
df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
df['macd_line'] = df['ema12'] - df['ema26']
df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
df['macd_hist'] = df['macd_line'] - df['macd_signal']

# D1 EMA20 slope
d1 = df.set_index('ts').resample('1D').agg(
    close=('close','last')).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

# Daily open/close for prior day bear
daily_oc = df.groupby('date').agg(
    day_open=('open','first'),
    day_close=('close','last')).reset_index()
daily_oc['day_bear'] = (daily_oc['day_close'] < daily_oc['day_open']).astype(int)
daily_oc['date'] = pd.to_datetime(daily_oc['date'])
daily_oc = daily_oc.sort_values('date').reset_index(drop=True)
daily_oc['prior_day_bear'] = daily_oc['day_bear'].shift(1)
daily_oc['date_key'] = daily_oc['date'].dt.date
prior_day_map = dict(zip(daily_oc['date_key'], daily_oc['prior_day_bear']))

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

# RSI5 at 07:00 bar (same as C63 — use the entry bar's own RSI5)
bar07_rsi5 = df[df['hour']==7][['date','rsi5']].rename(columns={'rsi5':'rsi5_07'})

# Williams %R at 07:00 bar
bar07_willr = df[df['hour']==7][['date','willr14']].rename(columns={'willr14':'willr_07'})

# MACD histogram at 07:00 bar
bar07_macd = df[df['hour']==7][['date','macd_hist']].rename(columns={'macd_hist':'macd_hist_07'})
# MACD at prior bar (06:00) for direction
bar06_macd_prev = df[df['hour']==6][['date','macd_hist']].rename(columns={'macd_hist':'macd_hist_06'})
bar06_macd_prev['date'] = pd.to_datetime(bar06_macd_prev['date'])

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
               'atr14','atr14_pct','ema120_slope','adx14','stoch_k','dow','week','year_num']]

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
             .merge(bar07_willr, on='date', how='left')
             .merge(bar07_macd, on='date', how='left')
             .merge(h1_score_grp, on='date', how='left'))
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)
entry['prior_day_bear'] = entry['date_key'].map(prior_day_map)

entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['no_gap_up'] = entry['overnight_gap'] <= 0

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
no_gap = base & (entry['no_gap_up'])
rsi5_lo = base & (entry['rsi5_07'] < 60)
prior_bear = base & (entry['prior_day_bear'] == 1)
mom_ge2 = base & (entry['h1_mom_score'] >= 2)

print("="*65)
print("BASELINE + KEY REFERENCES")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))
pr("EMA30(H1)<0 (C59c)", run_on_mask(ema30_neg))
pr("RSI5(H1)<60 (C63b)", run_on_mask(rsi5_lo))
pr("No gap up (C57a)", run_on_mask(no_gap))
pr("C53b (SK<60+D1slope<0)", run_on_mask(c53b))

print("\n"+"="*65)
print("C64a: RSI5(H1)<60 + PRIOR DAY BEAR COMBOS")
print("="*65)
rsi5_prior_base = entry.loc[rsi5_lo, 'prior_day_bear'].dropna()
print(f"\n  Prior day direction on {rsi5_lo.sum()} RSI5<60 qualifying trades:")
print(f"  Prior day bearish: {(rsi5_prior_base==1).sum()}")
print(f"  Prior day bullish: {(rsi5_prior_base==0).sum()}")
print()

rsi5_prior_bear = rsi5_lo & prior_bear
rsi5_prior_bull = rsi5_lo & ~prior_bear
no_gap_rsi5 = no_gap & rsi5_lo
no_gap_rsi5_prior_bear = no_gap & rsi5_lo & prior_bear
ema30_rsi5_prior_bear = ema30_neg & rsi5_lo & prior_bear
c53b_rsi5 = c53b & rsi5_lo

pr("RSI5<60 + prior day bear", run_on_mask(rsi5_prior_bear))
pr("RSI5<60 + prior day bull", run_on_mask(rsi5_prior_bull))
pr("No gap + RSI5<60 (C63b-a)", run_on_mask(no_gap_rsi5))
pr("No gap + RSI5<60 + prior bear", run_on_mask(no_gap_rsi5_prior_bear))
pr("EMA30 neg + RSI5<60 + prior bear", run_on_mask(ema30_rsi5_prior_bear))
pr("C53b + RSI5<60", run_on_mask(c53b_rsi5))

print("\n"+"="*65)
print("C64b: RSI5<60 + EMA30 NEG + NO GAP (THREE-FILTER CORE)")
print("="*65)
ema30_rsi5 = ema30_neg & rsi5_lo
ema30_rsi5_no_gap = ema30_neg & rsi5_lo & no_gap
ema30_rsi5_no_gap_bear = ema30_neg & rsi5_lo & no_gap & prior_bear
ema30_rsi5_mom2 = ema30_neg & rsi5_lo & mom_ge2
no_gap_rsi5_mom2 = no_gap & rsi5_lo & mom_ge2

pr("EMA30 neg + RSI5<60 (C63b-b)", run_on_mask(ema30_rsi5))
pr("EMA30 neg + RSI5<60 + no gap", run_on_mask(ema30_rsi5_no_gap))
pr("EMA30 neg + RSI5<60 + no gap + prior bear", run_on_mask(ema30_rsi5_no_gap_bear))
pr("EMA30 neg + RSI5<60 + mom>=2", run_on_mask(ema30_rsi5_mom2))
pr("No gap + RSI5<60 + mom>=2", run_on_mask(no_gap_rsi5_mom2))

print("\n"+"="*65)
print("C64c: WILLIAMS %R(14) AT ENTRY (from 06:00 bar)")
print("="*65)
willr_base = entry.loc[base, 'willr_07'].dropna()
print(f"\n  Williams %R distribution on {base.sum()} qualifying trades:")
print(f"  mean={willr_base.mean():.1f}, median={willr_base.median():.1f}")
print(f"  <-80 (oversold): {(willr_base<-80).sum()}")
print(f"  -80 to -20: {((willr_base>=-80)&(willr_base<-20)).sum()}")
print(f"  >=-20 (overbought): {(willr_base>=-20).sum()}")
for t in [-80,-70,-60,-50,-40,-30,-20]:
    n_below = (willr_base<t).sum()
    n_above = (willr_base>=t).sum()
    print(f"  threshold {t}: below={n_below}, above={n_above}")

willr_ob = base & (entry['willr_07'] > -30)
willr_mid = base & (entry['willr_07'].between(-70,-30))
willr_os = base & (entry['willr_07'] < -70)

print(f"\n  Overbought >-30: n={willr_ob.sum()}, Mid -70 to -30: n={willr_mid.sum()}, Oversold <-70: n={willr_os.sum()}")
print()
pr("WillR overbought (>-30)", run_on_mask(willr_ob))
pr("WillR mid (-70 to -30)", run_on_mask(willr_mid))
pr("WillR oversold (<-70)", run_on_mask(willr_os))
pr("No gap + WillR overbought", run_on_mask(no_gap & willr_ob))
pr("No gap + WillR mid", run_on_mask(no_gap & willr_mid))
pr("EMA30 neg + WillR overbought", run_on_mask(ema30_neg & willr_ob))
pr("EMA30 neg + WillR mid", run_on_mask(ema30_neg & willr_mid))
pr("RSI5<60 + WillR overbought", run_on_mask(rsi5_lo & willr_ob))
pr("RSI5<60 + WillR mid", run_on_mask(rsi5_lo & willr_mid))

print("\n"+"="*65)
print("C64d: MACD HISTOGRAM DIRECTION AT 07:00 (from 06:00 bar)")
print("="*65)
macd_base = entry.loc[base, 'macd_hist_07'].dropna()
print(f"\n  MACD histogram distribution on {base.sum()} qualifying trades:")
print(f"  mean={macd_base.mean():.6f}, median={macd_base.median():.6f}")
print(f"  Negative (bearish): {(macd_base<0).sum()}")
print(f"  Positive (bullish): {(macd_base>0).sum()}")
macd_neg = base & (entry['macd_hist_07'] < 0)
macd_pos = base & (entry['macd_hist_07'] >= 0)

# MACD direction: merge prior bar (06:00) to see if histogram is falling
bar06_macd_prev['date_key'] = bar06_macd_prev['date'].dt.date
entry['macd_hist_06'] = entry['date_key'].map(dict(zip(bar06_macd_prev['date_key'], bar06_macd_prev['macd_hist_06'])))
macd_detr = base & (entry['macd_hist_07'] < entry['macd_hist_06'])

print(f"\n  MACD neg: n={macd_neg.sum()}, MACD pos: n={macd_pos.sum()}")
print(f"  MACD deteriorating (hist<prev bar): n={macd_detr.sum()}")
print()
pr("MACD histogram < 0", run_on_mask(macd_neg))
pr("MACD histogram >= 0", run_on_mask(macd_pos))
pr("MACD deteriorating (falling)", run_on_mask(macd_detr))
pr("No gap + MACD neg", run_on_mask(no_gap & macd_neg))
pr("EMA30 neg + MACD neg", run_on_mask(ema30_neg & macd_neg))
pr("RSI5<60 + MACD neg", run_on_mask(rsi5_lo & macd_neg))
pr("EMA30 neg + RSI5<60 + MACD neg", run_on_mask(ema30_neg & rsi5_lo & macd_neg))
pr("No gap + RSI5<60 + MACD neg", run_on_mask(no_gap & rsi5_lo & macd_neg))

print("\nDone.")
