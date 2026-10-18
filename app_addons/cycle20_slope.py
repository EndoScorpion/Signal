"""Cycle 20: EMA slope magnitude on v2.3 — does requiring steeper slope help?"""
import pandas as pd, numpy as np, warnings
warnings.filterwarnings('ignore')

def load_td(path):
    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df.sort_values('datetime').reset_index(drop=True)

def load_fx(path):
    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]
    df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True).dt.tz_localize(None)
    return df.sort_values('datetime').reset_index(drop=True)

def build_indicators(df):
    df = df.copy()
    df['prev_close'] = df['close'].shift(1)
    df['tr'] = df[['high','low','prev_close']].apply(
        lambda r: max(r['high']-r['low'],abs(r['high']-r['prev_close']),abs(r['low']-r['prev_close'])),axis=1)
    df['atr14'] = df['tr'].ewm(span=14, adjust=False).mean()
    df['ema120'] = df['close'].ewm(span=120, adjust=False).mean()
    df['slope'] = df['ema120'].diff(1)
    df['pdm'] = (df['high'] - df['high'].shift(1)).clip(lower=0)
    df['ndm'] = (df['low'].shift(1) - df['low']).clip(lower=0)
    df.loc[df['pdm'] < df['ndm'], 'pdm'] = 0
    df.loc[df['ndm'] < df['pdm'], 'ndm'] = 0
    df['pdi'] = 100 * df['pdm'].ewm(span=14,adjust=False).mean() / df['atr14']
    df['ndi'] = 100 * df['ndm'].ewm(span=14,adjust=False).mean() / df['atr14']
    df['dx'] = (abs(df['pdi']-df['ndi']) / (df['pdi']+df['ndi']).replace(0,np.nan)) * 100
    df['adx14'] = df['dx'].ewm(span=14,adjust=False).mean()
    df['atr_pct'] = df['atr14'].rolling(252).rank(pct=True)
    return df

def backtest(bars, cost=0.00008, entry_hour=7, adx_max=30, atr_hi=0.75, stop_mult=0.80,
             exit_hour=21, asia_mult=0.25, weekdays=(2,3), atr_floor=0.0005,
             slope_max=None):
    """slope_max: if set, require slope <= -slope_max (steeper downtrend)"""
    df = build_indicators(bars)
    df2 = df.dropna(subset=['atr_pct']).copy()
    grouped = {d: g for d, g in df2.groupby(df2['datetime'].dt.date)}
    trades = []
    for d in sorted(grouped.keys()):
        day_df = grouped[d]
        wd = pd.Timestamp(d).weekday()
        if wd not in weekdays:
            continue
        asia = day_df[(day_df['datetime'].dt.hour >= 0) & (day_df['datetime'].dt.hour < entry_hour)]
        if asia.empty:
            continue
        entry_bars = day_df[day_df['datetime'].dt.hour == entry_hour]
        if entry_bars.empty:
            continue
        eb = entry_bars.iloc[0]
        atr = eb['atr14']; slope = eb['slope']
        adx = eb['adx14']; atr_p = eb['atr_pct']
        if any(pd.isna(x) for x in [atr, slope, adx, atr_p]) or atr == 0:
            continue
        if atr_floor and atr < atr_floor:
            continue
        asia_move = asia['close'].iloc[-1] - asia['open'].iloc[0]
        if asia_move <= 0 or abs(asia_move) < asia_mult * atr:
            continue
        if slope >= 0 or adx >= adx_max or atr_p > atr_hi:
            continue
        # Additional slope magnitude filter
        if slope_max is not None and slope > -slope_max:
            continue
        entry = eb['open']
        stop = entry + stop_mult * atr
        exit_bars_df = day_df[(day_df['datetime'].dt.hour > entry_hour) &
                               (day_df['datetime'].dt.hour <= exit_hour)]
        exit_price = None
        for _, bar in exit_bars_df.iterrows():
            if bar['high'] >= stop:
                exit_price = stop; break
            if bar['datetime'].hour == exit_hour:
                exit_price = bar['close']; break
        if exit_price is None:
            continue
        pnl = (entry - exit_price) - cost
        yr = str(d)[:4]; q = f"Q{(d.month-1)//3+1}"
        trades.append({'date': str(d), 'year': yr, 'quarter': q, 'pnl': pnl, 'slope': slope})
    return pd.DataFrame(trades)

def stats(trades):
    if trades.empty: return {'n':0,'pf':0,'avg':0}
    wins = trades[trades['pnl']>0]['pnl'].sum()
    loss = abs(trades[trades['pnl']<0]['pnl'].sum())
    pf = wins/loss if loss>0 else float('inf')
    return {'n':len(trades),'pf':round(pf,2),'avg':round(trades['pnl'].mean()*100,3)}

TD  = load_td('/mnt/project-files/data/eurusd_twelvedata_h1_2020_2026.csv')
FX  = load_fx('/mnt/project-files/data/eurusd_fxopen_h1.csv')

# First: understand slope distribution on qualifying trades (no slope filter)
fx_base = backtest(FX)
td_base = backtest(TD)
if not fx_base.empty and 'slope' in fx_base.columns:
    print("=== SLOPE DISTRIBUTION ON QUALIFYING FX TRADES ===")
    print(f"FX slope percentiles: {fx_base['slope'].describe().round(6).to_dict()}")
    td_is = td_base[td_base['year']<'2024']
    if not td_is.empty:
        print(f"TD IS slope percentiles: {td_is['slope'].describe().round(6).to_dict()}")

