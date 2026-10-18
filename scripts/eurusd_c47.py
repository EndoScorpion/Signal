"""
EURUSD Cycle C47 — Prior Week Direction + Non-Q2 Seasonal Breakdown
C47a: Prior week direction (was last week net bullish or bearish for EURUSD?)
C47b: Within non-Q2 trades: Q1 vs Q3 vs Q4 breakdown
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
df['isoyear'] = df['ts'].dt.isocalendar().year.astype(int)
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

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# Weekly open/close: week starts Monday (DOW=0), ends Friday (DOW=4)
# Get each week's first open and last close using isoyear+week
weekly = df.groupby(['isoyear','week']).agg(
    week_open=('open','first'), week_close=('close','last')).reset_index()
weekly['week_return'] = weekly['week_close'] - weekly['week_open']
weekly['week_bearish'] = weekly['week_return'] < 0
# Shift by one: for trade on week W, use prior week W-1
weekly = weekly.sort_values(['isoyear','week']).reset_index(drop=True)
weekly['prev_week_return'] = weekly['week_return'].shift(1)
weekly['prev_week_bearish'] = weekly['week_bearish'].shift(1)

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','dow','month','week','isoyear']]

intra_s = df[df['hour'].between(8,20)][['date','hour','high','open']].copy()
intra_dict = {}
for row in intra_s.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.open))
bar21 = df[df['hour']==21][['date','open']].rename(columns={'open':'exit21'})
bar21_dict = dict(zip(bar21['date'], bar21['exit21']))

entry = bar07.merge(asia, on='date').merge(weekly[['isoyear','week','prev_week_return','prev_week_bearish']],
                                            on=['isoyear','week'], how='left')
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year
# Quarter
entry['quarter'] = ((entry['month'] - 1) // 3 + 1)

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

e_base = entry[base]
pwr = e_base['prev_week_return']
print(f"\nPrior week return on qualifying trades: mean={pwr.mean():.5f}, "
      f"pct_bearish={(pwr<0).mean()*100:.1f}%")

print("\n"+"="*65)
print("C47a: PRIOR WEEK DIRECTION")
print("="*65)

prev_bear_wk = base & (entry['prev_week_bearish']==True)
prev_bull_wk = base & (entry['prev_week_bearish']==False)
prev_na = base & entry['prev_week_bearish'].isna()
print(f"\n  Prior week bearish: n={prev_bear_wk.sum()}, bullish: n={prev_bull_wk.sum()}, NA: n={prev_na.sum()}")
print("\n--- Prior week bearish (EUR fell last week) ---")
pr("Prior week bearish", run_on_mask(prev_bear_wk))
print("\n--- Prior week bullish (EUR rose last week — fade into continuation?) ---")
pr("Prior week bullish", run_on_mask(prev_bull_wk))

# Magnitude of prior week return
print("\nPrior week return tiers:")
med_wr = abs(e_base['prev_week_return'].dropna()).median()
print(f"  Median absolute weekly return: {med_wr:.5f} ({med_wr*10000:.1f} pips)")
for lo, hi, label in [(-99,-0.005,"big bear week >50pip"), (-0.005,-0.001,"small bear"),
                       (-0.001,0.001,"flat week"), (0.001,0.005,"small bull"),
                       (0.005,99,"big bull week >50pip")]:
    mask = base & (entry['prev_week_return'] >= lo) & (entry['prev_week_return'] < hi)
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\n"+"="*65)
print("C47b: NON-Q2 SEASONAL BREAKDOWN (Q1 vs Q3 vs Q4)")
print("="*65)
print("\n(Q2 = April-June is already identified as weak; this tests Q1/Q3/Q4)")
for q, qname in [(1,"Q1 Jan-Mar"), (3,"Q3 Jul-Sep"), (4,"Q4 Oct-Dec")]:
    mask = base & (entry['quarter'] == q)
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}: PF={v}" for y,v in sorted(r['by_year'].items()))
    print(f"\n  {qname}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%, win={r['win']}%")
    if yr: print(f"    {yr}")

# Skip worst non-Q2 quarter if one stands out
q_results = {}
for q in [1,3,4]:
    mask = base & (entry['quarter'] == q)
    q_results[q] = run_on_mask(mask)
worst_q = min(q_results, key=lambda q: q_results[q]['pf'] if q_results[q]['n']>0 else 99)
print(f"\n  Worst quarter among Q1/Q3/Q4: Q{worst_q} (PF={q_results[worst_q]['pf']})")
skip_worst = base & (entry['quarter'] != 2) & (entry['quarter'] != worst_q)
print(f"\n--- Skip Q2 + Skip Q{worst_q} ---")
pr(f"Skip Q2+Q{worst_q}", run_on_mask(skip_worst))

# Q2-only skip (reminder) vs best 2 quarters
skip_q2_only = base & (entry['quarter'] != 2)
print(f"\n--- Skip Q2 only (reminder) ---")
pr("Skip Q2 only", run_on_mask(skip_q2_only))

print("\nDone.")
