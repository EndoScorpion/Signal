"""
EURUSD Cycle C65 — WillR exclusion filter, CCI(20) H1, Bollinger Band position
C65a: WillR >-30 exclusion (remove overbought entries) — improving baseline and combos
C65b: CCI(20) on H1 at 07:00 — commodity channel index as momentum/reversal signal
C65c: Bollinger Band position at 07:00 — is price near upper/lower band?
C65d: Price vs prior day high at 07:00 — did Asia close above prior day high?
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

# Williams %R(14)
df['willr14'] = -100 * (high14 - df['close']) / (high14 - low14).clip(lower=1e-9)

# RSI(5) on H1
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
df['rsi5'] = 100 - (100 / (1 + gain.ewm(span=5, adjust=False).mean() /
                    loss.ewm(span=5, adjust=False).mean().clip(lower=1e-9)))

# CCI(20): (Typical Price - SMA20) / (0.015 * Mean Deviation)
df['tp'] = (df['high'] + df['low'] + df['close']) / 3
sma20_tp = df['tp'].rolling(20).mean()
mad20 = df['tp'].rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
df['cci20'] = (df['tp'] - sma20_tp) / (0.015 * mad20.clip(lower=1e-9))

# Bollinger Bands (20, 2) on H1 close
sma20 = df['close'].rolling(20).mean()
std20 = df['close'].rolling(20).std()
df['bb_upper'] = sma20 + 2*std20
df['bb_lower'] = sma20 - 2*std20
df['bb_width'] = df['bb_upper'] - df['bb_lower']
df['bb_pct'] = (df['close'] - df['bb_lower']) / df['bb_width'].clip(lower=1e-9)  # 0=lower, 1=upper

# D1 EMA20 slope
d1 = df.set_index('ts').resample('1D').agg(
    close=('close','last')).dropna(subset=['close']).reset_index()
d1['ema20_d1'] = d1['close'].ewm(span=20, adjust=False).mean()
d1['ema20_d1_slope'] = d1['ema20_d1'].diff()
d1['date'] = d1['ts'].dt.date
d1_map_slope = dict(zip(d1['date'], d1['ema20_d1_slope']))

# Daily open/close for prior day bear + prior day high
daily_oc = df.groupby('date').agg(
    day_open=('open','first'),
    day_close=('close','last'),
    day_high=('high','max')).reset_index()
daily_oc['day_bear'] = (daily_oc['day_close'] < daily_oc['day_open']).astype(int)
daily_oc['date'] = pd.to_datetime(daily_oc['date'])
daily_oc = daily_oc.sort_values('date').reset_index(drop=True)
daily_oc['prior_day_bear'] = daily_oc['day_bear'].shift(1)
daily_oc['prior_day_high'] = daily_oc['day_high'].shift(1)
daily_oc['date_key'] = daily_oc['date'].dt.date
prior_day_map = dict(zip(daily_oc['date_key'], daily_oc['prior_day_bear']))
prior_high_map = dict(zip(daily_oc['date_key'], daily_oc['prior_day_high']))

# Asia session
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
    asia_high=('high','max'),
    asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']

bar07_ema30 = df[df['hour']==7][['date','ema30_slope']].rename(columns={'ema30_slope':'ema30_slope_07'})
bar06 = df[df['hour']==6][['date','close']].rename(columns={'close':'close06'})
bar07_rsi5 = df[df['hour']==7][['date','rsi5']].rename(columns={'rsi5':'rsi5_07'})
bar07_willr = df[df['hour']==7][['date','willr14']].rename(columns={'willr14':'willr_07'})
bar07_cci = df[df['hour']==7][['date','cci20']].rename(columns={'cci20':'cci_07'})
bar07_bb = df[df['hour']==7][['date','bb_pct']].rename(columns={'bb_pct':'bb_pct_07'})

h1_score = df[df['hour'].between(2,6)].copy()
h1_score['h1_bear'] = (h1_score['close'] < h1_score['open']).astype(int)
h1_score_grp = h1_score.groupby('date').agg(
    h1_mom_score=('h1_bear','sum')).reset_index()

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
             .merge(bar07_cci, on='date', how='left')
             .merge(bar07_bb, on='date', how='left')
             .merge(h1_score_grp, on='date', how='left'))
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
entry['d1_slope'] = entry['date_key'].map(d1_map_slope)
entry['prior_day_bear'] = entry['date_key'].map(prior_day_map)
entry['prior_day_high'] = entry['date_key'].map(prior_high_map)

entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['no_gap_up'] = entry['overnight_gap'] <= 0

# Price vs prior day high at entry
entry['above_prior_high'] = (entry['open07'] > entry['prior_day_high']).astype(int)

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
willr_not_ob = base & (entry['willr_07'] <= -30)  # EXCLUDE overbought
willr_ob = base & (entry['willr_07'] > -30)

print("="*65)
print("BASELINE + KEY REFERENCES")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))
pr("EMA30(H1)<0 (C59c)", run_on_mask(ema30_neg))
pr("RSI5(H1)<60 (C63b)", run_on_mask(rsi5_lo))
pr("No gap up (C57a)", run_on_mask(no_gap))
pr("EMA30 neg + RSI5<60 + no gap (C64b)", run_on_mask(ema30_neg & rsi5_lo & no_gap))

print("\n"+"="*65)
print("C65a: WILLR NOT OVERBOUGHT (<=−30) AS EXCLUSION FILTER")
print("="*65)
wb = entry.loc[base, 'willr_07'].dropna()
print(f"\n  WillR on {base.sum()} qualifying trades: mean={wb.mean():.1f}, median={wb.median():.1f}")
print(f"  WillR <=−30 (not overbought): {(wb<=-30).sum()}, WillR >−30 (excluded): {(wb>-30).sum()}")
print()
pr("Baseline excl. WillR overbought (WillR<=−30)", run_on_mask(willr_not_ob))
pr("EMA30 neg + WillR not ob", run_on_mask(ema30_neg & willr_not_ob))
pr("No gap + WillR not ob", run_on_mask(no_gap & willr_not_ob))
pr("RSI5<60 + WillR not ob", run_on_mask(rsi5_lo & willr_not_ob))
pr("EMA30 neg + RSI5<60 + WillR not ob", run_on_mask(ema30_neg & rsi5_lo & willr_not_ob))
pr("EMA30 neg + RSI5<60 + no gap + WillR not ob", run_on_mask(ema30_neg & rsi5_lo & no_gap & willr_not_ob))
pr("No gap + RSI5<60 + WillR not ob", run_on_mask(no_gap & rsi5_lo & willr_not_ob))
pr("Prior bear + WillR not ob", run_on_mask(prior_bear & willr_not_ob))

print("\n"+"="*65)
print("C65b: CCI(20) AT 07:00 BAR")
print("="*65)
cci_base = entry.loc[base, 'cci_07'].dropna()
print(f"\n  CCI distribution on {base.sum()} qualifying trades:")
print(f"  mean={cci_base.mean():.1f}, median={cci_base.median():.1f}")
print(f"  <-100 (oversold): {(cci_base<-100).sum()}")
print(f"  -100 to 0: {((cci_base>=-100)&(cci_base<0)).sum()}")
print(f"  0 to 100: {((cci_base>=0)&(cci_base<100)).sum()}")
print(f"  >=100 (overbought): {(cci_base>=100).sum()}")
for t in [-200,-100,-50,0,50,100,200]:
    nb = (cci_base<t).sum(); na = (cci_base>=t).sum()
    print(f"  CCI threshold {t}: below={nb}, above={na}")

# CCI for SHORT: positive CCI = above average price = bearish reversal candidate
# Very high CCI >100 = overbought, good for SHORT entry
# CCI < 0 = below average, might be too depressed
cci_pos = base & (entry['cci_07'] >= 0)    # above typical price = bullish extension
cci_neg = base & (entry['cci_07'] < 0)     # below typical price
cci_ob = base & (entry['cci_07'] >= 100)   # overbought
cci_not_ob = base & (entry['cci_07'] < 100)

print(f"\n  CCI>=0: n={cci_pos.sum()}, CCI<0: n={cci_neg.sum()}, CCI>=100: n={cci_ob.sum()}, CCI<100: n={cci_not_ob.sum()}")
print()
pr("CCI >= 0 (above avg)", run_on_mask(cci_pos))
pr("CCI < 0 (below avg)", run_on_mask(cci_neg))
pr("CCI >= 100 (overbought)", run_on_mask(cci_ob))
pr("CCI < 100 (not overbought)", run_on_mask(cci_not_ob))
pr("No gap + CCI >= 0", run_on_mask(no_gap & cci_pos))
pr("No gap + CCI < 0", run_on_mask(no_gap & cci_neg))
pr("EMA30 neg + CCI >= 0", run_on_mask(ema30_neg & cci_pos))
pr("RSI5<60 + CCI >= 0", run_on_mask(rsi5_lo & cci_pos))
pr("RSI5<60 + CCI < 0", run_on_mask(rsi5_lo & cci_neg))

print("\n"+"="*65)
print("C65c: BOLLINGER BAND POSITION AT 07:00 BAR")
print("="*65)
bb_base = entry.loc[base, 'bb_pct_07'].dropna()
print(f"\n  BB %B on {base.sum()} qualifying trades:")
print(f"  mean={bb_base.mean():.3f}, median={bb_base.median():.3f}")
print(f"  Above upper band (>1.0): {(bb_base>1.0).sum()}")
print(f"  Upper half (0.5-1.0): {((bb_base>=0.5)&(bb_base<=1.0)).sum()}")
print(f"  Lower half (0-0.5): {((bb_base>=0)&(bb_base<0.5)).sum()}")
print(f"  Below lower band (<0): {(bb_base<0).sum()}")
for t in [0.3, 0.5, 0.7, 0.8, 0.9, 1.0]:
    nb = (bb_base<t).sum(); na = (bb_base>=t).sum()
    print(f"  BB threshold {t}: below={nb}, above={na}")

# For SHORT: price near/above upper band = overextended = good short candidate
# %B > 0.8 means price near upper Bollinger = extended
bb_hi = base & (entry['bb_pct_07'] >= 0.6)  # upper portion of bands
bb_lo = base & (entry['bb_pct_07'] < 0.6)   # lower/mid portion
bb_ext = base & (entry['bb_pct_07'] >= 0.8)  # extended near upper band

print(f"\n  BB>=0.6 (upper): n={bb_hi.sum()}, BB<0.6 (mid/lower): n={bb_lo.sum()}, BB>=0.8 (extended): n={bb_ext.sum()}")
print()
pr("BB high (>=0.6)", run_on_mask(bb_hi))
pr("BB low (<0.6)", run_on_mask(bb_lo))
pr("BB extended (>=0.8)", run_on_mask(bb_ext))
pr("No gap + BB high", run_on_mask(no_gap & bb_hi))
pr("No gap + BB low", run_on_mask(no_gap & bb_lo))
pr("EMA30 neg + BB high", run_on_mask(ema30_neg & bb_hi))
pr("RSI5<60 + BB high", run_on_mask(rsi5_lo & bb_hi))
pr("RSI5<60 + BB low", run_on_mask(rsi5_lo & bb_lo))

print("\n"+"="*65)
print("C65d: PRICE VS PRIOR DAY HIGH AT ENTRY")
print("="*65)
above_ph = entry.loc[base, 'above_prior_high'].dropna()
print(f"\n  Price vs prior day high on {base.sum()} qualifying trades:")
print(f"  Above prior day high: {(above_ph==1).sum()}")
print(f"  At or below prior day high: {(above_ph==0).sum()}")

abv_ph = base & (entry['above_prior_high'] == 1)
blw_ph = base & (entry['above_prior_high'] == 0)

print(f"\n  Above prior high: n={abv_ph.sum()}, Below: n={blw_ph.sum()}")
print()
pr("Above prior day high", run_on_mask(abv_ph))
pr("At/below prior day high", run_on_mask(blw_ph))
pr("No gap + above prior high", run_on_mask(no_gap & abv_ph))
pr("No gap + below prior high", run_on_mask(no_gap & blw_ph))
pr("EMA30 neg + above prior high", run_on_mask(ema30_neg & abv_ph))
pr("EMA30 neg + below prior high", run_on_mask(ema30_neg & blw_ph))
pr("RSI5<60 + above prior high", run_on_mask(rsi5_lo & abv_ph))
pr("RSI5<60 + below prior high", run_on_mask(rsi5_lo & blw_ph))

print("\nDone.")
