"""
EURUSD Cycle C46 — Open Gap + EMA Slope Magnitude
C46a: Overnight gap (07:00 open vs prior 21:00 close) — gap-up into the short
C46b: EMA120 slope magnitude — does steeper downtrend improve the fade?
C46c: ATR floor tightening — current 5 pip floor, test 7/8/10 pip to reduce low-vol noise
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

# Prior 21:00 close for gap calculation
bar21_prior = df[df['hour']==21][['date','open']].rename(columns={'open':'prior_close21'})
bar21_prior['date_dt'] = pd.to_datetime(bar21_prior['date'])
bar21_prior = bar21_prior.sort_values('date_dt').reset_index(drop=True)
bar21_prior['next_date'] = bar21_prior['date_dt'].shift(-1).dt.date
# map: trade_date -> prior day's 21:00 open
prior_close_map = dict(zip(bar21_prior['next_date'], bar21_prior['prior_close21']))

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','dow']]

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

# Open gap: 07:00 open vs prior day's 21:00 close
entry['prior_close21'] = entry['date_key'].map(prior_close_map)
entry['open_gap'] = entry['open07'] - entry['prior_close21']
entry['open_gap_atr'] = entry['open_gap'] / entry['atr14']

# EMA slope normalized (in ATR/bar units)
entry['ema_slope_norm'] = entry['ema120_slope'] / entry['atr14']

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
print(f"\nOpen gap (07:00 open vs prior 21:00) on qualifying trades:")
og = e_base['open_gap_atr'].dropna()
print(f"  n_valid={len(og)}, mean={og.mean():.3f} ATR, pct_positive={(og>0).mean()*100:.1f}%")
print(f"  min={og.min():.3f}, p25={og.quantile(0.25):.3f}, p75={og.quantile(0.75):.3f}, max={og.max():.3f}")

es = e_base['ema_slope_norm']
print(f"\nEMA120 slope (normalized by ATR) on qualifying trades:")
print(f"  mean={es.mean():.4f}, min={es.min():.4f}, max={es.max():.4f}, "
      f"p25={es.quantile(0.25):.4f}, p75={es.quantile(0.75):.4f}")

print("\n"+"="*65)
print("C46a: OVERNIGHT OPEN GAP")
print("="*65)
print("\n(Gap = 07:00 open minus prior 21:00 close; positive = EUR gapped up)")

gap_pos = base & (entry['open_gap'] > 0)
gap_neg = base & (entry['open_gap'] <= 0)
gap_na = base & entry['open_gap'].isna()
print(f"\n  Gap up (n={gap_pos.sum()}), Gap down/flat (n={gap_neg.sum()}), Missing (n={gap_na.sum()})")
print("\n--- Gap up (EUR opened higher than prior close — gap into the short) ---")
pr("Gap up", run_on_mask(gap_pos))
print("\n--- Gap down/flat (EUR opened flat or lower) ---")
pr("Gap down/flat", run_on_mask(gap_neg))

# Gap magnitude sweep (in ATR units)
print("\nGap magnitude tiers (positive = gapped up into the short):")
for lo, hi, label in [(-99,-0.10,"gap down >0.1 ATR"),(-0.10,0,"small gap down"),
                       (0,0.05,"tiny gap up <0.05"),
                       (0.05,0.15,"moderate gap up 0.05-0.15"),
                       (0.15,99,"large gap up >0.15")]:
    mask = base & (entry['open_gap_atr'] >= lo) & (entry['open_gap_atr'] < hi)
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\n"+"="*65)
print("C46b: EMA SLOPE MAGNITUDE")
print("="*65)
print("\n(More negative slope = stronger downtrend)")

slope_med = e_base['ema_slope_norm'].median()
print(f"\nMedian EMA slope: {slope_med:.4f} ATR/bar")

steep = base & (entry['ema_slope_norm'] < slope_med)
shallow = base & (entry['ema_slope_norm'] >= slope_med) & (entry['ema120_slope'] < 0)
print(f"\n  Steep slope (<median, n={steep.sum()}), Shallow slope (>median & <0, n={shallow.sum()})")
print("\n--- Steep slope (more negative than median — strong downtrend) ---")
pr("Steep EMA slope", run_on_mask(steep))
print("\n--- Shallow slope (between median and 0 — weak downtrend) ---")
pr("Shallow EMA slope", run_on_mask(shallow))

print("\nEMA slope quartile breakdown:")
q = e_base['ema_slope_norm'].quantile([0.25, 0.50, 0.75])
thresholds = [(-99, q[0.25], "Q1 (steepest)"), (q[0.25], q[0.50], "Q2"),
              (q[0.50], q[0.75], "Q3"), (q[0.75], 0, "Q4 (shallowest)")]
for lo, hi, ql in thresholds:
    mask = base & (entry['ema_slope_norm'] >= lo) & (entry['ema_slope_norm'] < hi)
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  {ql} (slope {lo:.4f} to {hi:.4f}): n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

print("\n"+"="*65)
print("C46c: ATR FLOOR (minimum ATR to require)")
print("="*65)
print("\n(Current: >=0.0005 = 5 pips. Higher floor = require more volatility)")
for floor_pip in [5, 6, 7, 8, 10]:
    floor = floor_pip * 0.0001
    mask = ((entry['ema120_slope']<0)&(entry['adx14']<30)&(entry['atr14_pct']<0.75)&
            (entry['atr14']>=floor)&(entry['dow'].isin([2,3]))&
            (entry['asia_net']>=0.25*entry['atr14']))
    r = run_on_mask(mask)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  ATR>={floor_pip}pip: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%  [{yr}]")

# Which trades are excluded by raising the floor?
excluded_6pip = base & (entry['atr14'] < 0.0006)
excluded_7pip = base & (entry['atr14'] < 0.0007)
print(f"\n  Trades with ATR 5-6 pip (marginal): n={excluded_6pip.sum()}")
print(f"  Trades with ATR 5-7 pip (marginal): n={excluded_7pip.sum()}")
if excluded_6pip.sum() > 0:
    pr("5-6 pip ATR trades (excluded by 6pip floor)", run_on_mask(excluded_6pip))
if excluded_7pip.sum() > 0 and excluded_7pip.sum() > excluded_6pip.sum():
    pr("6-7 pip ATR trades", run_on_mask(base & (entry['atr14']>=0.0006) & (entry['atr14']<0.0007)))

print("\nDone.")
