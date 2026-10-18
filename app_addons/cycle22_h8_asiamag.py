"""Cycle 22: H8 pullback confirmation + asia magnitude on v2.3"""
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
             h8_pullback=False, h8_min_retrace=0.0):
    """
    h8_pullback: require the 8-hour bar ending at 08:00 UTC to have closed lower than it opened
                 (price retraced in last H8 bar before entry)
    h8_min_retrace: fraction of ATR that H8 bar must have retraced (close < open by this amount)
    """
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

        # H8 pullback: last 8 hours before entry (hours 23,0,1,2,3,4,5,6 — "night" H8 bar)
        # Simpler: check if Asia session ended with a down bar (last Asia bar closed < opened)
        if h8_pullback:
            # Use last H1 bar of Asia session (06:00 bar) as proxy for H8 "close"
            last_asia_bar = asia.iloc[-1]
            h8_retrace = last_asia_bar['open'] - last_asia_bar['close']  # positive = down move in last bar
            if h8_retrace < h8_min_retrace * atr:
                continue

        entry = eb['open']
        stop = entry + stop_mult * atr
        exit_bars_df = day_df[(day_df['datetime'].dt.hour > entry_hour) &
                               (day_df['datetime'].dt.hour <= exit_hour)]
        exit_price = None
        for _, bar in exit_bars_df.iterrows():
            if bar['high'] >= stop: exit_price = stop; break
            if bar['datetime'].hour == exit_hour: exit_price = bar['close']; break
        if exit_price is None: continue
        pnl = (entry - exit_price) - cost
        yr = str(d)[:4]; q = f"Q{(d.month-1)//3+1}"
        trades.append({'date': str(d), 'year': yr, 'quarter': q, 'pnl': pnl})
    return pd.DataFrame(trades)

def stats(t):
    if t.empty or 'year' not in t.columns: return {'n':0,'pf':0,'avg':0}
    wins = t[t['pnl']>0]['pnl'].sum()
    loss = abs(t[t['pnl']<0]['pnl'].sum())
    pf = wins/loss if loss>0 else float('inf')
    return {'n':len(t),'pf':round(pf,2),'avg':round(t['pnl'].mean()*100,3)}

TD  = load_td('/mnt/project-files/data/eurusd_twelvedata_h1_2020_2026.csv')
FX  = load_fx('/mnt/project-files/data/eurusd_fxopen_h1.csv')

print("=== CYCLE 22: H8 PULLBACK CONFIRMATION ===")
print("Definition: last Asia H1 bar (06:00) must have closed BELOW its open (price pulled back at end of Asia)")
print(f"{'filter':<20} {'TD-IS n':>7} {'TD-IS PF':>9} {'TD-OOS n':>9} {'TD-OOS PF':>10} {'FX n':>6} {'FX PF':>7} {'FX avg%':>9}")

def row(label, tdt, fxt):
    ti = stats(tdt[tdt['year']<'2024'] if not tdt.empty and 'year' in tdt.columns else tdt)
    to = stats(tdt[tdt['year']>='2024'] if not tdt.empty and 'year' in tdt.columns else tdt)
    fx = stats(fxt)
    print(f"{label:<20} {ti['n']:>7} {ti['pf']:>9} {to['n']:>9} {to['pf']:>10} {fx['n']:>6} {fx['pf']:>7} {fx['avg']:>9}")

row("baseline_v2.3", backtest(TD), backtest(FX))
row("h8_any_pullback", backtest(TD, h8_pullback=True, h8_min_retrace=0.0), backtest(FX, h8_pullback=True, h8_min_retrace=0.0))
row("h8_pull>=0.05atr", backtest(TD, h8_pullback=True, h8_min_retrace=0.05), backtest(FX, h8_pullback=True, h8_min_retrace=0.05))
row("h8_pull>=0.10atr", backtest(TD, h8_pullback=True, h8_min_retrace=0.10), backtest(FX, h8_pullback=True, h8_min_retrace=0.10))
row("h8_pull>=0.20atr", backtest(TD, h8_pullback=True, h8_min_retrace=0.20), backtest(FX, h8_pullback=True, h8_min_retrace=0.20))

print()
print("=== CYCLE 22: ASIA MAGNITUDE SWEEP ===")
print(f"{'asia_mult':<12} {'TD-IS n':>7} {'TD-IS PF':>9} {'TD-OOS n':>9} {'TD-OOS PF':>10} {'FX n':>6} {'FX PF':>7} {'FX avg%':>9}")
for am in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]:
    tdt = backtest(TD, asia_mult=am)
    fxt = backtest(FX, asia_mult=am)
    ti = stats(tdt[tdt['year']<'2024'] if not tdt.empty and 'year' in tdt.columns else tdt)
    to = stats(tdt[tdt['year']>='2024'] if not tdt.empty and 'year' in tdt.columns else tdt)
    fx = stats(fxt)
    marker = " <-- v2.3" if am == 0.25 else ""
    print(f"{am:<12} {ti['n']:>7} {ti['pf']:>9} {to['n']:>9} {to['pf']:>10} {fx['n']:>6} {fx['pf']:>7} {fx['avg']:>9}{marker}")
