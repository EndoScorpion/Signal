"""
EURUSD Cycle C50 — Wed vs Thu + Target Exit + Earlier Partial Exit
C50a: Wednesday vs Thursday performance breakdown
C50b: Fixed profit target (take profit at N×ATR)
C50c: Earlier exit times (15:00, 17:00, 19:00 vs 21:00)
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

# Asia
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'), asia_close=('close','last')).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']

# 07:00 bar
bar07 = df[df['hour']==7].copy()
bar07 = bar07.rename(columns={'open':'open07','high':'high07','low':'low07','close':'close07'})
bar07 = bar07[['date','open07','high07','low07','close07',
               'atr14','atr14_pct','ema120_slope','adx14','dow','month']]

# Build comprehensive intra-day dict with all bars 8-20
intra_all = df[df['hour'].between(8,20)][['date','hour','high','low','open','close']].copy()
intra_dict = {}
for row in intra_all.itertuples():
    d = row.date
    if d not in intra_dict: intra_dict[d] = []
    intra_dict[d].append((row.hour, row.high, row.low, row.open, row.close))

# Exit bars at various hours
def get_exit_bar_dict(target_hour):
    b = df[df['hour']==target_hour][['date','open']].rename(columns={'open':f'exit{target_hour}'})
    return dict(zip(b['date'], b[f'exit{target_hour}']))

bar15_dict = get_exit_bar_dict(15)
bar17_dict = get_exit_bar_dict(17)
bar19_dict = get_exit_bar_dict(19)
bar21_dict = get_exit_bar_dict(21)

entry = bar07.merge(asia, on='date')
entry['date_key'] = entry['date']
entry['date'] = pd.to_datetime(entry['date'])
entry['year'] = entry['date'].dt.year

def sim_full(ep, atr, date, exit_hour=21, take_profit_mult=None):
    """Simulate with stop, optional target, and exit at specified hour."""
    stop_px = ep + 0.80*atr
    tp_px = ep - take_profit_mult * atr if take_profit_mult else None

    exit_dicts = {15: bar15_dict, 17: bar17_dict, 19: bar19_dict, 21: bar21_dict}

    for hour, high, low, open_px, close_px in sorted(intra_dict.get(date, [])):
        if hour > exit_hour:
            break
        # Stop hit (check high)
        if high >= stop_px:
            return stop_px, 'stopped'
        # Target hit (check low — we're short, so a low below TP means we hit it)
        if tp_px and low <= tp_px:
            return tp_px, 'target'
        # Exit hour
        if hour == exit_hour:
            return open_px, 'time_exit'

    # Fallback to exit bar open
    fallback = exit_dicts.get(exit_hour, bar21_dict).get(date, ep)
    return fallback, 'time_exit'

def run_on_mask_full(mask, exit_hour=21, take_profit_mult=None):
    results = []
    for _, row in entry[mask].iterrows():
        ep = row['open07']; atr = row['atr14']; date = row['date_key']
        exit_px, reason = sim_full(ep, atr, date, exit_hour, take_profit_mult)
        pnl = (ep - exit_px) / ep - COST
        results.append({'year': row['year'], 'pnl': pnl, 'reason': reason})
    if not results: return {'n':0,'pf':0,'avg':0,'win':0,'by_year':{}}
    r = pd.DataFrame(results)
    w = r[r['pnl']>0]['pnl'].sum(); l = abs(r[r['pnl']<0]['pnl'].sum())
    pf = w/l if l>0 else float('inf')
    by_yr = {yr: round(g[g['pnl']>0]['pnl'].sum()/max(abs(g[g['pnl']<0]['pnl'].sum()),1e-10),2)
             for yr, g in r.groupby('year')}
    stop_pct = (r['reason']=='stopped').mean()*100
    tp_pct = (r['reason']=='target').mean()*100
    return {'n':len(r),'pf':round(pf,2),'avg':round(r['pnl'].mean()*100,3),
            'win':round((r['pnl']>0).mean()*100,1),'by_year':by_yr,
            'stop_pct':round(stop_pct,1),'tp_pct':round(tp_pct,1)}

def run_on_mask(mask):
    return run_on_mask_full(mask, 21, None)

def pr(label, r):
    yr = ' | '.join(f"{y}: PF={v}" for y,v in sorted(r['by_year'].items()))
    extra = f", stopped={r.get('stop_pct','?')}%, target={r.get('tp_pct','?')}%" if r.get('stop_pct') is not None else ""
    print(f"  {label}: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%, win={r['win']}%{extra}")
    if yr: print(f"    {yr}")

base = ((entry['ema120_slope']<0)&(entry['adx14']<30)&(entry['atr14_pct']<0.75)&
        (entry['atr14']>=0.0005)&(entry['dow'].isin([2,3]))&
        (entry['asia_net']>=0.25*entry['atr14']))

print("="*65)
print("BASELINE")
print("="*65)
pr("v2.3 baseline", run_on_mask(base))

print("\n"+"="*65)
print("C50a: WEDNESDAY vs THURSDAY")
print("="*65)
wed = base & (entry['dow']==2)
thu = base & (entry['dow']==3)
print(f"\n  Wednesday: n={wed.sum()}, Thursday: n={thu.sum()}")
print("\n--- Wednesday ---")
pr("Wednesday", run_on_mask(wed))
print("\n--- Thursday ---")
pr("Thursday", run_on_mask(thu))

print("\n"+"="*65)
print("C50b: PROFIT TARGET (take profit at N×ATR)")
print("="*65)
print("\n(Short: target = entry - N×ATR; baseline stop = entry + 0.80×ATR)")
print("(Baseline has no target — holds to 21:00 or stop)")
pr("No target (baseline)", run_on_mask_full(base, 21, None))
for mult in [0.5, 0.8, 1.0, 1.5, 2.0]:
    r = run_on_mask_full(base, 21, mult)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  Target {mult}×ATR: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%, "
          f"win={r['win']}%, stopped={r['stop_pct']}%, target={r['tp_pct']}%  [{yr}]")

print("\n"+"="*65)
print("C50c: EARLIER EXIT TIME")
print("="*65)
print("\n(Current: exit at 21:00 open; test 15:00, 17:00, 19:00)")
for exit_h in [15, 17, 19, 21]:
    r = run_on_mask_full(base, exit_h, None)
    yr = ' | '.join(f"{y}:{v}" for y,v in sorted(r['by_year'].items()))
    print(f"  Exit {exit_h}:00: n={r['n']}, PF={r['pf']}, avg={r['avg']:+.3f}%, win={r['win']}%  [{yr}]")

print("\nDone.")
