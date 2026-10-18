"""Cycle 14: 2024 gap analysis + entry timing sweep — confirmed implementation"""
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

def backtest(bars, cost=0.00008, entry_hour=7, adx_max=30, atr_hi=0.75, stop_mult=0.85,
             exit_hour=21, asia_mult=0.35, weekdays=(1,2,3), atr_floor=0.0005):
    df = build_indicators(bars)
    # Drop NaN atr_pct before groupby (matches confirmed implementation)
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
        # Asia move: last close of Asia session minus open of first Asia bar
        asia_move = asia['close'].iloc[-1] - asia['open'].iloc[0]
        if asia_move <= 0 or abs(asia_move) < asia_mult * atr:
            continue
        if slope >= 0 or adx >= adx_max or atr_p > atr_hi:
            continue
        entry = eb['open']
        stop = entry + stop_mult * atr
        # Exit bars: hour AFTER entry bar up to exit_hour inclusive
        exit_bars = day_df[(day_df['datetime'].dt.hour > entry_hour) &
                           (day_df['datetime'].dt.hour <= exit_hour)]
        exit_price = None
        for _, bar in exit_bars.iterrows():
            if bar['high'] >= stop:
                exit_price = stop; break
            if bar['datetime'].hour == exit_hour:
                exit_price = bar['close']; break
        if exit_price is None:
            continue
        pnl = (entry - exit_price) - cost
        yr = str(d)[:4]; q = f"Q{(d.month-1)//3+1}"
        trades.append({'date': str(d), 'year': yr, 'quarter': q, 'pnl': pnl})
    return pd.DataFrame(trades)

def stats(trades):
    if trades.empty: return {'n':0,'pf':0,'avg':0}
    wins = trades[trades['pnl']>0]['pnl'].sum()
    loss = abs(trades[trades['pnl']<0]['pnl'].sum())
    pf = wins/loss if loss>0 else float('inf')
    return {'n':len(trades),'pf':round(pf,2),'avg':round(trades['pnl'].mean()*100,3)}

TD  = load_td('/mnt/project-files/data/eurusd_twelvedata_h1_2020_2026.csv')
FX  = load_fx('/mnt/project-files/data/eurusd_fxopen_h1.csv')

td_trades = backtest(TD, entry_hour=7)
fx_trades = backtest(FX, entry_hour=7)

print("=== CYCLE 14: BASELINE CHECK (should match: TD IS n=25 PF=1.44, FX n=44 PF=4.76) ===")
print(f"TD IS (2020-23): {stats(td_trades[td_trades['year']<'2024'])}")
print(f"TD OOS (2024+):  {stats(td_trades[td_trades['year']>='2024'])}")
print(f"FXOpen total:    {stats(fx_trades)}")
print(f"\nFXOpen by year:")
print(fx_trades.groupby('year').apply(lambda g: pd.Series(stats(g))).to_string())

print("\n\n=== CYCLE 14: 2024 QUARTERLY BREAKDOWN ===")
print("\nTD IS (2020-2023) by quarter:")
is_td = td_trades[td_trades['year']<'2024']
print(is_td.groupby(['year','quarter']).apply(lambda g: pd.Series(stats(g))).to_string())

print("\nTD OOS (2024-2026) by quarter:")
oos_td = td_trades[td_trades['year']>='2024']
print(oos_td.groupby(['year','quarter']).apply(lambda g: pd.Series(stats(g))).to_string())

print("\nFXOpen by quarter:")
print(fx_trades.groupby(['year','quarter']).apply(lambda g: pd.Series(stats(g))).to_string())

print("\n\n=== CYCLE 14: ENTRY HOUR SWEEP ===")
print(f"{'Hour':<6} {'TD-IS n':>7} {'TD-IS PF':>9} {'TD-OOS n':>9} {'TD-OOS PF':>10} {'FX n':>6} {'FX PF':>7} {'FX avg%':>9}")
for h in [6, 7, 8, 9]:
    tdt = backtest(TD, entry_hour=h)
    fxt = backtest(FX, entry_hour=h)
    ti  = stats(tdt[tdt['year']<'2024'])
    to  = stats(tdt[tdt['year']>='2024'])
    fx  = stats(fxt)
    print(f"{h:<6} {ti['n']:>7} {ti['pf']:>9} {to['n']:>9} {to['pf']:>10} {fx['n']:>6} {fx['pf']:>7} {fx['avg']:>9}")

print("\n\n=== CYCLE 14: SIGNAL COUNT BY MONTH (FXOpen) ===")
fx_trades['month'] = fx_trades['date'].str[5:7]
print(fx_trades.groupby(['year','month']).size().to_string())
