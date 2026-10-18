#!/usr/bin/env python3
"""EURUSD Asia-London Fade Cycle 14+ — corrected: asia_up = asia_close - asia_open (net move)."""
import pandas as pd
import numpy as np

DATA = "/mnt/project-files/data/eurusd_fxopen_h1.csv"
COST = 0.00008

df = pd.read_csv(DATA)
df['ts'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
df = df.sort_values('ts').reset_index(drop=True)
df['hour'] = df['ts'].dt.hour
df['dow'] = df['ts'].dt.dayofweek
df['date'] = df['ts'].dt.date

def ema(s, n): return s.ewm(span=n, adjust=False).mean()
def atr14_calc(df):
    h, l, c = df['high'], df['low'], df['close']
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(span=14, adjust=False).mean()

df['ema120'] = ema(df['close'], 120)
df['ema120_slope'] = df['ema120'].diff()
df['atr14'] = atr14_calc(df)
df['atr14_pct'] = df['atr14'].rolling(252).rank(pct=True)

def adx(df, n=14):
    h, l, c = df['high'], df['low'], df['close']
    up = h.diff(); dn = -l.diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr = tr.ewm(span=n,adjust=False).mean()
    pdi = 100*pd.Series(pdm,index=df.index).ewm(span=n,adjust=False).mean()/atr
    ndi = 100*pd.Series(ndm,index=df.index).ewm(span=n,adjust=False).mean()/atr
    dx = (100*(pdi-ndi).abs()/(pdi+ndi).clip(lower=1e-9))
    return dx.ewm(span=n,adjust=False).mean()

df['adx14'] = adx(df)

# Asia session: hours 0-6, net move = close - open
asia = df[df['hour'].between(0,6)].groupby('date').agg(
    asia_open=('open','first'),
    asia_close=('close','last'),
).reset_index()
asia['asia_net'] = asia['asia_close'] - asia['asia_open']  # positive = moved up

entry_bars = df[df['hour'] == 7].copy()
entry_bars = entry_bars.merge(asia, on='date', how='left')

def run_backtest(params):
    asia_mult, adx_max, stop_mult, exit_hour = params
    results = []
    for _, row in entry_bars.iterrows():
        if pd.isna(row['ema120_slope']) or pd.isna(row['adx14']) or pd.isna(row['atr14_pct']): continue
        if row['ema120_slope'] >= 0: continue
        if row['adx14'] >= adx_max: continue
        if row['atr14_pct'] >= 0.75: continue
        if row['atr14'] < 0.0005: continue
        if row['dow'] not in [1,2,3]: continue
        if row['asia_net'] < asia_mult * row['atr14']: continue

        entry_px = row['open']
        stop_px = entry_px + stop_mult * row['atr14']
        ts_date = row['date']
        year = row['ts'].year

        day_bars = df[(df['date'] == ts_date) & (df['hour'].between(8, exit_hour))]
        exit_px = None
        for _, bar in day_bars.iterrows():
            if bar['high'] >= stop_px:
                exit_px = stop_px
                break
        if exit_px is None:
            exit_bar = day_bars[day_bars['hour'] == exit_hour]
            exit_px = exit_bar.iloc[0]['open'] if len(exit_bar) > 0 else (day_bars.iloc[-1]['close'] if len(day_bars) > 0 else entry_px)

        pnl_pct = (entry_px - exit_px) / entry_px - COST
        results.append({'pnl': pnl_pct, 'year': year})

    if not results: return None
    df_r = pd.DataFrame(results)
    wins = df_r['pnl'] > 0
    n = len(df_r)
    gp = df_r[wins]['pnl'].sum()
    gl = df_r[~wins]['pnl'].abs().sum()
    pf = gp / gl if gl > 0 else np.inf
    avg = df_r['pnl'].mean() * 100
    by_year = df_r.groupby('year').apply(lambda g: pd.Series({
        'n': len(g), 'wins': (g['pnl']>0).sum(),
        'pf': round(g[g['pnl']>0]['pnl'].sum() / max(g[g['pnl']<=0]['pnl'].abs().sum(), 1e-9), 2)
    }))
    return {'n': n, 'pf': round(pf,2), 'avg': round(avg,4), 'by_year': by_year}

def fmt(r, label):
    if r is None: return f"{label}: NO TRADES"
    yr = " | ".join([f"{int(y)}: n={int(row['n'])} PF={row['pf']:.2f}" for y, row in r['by_year'].iterrows()])
    return f"{label}: n={r['n']} PF={r['pf']} avg={r['avg']}%  [{yr}]"

print("=== BASELINE v2.1 ===")
baseline = run_backtest((0.35, 30, 0.85, 21))
print(fmt(baseline, "v2.1 baseline"))
print()

print("=== C14a: Asia net-move threshold ===")
for mult in [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
    r = run_backtest((mult, 30, 0.85, 21))
    print(fmt(r, f"asia>={mult}×ATR"))

print()
print("=== C14b: ADX threshold ===")
for adx_max in [20, 25, 28, 30, 35]:
    r = run_backtest((0.35, adx_max, 0.85, 21))
    print(fmt(r, f"ADX<{adx_max}"))

print()
print("=== C14c: Stop multiplier ===")
for stop in [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 1.00, 1.10]:
    r = run_backtest((0.35, 30, stop, 21))
    print(fmt(r, f"stop={stop}×ATR"))

print()
print("=== C14d: Exit time ===")
for exit_h in [16, 17, 18, 19, 20, 21]:
    r = run_backtest((0.35, 30, 0.85, exit_h))
    print(fmt(r, f"exit={exit_h}:00"))

print()
print("=== C14e: EMA slope filter ===")
# EMA slope magnitude: need negative AND |slope| > threshold (strong downtrend)
# Check what slope values look like
print("=== C14f: Best combos ===")
combos = [
    (0.40, 30, 0.85, 21, "asia0.40"),
    (0.45, 30, 0.85, 21, "asia0.45"),
    (0.35, 28, 0.85, 21, "ADX28"),
    (0.35, 25, 0.85, 21, "ADX25"),
    (0.35, 30, 0.80, 21, "stop0.80"),
    (0.35, 30, 0.75, 21, "stop0.75"),
    (0.40, 28, 0.85, 21, "asia0.40+ADX28"),
    (0.40, 28, 0.80, 21, "asia0.40+ADX28+stop0.80"),
    (0.40, 30, 0.80, 21, "asia0.40+stop0.80"),
    (0.45, 28, 0.80, 21, "asia0.45+ADX28+stop0.80"),
    (0.35, 28, 0.80, 21, "ADX28+stop0.80"),
    (0.40, 25, 0.85, 21, "asia0.40+ADX25"),
]
for asia_m, adx_m, stop_m, exit_h, label in combos:
    r = run_backtest((asia_m, adx_m, stop_m, exit_h))
    print(fmt(r, label))
