"""
EURUSD Cycles C39–C41
C39: Asia range (high-low / ATR) — did Asia consolidate or range widely?
C40: Price position within Asia range at 07:00 entry
C41: Monthly seasonality — any strong months?
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

# Asia: net, range, high, low
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last'),
    asia_high=('high','max'), asia_low=('low','min')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia['asia_range'] = asia['asia_high'] - asia['asia_low']

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','dow','month']]

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

# C39: Asia range relative to ATR
entry['asia_range_atr'] = entry['asia_range'] / entry['atr14']
# C40: Where within Asia range is entry price (open07)?
# 0 = at Asia low, 1 = at Asia high
entry['asia_pos'] = (entry['open07'] - entry['asia_low']) / (entry['asia_range'].clip(lower=1e-8))

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
print("C39: ASIA RANGE / ATR (how wide was Asia relative to ATR?)")
print("="*65)
e_base = entry[base]
ar = e_base['asia_range_atr']
print(f"\nAsia range/ATR: mean={ar.mean():.2f}, median={ar.median():.2f}, min={ar.min():.2f}, max={ar.max():.2f}")

# Hypothesis: narrow Asia range (consolidation) = better fade (coiled spring)
for thresh_label, lo, hi in [("narrow (<0.5 ATR)", None, 0.5),
                               ("medium (0.5-1.0)", 0.5, 1.0),
                               ("wide (>1.0 ATR)", 1.0, None)]:
    if lo is None:
        mask = base & (entry['asia_range_atr'] < hi)
    elif hi is None:
        mask = base & (entry['asia_range_atr'] >= lo)
    else:
        mask = base & (entry['asia_range_atr'] >= lo) & (entry['asia_range_atr'] < hi)
    r = run_on_mask(mask)
    print(f"\n  Asia range {thresh_label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%")
    if r['by_year']: print(f"    {' | '.join(f'{y}: PF={v}' for y,v in sorted(r['by_year'].items()))}")

# Split at median
med = ar.median()
mask_narrow = base & (entry['asia_range_atr'] < med)
mask_wide = base & (entry['asia_range_atr'] >= med)
print(f"\n--- Below median range ({med:.2f}x ATR) ---")
pr("narrow (below median)", run_on_mask(mask_narrow))
print(f"\n--- Above median range ({med:.2f}x ATR) ---")
pr("wide (above median)", run_on_mask(mask_wide))

print("\n"+"="*65)
print("C40: PRICE POSITION WITHIN ASIA RANGE AT ENTRY")
print("="*65)
ap = e_base['asia_pos']
print(f"\nAsia position (0=low, 1=high): mean={ap.mean():.2f}, median={ap.median():.2f}, min={ap.min():.2f}, max={ap.max():.2f}")

# Hypothesis: near Asia HIGH at 07:00 = momentum persisted into London, harder to fade?
# or: near Asia LOW = reversal already started, better fade?
for thresh_label, lo, hi in [("near bottom (<0.33)", None, 0.33),
                               ("middle (0.33-0.67)", 0.33, 0.67),
                               ("near top (>0.67)", 0.67, None)]:
    if lo is None:
        mask = base & (entry['asia_pos'] < hi)
    elif hi is None:
        mask = base & (entry['asia_pos'] >= lo)
    else:
        mask = base & (entry['asia_pos'] >= lo) & (entry['asia_pos'] < hi)
    r = run_on_mask(mask)
    print(f"\n  Entry position {thresh_label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%")
    if r['by_year']: print(f"    {' | '.join(f'{y}: PF={v}' for y,v in sorted(r['by_year'].items()))}")

# Split at median
med_pos = ap.median()
mask_low = base & (entry['asia_pos'] < med_pos)
mask_high = base & (entry['asia_pos'] >= med_pos)
print(f"\n--- Below median position ({med_pos:.2f}) ---")
pr("lower half of Asia range", run_on_mask(mask_low))
print(f"\n--- Above median position ({med_pos:.2f}) ---")
pr("upper half of Asia range", run_on_mask(mask_high))

print("\n"+"="*65)
print("C41: MONTHLY SEASONALITY")
print("="*65)
e_base2 = entry[base]
print(f"\nTrades by month:")
for m in sorted(e_base2['month'].unique()):
    mask = base & (entry['month'] == m)
    r = run_on_mask(mask)
    mn = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m]
    print(f"  {mn}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%")

# Group quarters
q1 = base & entry['month'].isin([1,2,3])
q2 = base & entry['month'].isin([4,5,6])
q3 = base & entry['month'].isin([7,8,9])
q4 = base & entry['month'].isin([10,11,12])
print("\n--- Quarters ---")
pr("Q1 Jan-Mar", run_on_mask(q1))
pr("Q2 Apr-Jun", run_on_mask(q2))
pr("Q3 Jul-Sep", run_on_mask(q3))
pr("Q4 Oct-Dec", run_on_mask(q4))

print("\nDone.")
