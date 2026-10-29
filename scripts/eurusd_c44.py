"""
EURUSD Cycle C44 — H4 EMA + Top Candidate Combos
C44a: H4 EMA50 slope at 04:00 UTC (last H4 before entry)
C44b: Combo tests of best pending candidates
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
df['atr14_5d_ago'] = df['atr14'].shift(5)

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

# H4 bars: resample 4-hour, compute EMA50
df_h4 = df.set_index('ts').resample('4h').agg(
    open=('open','first'), high=('high','max'),
    low=('low','min'), close=('close','last')).dropna()
df_h4['ema50_h4'] = df_h4['close'].ewm(span=50, adjust=False).mean()
df_h4['ema50_h4_slope'] = df_h4['ema50_h4'].diff()
df_h4 = df_h4.reset_index()
df_h4['date'] = df_h4['ts'].dt.date
df_h4['h4_hour'] = df_h4['ts'].dt.hour

# Get the 04:00 UTC H4 bar for each date (the bar covering 04:00-07:59 UTC)
h4_04 = df_h4[df_h4['h4_hour'] == 4][['date','ema50_h4_slope']].rename(
    columns={'ema50_h4_slope': 'h4_ema_slope'})

# D1 EMA20 slope
d1 = df.groupby('date').agg(d1_close=('close','last')).reset_index()
d1['ema20_d1'] = d1['d1_close'].ewm(span=20, adjust=False).mean()
d1['d1_slope'] = d1['ema20_d1'].diff()

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia = asia.sort_values('date').reset_index(drop=True)
asia['prev1_net'] = asia['asia_net'].shift(1)
asia['prev2_net'] = asia['asia_net'].shift(2)
asia['prev3_net'] = asia['asia_net'].shift(3)
asia['consec_asia_up'] = (
    (asia['prev1_net'] > 0).astype(int) +
    (asia['prev2_net'] > 0).astype(int) +
    (asia['prev3_net'] > 0).astype(int)
)

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','dow','month','atr14_5d_ago']]

intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = bar07.merge(asia, on='date').merge(h4_04, on='date', how='left')
entry = entry.merge(d1[['date','d1_slope']], on='date', how='left')
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

print("\n"+"="*65)
print("C44a: H4 EMA50 SLOPE AT 04:00 UTC")
print("="*65)
e_base = entry[base]
h4s = e_base['h4_ema_slope']
print(f"\nH4 EMA50 slope distribution: n_valid={h4s.notna().sum()}, "
      f"mean={h4s.mean():.6f}, pct_neg={(h4s<0).mean()*100:.1f}%")

h4_bear = base & (entry['h4_ema_slope'] < 0)
h4_bull = base & (entry['h4_ema_slope'] >= 0)
h4_na = base & entry['h4_ema_slope'].isna()
print(f"\n  H4 EMA<0 (n={h4_bear.sum()}), H4 EMA>=0 (n={h4_bull.sum()}), missing (n={h4_na.sum()})")
print("\n--- H4 EMA50 slope < 0 (H4 downtrend confirms trade) ---")
pr("H4 EMA<0", run_on_mask(h4_bear))
print("\n--- H4 EMA50 slope >= 0 (H4 uptrend — going against) ---")
pr("H4 EMA>=0", run_on_mask(h4_bull))

print("\n"+"="*65)
print("C44b: TOP CANDIDATE COMBOS")
print("="*65)

# Individual pending candidates
c_d1 = base & (entry['d1_slope'] < 0)
c_atr_exp = base & (entry['atr14'] > entry['atr14_5d_ago'])
c_consec = base & (entry['consec_asia_up'] <= 1)
c_skip_q2 = base & (~entry['month'].isin([4,5,6]))
c_bear07 = base & (entry['close07'] < entry['open07'])

print("\n--- Individual candidates (reminder) ---")
pr("D1 slope<0 (C25b)", run_on_mask(c_d1))
pr("ATR expanding (C37)", run_on_mask(c_atr_exp))
pr("0-1 prior Asia up (C43)", run_on_mask(c_consec))
pr("Skip Q2 (C42)", run_on_mask(c_skip_q2))
pr("Bear07 (C35)", run_on_mask(c_bear07))

print("\n--- Pairwise combos ---")
combos = [
    ("D1+ATR_exp", c_d1 & c_atr_exp),
    ("D1+consec", c_d1 & c_consec),
    ("D1+skipQ2", c_d1 & c_skip_q2),
    ("ATR_exp+consec", c_atr_exp & c_consec),
    ("ATR_exp+skipQ2", c_atr_exp & c_skip_q2),
    ("consec+skipQ2", c_consec & c_skip_q2),
    ("D1+bear07", c_d1 & c_bear07),
    ("consec+bear07", c_consec & c_bear07),
]
for label, mask in combos:
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\n--- Triple combos ---")
triples = [
    ("D1+consec+skipQ2", c_d1 & c_consec & c_skip_q2),
    ("D1+ATR_exp+consec", c_d1 & c_atr_exp & c_consec),
    ("consec+skipQ2+ATR_exp", c_consec & c_skip_q2 & c_atr_exp),
]
for label, mask in triples:
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\nDone.")
