"""
EURUSD Cycles C42–C43
C42: Skip Q2 (April-June) — is Apr-Jun consistently poor?
C43: Consecutive Asia up days — does 2+ days of rising Asia confirm fade?
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

# Asia: net per day
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']
asia = asia.sort_values('date').reset_index(drop=True)

# Consecutive Asia up days: count how many of the last N days had positive asia_net
# For each date, check asia_net of previous 1, 2, 3 days
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
print("C42: SKIP Q2 (April-June)")
print("="*65)
skip_q2 = base & (~entry['month'].isin([4,5,6]))
q2_only = base & entry['month'].isin([4,5,6])
print("\n--- Without Q2 (Jan-Mar + Jul-Dec) ---")
pr("skip Q2", run_on_mask(skip_q2))
print("\n--- Q2 only (Apr-Jun) ---")
pr("Q2 only", run_on_mask(q2_only))

# Per-year Q2 breakdown
print("\nQ2 per-year detail:")
for yr in [2024, 2025, 2026]:
    m = q2_only & (entry['year'] == yr)
    r = run_on_mask(m)
    print(f"  {yr} Q2: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%")

print("\n"+"="*65)
print("C43: CONSECUTIVE ASIA UP DAYS (prior day context)")
print("="*65)
e_base = entry[base]
cu = e_base['consec_asia_up']
print(f"\nPrior Asia up days (0-3): {cu.value_counts().sort_index().to_dict()}")

for n_up in [0, 1, 2, 3]:
    mask = base & (entry['consec_asia_up'] == n_up)
    r = run_on_mask(mask)
    print(f"\n  {n_up} of prev 3 days Asia up: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%")
    if r['by_year']: print(f"    {' | '.join(f'{y}: PF={v}' for y,v in sorted(r['by_year'].items()))}")

# Split: 0-1 vs 2-3 prior up days
low_consec = base & (entry['consec_asia_up'] <= 1)
high_consec = base & (entry['consec_asia_up'] >= 2)
print("\n--- 0-1 prior Asia up days (momentum just starting) ---")
pr("0-1 prior up days", run_on_mask(low_consec))
print("\n--- 2-3 prior Asia up days (persistent Asia bull run) ---")
pr("2-3 prior up days", run_on_mask(high_consec))

print("\nDone.")
