"""Cycle 21: Profit target exploration on v2.3"""
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
             tp_mult=None):
    """tp_mult: if set, take full profit when price drops entry - tp_mult*atr (SHORT position)"""
    df = build_indicators(bars)
    df2 = df.dropna(subset=['atr_pct']).copy()
    grouped = {d: g for d, g in df2.groupby(df2['datetime'].dt.date)}
    trades = []
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
        entry = eb['open']
        stop = entry + stop_mult * atr
        tp = entry - tp_mult * atr if tp_mult is not None else None
        exit_bars_df = day_df[(day_df['datetime'].dt.hour > entry_hour) &
                               (day_df['datetime'].dt.hour <= exit_hour)]
        exit_price = None
        exit_reason = None
        for _, bar in exit_bars_df.iterrows():
            if bar['high'] >= stop:
                exit_price = stop; exit_reason = 'stop'; break
            if tp is not None and bar['low'] <= tp:
                exit_price = tp; exit_reason = 'tp'; break
            if bar['datetime'].hour == exit_hour:
                exit_price = bar['close']; exit_reason = 'time'; break
        if exit_price is None: continue
        pnl = (entry - exit_price) - cost
        yr = str(d)[:4]; q = f"Q{(d.month-1)//3+1}"
        trades.append({'date': str(d), 'year': yr, 'quarter': q, 'pnl': pnl,
                       'exit_reason': exit_reason if exit_reason else 'none'})
    return pd.DataFrame(trades)

def stats(trades):
    if trades.empty or 'year' not in trades.columns: return {'n':0,'pf':0,'avg':0}
    wins = trades[trades['pnl']>0]['pnl'].sum()
    loss = abs(trades[trades['pnl']<0]['pnl'].sum())
    pf = wins/loss if loss>0 else float('inf')
    return {'n':len(trades),'pf':round(pf,2),'avg':round(trades['pnl'].mean()*100,3)}

TD  = load_td('/mnt/project-files/data/eurusd_twelvedata_h1_2020_2026.csv')
FX  = load_fx('/mnt/project-files/data/eurusd_fxopen_h1.csv')

print("=== CYCLE 21: PROFIT TARGET SWEEP ===")
print(f"{'tp_mult':<10} {'TD-IS n':>7} {'TD-IS PF':>9} {'TD-OOS n':>9} {'TD-OOS PF':>10} {'FX n':>6} {'FX PF':>7} {'FX avg%':>9}")

for tp in [None, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
    tdt = backtest(TD, tp_mult=tp)
    fxt = backtest(FX, tp_mult=tp)
    ti  = stats(tdt[tdt['year']<'2024'] if not tdt.empty else tdt)
    to  = stats(tdt[tdt['year']>='2024'] if not tdt.empty else tdt)
    fx  = stats(fxt)
    label = "none" if tp is None else str(tp)
    marker = " <-- v2.3" if tp is None else ""
    print(f"{label:<10} {ti['n']:>7} {ti['pf']:>9} {to['n']:>9} {to['pf']:>10} {fx['n']:>6} {fx['pf']:>7} {fx['avg']:>9}{marker}")

print()
print("=== CYCLE 21: EXIT REASON BREAKDOWN (baseline v2.3 no TP) ===")
fx_base = backtest(FX)
if not fx_base.empty:
    for reason, grp in fx_base.groupby('exit_reason'):
        s = stats(grp)
        print(f"  {reason}: n={s['n']}, PF={s['pf']}, avg={s['avg']}%")
    # Stop-out analysis
    n_stop = (fx_base['exit_reason']=='stop').sum()
    n_time = (fx_base['exit_reason']=='time').sum()
    print(f"\nStop-outs: {n_stop}/{len(fx_base)} ({100*n_stop/len(fx_base):.0f}%)")
    print(f"Time exits: {n_time}/{len(fx_base)} ({100*n_time/len(fx_base):.0f}%)")