print()
print("=== CYCLE 20: SLOPE MAGNITUDE SWEEP (any negative = baseline) ===")
print(f"{'slope_max':<12} {'TD-IS n':>7} {'TD-IS PF':>9} {'TD-OOS n':>9} {'TD-OOS PF':>10} {'FX n':>6} {'FX PF':>7} {'FX avg%':>9}")

# Baseline
tdt = backtest(TD, slope_max=None)
fxt = backtest(FX, slope_max=None)
ti  = stats(tdt[tdt['year']<'2024'])
to  = stats(tdt[tdt['year']>='2024'])
fx  = stats(fxt)
print(f"{'any_neg':<12} {ti['n']:>7} {ti['pf']:>9} {to['n']:>9} {to['pf']:>10} {fx['n']:>6} {fx['pf']:>7} {fx['avg']:>9}  <-- v2.3 baseline")

# Slope magnitude thresholds (slope must be <= -threshold)
# Using absolute pips (EURUSD ~0.0001 per pip)
for threshold in [0.00001, 0.00002, 0.00005, 0.0001, 0.0002, 0.0003, 0.0005]:
    tdt = backtest(TD, slope_max=threshold)
    fxt = backtest(FX, slope_max=threshold)
    ti  = stats(tdt[tdt['year']<'2024'])
    to  = stats(tdt[tdt['year']>='2024'])
    fx  = stats(fxt)
    print(f"{threshold:<12} {ti['n']:>7} {ti['pf']:>9} {to['n']:>9} {to['pf']:>10} {fx['n']:>6} {fx['pf']:>7} {fx['avg']:>9}")

print()
print("=== CYCLE 20: SLOPE AS FRACTION OF ATR ===")
print(f"{'slope/atr':<12} {'TD-IS n':>7} {'TD-IS PF':>9} {'TD-OOS n':>9} {'TD-OOS PF':>10} {'FX n':>6} {'FX PF':>7} {'FX avg%':>9}")

# Dynamic threshold: slope must be <= -(frac * atr)
def backtest_slope_atr(bars, frac, **kwargs):
    df = build_indicators(bars)
    df2 = df.dropna(subset=['atr_pct']).copy()
    grouped = {d: g for d, g in df2.groupby(df2['datetime'].dt.date)}
    trades = []
    cost = kwargs.get('cost', 0.00008)
    entry_hour = kwargs.get('entry_hour', 7)
    adx_max = kwargs.get('adx_max', 30)
    atr_hi = kwargs.get('atr_hi', 0.75)
    stop_mult = kwargs.get('stop_mult', 0.80)
    exit_hour = kwargs.get('exit_hour', 21)
    asia_mult = kwargs.get('asia_mult', 0.25)
    weekdays = kwargs.get('weekdays', (2,3))
    atr_floor = kwargs.get('atr_floor', 0.0005)
    for d in sorted(grouped.keys()):
        day_df = grouped[d]
        wd = pd.Timestamp(d).weekday()
        if wd not in weekdays: continue
        asia = day_df[(day_df['datetime'].dt.hour >= 0) & (day_df['datetime'].dt.hour < entry_hour)]
        if asia.empty: continue
        entry_bars = day_df[day_df['datetime'].dt.hour == entry_hour]
        if entry_bars.empty: continue
        eb = entry_bars.iloc[0]
        atr = eb['atr14']; slope = eb['slope']
        adx = eb['adx14']; atr_p = eb['atr_pct']
        if any(pd.isna(x) for x in [atr, slope, adx, atr_p]) or atr == 0: continue
        if atr_floor and atr < atr_floor: continue
        asia_move = asia['close'].iloc[-1] - asia['open'].iloc[0]
        if asia_move <= 0 or abs(asia_move) < asia_mult * atr: continue
        if slope >= 0 or adx >= adx_max or atr_p > atr_hi: continue
        if slope > -(frac * atr): continue  # slope magnitude filter
        entry = eb['open']
        stop = entry + stop_mult * atr
        exit_bars_df = day_df[(day_df['datetime'].dt.hour > entry_hour) & (day_df['datetime'].dt.hour <= exit_hour)]
        exit_price = None
        for _, bar in exit_bars_df.iterrows():
            if bar['high'] >= stop: exit_price = stop; break
            if bar['datetime'].hour == exit_hour: exit_price = bar['close']; break
        if exit_price is None: continue
        pnl = (entry - exit_price) - cost
        yr = str(d)[:4]; q = f"Q{(d.month-1)//3+1}"
        trades.append({'date': str(d), 'year': yr, 'quarter': q, 'pnl': pnl})
    return pd.DataFrame(trades)

for frac in [0.001, 0.002, 0.005, 0.01, 0.02, 0.05]:
    tdt = backtest_slope_atr(TD, frac)
    fxt = backtest_slope_atr(FX, frac)
    ti  = stats(tdt[tdt['year']<'2024'])
    to  = stats(tdt[tdt['year']>='2024'])
    fx  = stats(fxt)
    print(f"{frac:<12} {ti['n']:>7} {ti['pf']:>9} {to['n']:>9} {to['pf']:>10} {fx['n']:>6} {fx['pf']:>7} {fx['avg']:>9}")
