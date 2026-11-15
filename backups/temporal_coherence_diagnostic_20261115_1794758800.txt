#!/usr/bin/env python3
"""
Temporal Coherence Diagnostic: Forward vs Inverted vs Reversed
Purpose: Test whether winning SessionAdaptive variant has genuine signal across time directions
or if it's a regime artifact / directional bias

Variants tested:
1. FORWARD: Original logic (BUY on oversold + accel)
2. INVERTED: Flip signals (SELL on oversold + accel = opposite of forward)
3. REVERSED: Play time backwards (exit becomes entry, entry becomes exit)

If all 3 produce same results → structural problem (exits broken, not directional)
If FORWARD wins but INVERTED/REVERSED lose → directional bias detected
If all 3 win → true signal (temporal coherence)
If all 3 lose → regime artifact
"""

import pandas as pd
import numpy as np
import glob
from datetime import datetime, timedelta

COMM_RT_PTS = 1.5
TP_PTS, SL_PTS = 50, 30
LOTS = 0.01

HOT_WEEKS = [
    ("2015-W23", "2015-06-08", "2015-06-14"),
    ("2011-W02", "2011-01-10", "2011-01-16"),
    ("2010-W38", "2010-09-20", "2010-09-26"),
]

def load_week_data(start, end, tf='M1'):
    pattern = f"/mnt/project-files/EURUSD_{tf}_FXOpen*.csv"
    files = sorted(glob.glob(pattern))
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            if 'Date' in df.columns:
                df['time'] = pd.to_datetime(df['Date'], format='%Y.%m.%d %H:%M')
            df.columns = df.columns.str.lower()
            dfs.append(df)
        except:
            pass
    if not dfs:
        return pd.DataFrame()
    result = pd.concat(dfs, ignore_index=True).sort_values('time').drop_duplicates('time')
    return result[(result['time'] >= start) & (result['time'] <= end)].reset_index(drop=True)

def calc_rsi(prices, period=14):
    """Calculate RSI (14-period)"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def calc_hurst_quick(prices, period=30):
    if len(prices) < period or prices.std() == 0:
        return 0.5
    mean_price = prices.mean()
    cum_dev = (prices - mean_price).cumsum()
    r = cum_dev.max() - cum_dev.min()
    s = prices.std()
    if s < 1e-6:
        return 0.5
    h = np.log(r / s) / np.log(period) if period > 1 else 0.5
    return np.clip(h, 0.0, 1.0)

def backtest_session_adaptive(df, signal_mode='forward'):
    """
    Test SessionAdaptive variant in 3 modes:
    - 'forward': Original BUY logic (z20 < threshold + accel)
    - 'inverted': Flip to SELL logic (flip signal direction)
    - 'reversed': Time-reversed (play price backwards, flip entry/exit)
    """
    if len(df) < 50:
        return {'n': 0, 'wr': 0.0, 'pf': 0.0, 'net': 0.0, 'detail': ''}

    df = df.copy()

    # Handle reversed time
    if signal_mode == 'reversed':
        df = df.iloc[::-1].reset_index(drop=True)

    df['sma5'] = df['close'].rolling(5).mean()
    df['sma20'] = df['close'].rolling(20).mean()
    df['std20'] = df['close'].rolling(20).std()
    df['ema20'] = df['close'].ewm(span=20).mean()

    sma5_diff = df['sma5'].diff()
    df['slope_raw'] = sma5_diff.ewm(span=6).mean() * 10000
    df['slope'] = df['slope_raw']
    df['accel'] = df['slope'].diff()

    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()

    df['z20'] = (df['close'] - df['sma20']) / df['std20'].replace(0, 0.01)
    df['vol_ma'] = df['volume'].rolling(20).mean()
    df['v_ratio'] = df['volume'] / df['vol_ma'].replace(0, 1)
    df['rsi'] = calc_rsi(df['close'])
    df['hour'] = df['time'].dt.hour

    trades = []

    for i in range(40, len(df) - 12):
        hurst = calc_hurst_quick(df['close'].iloc[i-29:i+1].values)

        # Session-adaptive thresholds
        hour = df.iloc[i]['hour']
        if hour >= 8 and hour < 16:  # London
            threshold = -0.6
        elif hour >= 13 and hour < 21:  # NY
            threshold = -0.7
        else:  # Asia
            threshold = -0.5

        # Generate signal based on mode
        signal = None

        if signal_mode == 'forward':
            # Original: BUY on z20 < threshold + accel
            if (df.iloc[i]['z20'] < threshold and
                df.iloc[i]['accel'] <= -0.50 and
                hurst < 0.7):
                signal = 1

        elif signal_mode == 'inverted':
            # Inverted: SELL on z20 > -threshold + accel (flip logic)
            if (df.iloc[i]['z20'] > -threshold and
                df.iloc[i]['accel'] >= 0.50 and
                hurst > 0.3):
                signal = 1

        elif signal_mode == 'reversed':
            # Reversed time: same logic as forward (we're already playing time backwards)
            if (df.iloc[i]['z20'] < threshold and
                df.iloc[i]['accel'] <= -0.50 and
                hurst < 0.7):
                signal = 1

        if signal:
            entry = df.iloc[i]['close']
            for exit_bar in range(i+1, min(i+13, len(df))):
                exit_p = df.iloc[exit_bar]['close']
                pnl = (exit_p - entry) * 100000 * LOTS - COMM_RT_PTS

                tp_trigger = pnl > TP_PTS * 0.0001 * 100000 * LOTS
                sl_trigger = pnl < -SL_PTS * 0.0001 * 100000 * LOTS

                if tp_trigger or sl_trigger:
                    trades.append({
                        'pnl': pnl,
                        'win': pnl > 0,
                        'hour': df.iloc[i]['hour']
                    })
                    break

    if not trades:
        return {'n': 0, 'wr': 0.0, 'pf': 0.0, 'net': 0.0, 'detail': ''}

    trades_df = pd.DataFrame(trades)
    n = len(trades_df)
    wr = 100.0 * trades_df['win'].sum() / n
    wins_pnl = trades_df[trades_df['pnl'] > 0]['pnl'].sum() or 1
    loss_pnl = abs(trades_df[trades_df['pnl'] <= 0]['pnl'].sum()) or 1
    pf = wins_pnl / loss_pnl
    net = trades_df['pnl'].sum()

    return {
        'n': n,
        'wr': round(wr, 1),
        'pf': round(pf, 2),
        'net': round(net, 1),
        'detail': f"trades={n}"
    }

# Main
print("="*160)
print("TEMPORAL COHERENCE DIAGNOSTIC: SessionAdaptive Variant")
print("Testing Forward vs Inverted vs Reversed across 3 hot weeks")
print("="*160)

signal_modes = ['forward', 'inverted', 'reversed']
results = []

for week_label, start_date, end_date in HOT_WEEKS:
    df = load_week_data(start_date, end_date, 'M1')
    if df.empty:
        print(f"⚠ {week_label}: No data")
        continue

    print(f"\n{week_label}")
    print("-"*160)
    print(f"{'Mode':<12} | {'Trades':>5} | {'WR%':>6} | {'PF':>5} | {'Net Pts':>8} | Detail")
    print("-"*160)

    for mode in signal_modes:
        result = backtest_session_adaptive(df, signal_mode=mode)
        marker = "★" if result['wr'] >= 50 else "✓" if result['wr'] >= 30 else " "
        detail = result['detail'][:50] if result['detail'] else "no trades"

        print(f"{marker} {mode:<10} | {result['n']:5} | {result['wr']:6.1f} | {result['pf']:5.2f} | {result['net']:8.1f} | {detail}")

        row = {
            'week': week_label,
            'mode': mode,
            'n': result['n'],
            'wr': result['wr'],
            'pf': result['pf'],
            'net': result['net']
        }
        results.append(row)

print("\n" + "="*160)
print("COHERENCE ANALYSIS")
print("="*160)

if results:
    df_results = pd.DataFrame(results)

    print("\n→ Winners (WR >= 40%):")
    winners = df_results[df_results['wr'] >= 40]
    if len(winners) > 0:
        print(winners[['week', 'mode', 'n', 'wr', 'pf', 'net']].to_string(index=False))
    else:
        print("  None found")

    print("\n→ Summary by mode:")
    mode_summary = df_results.groupby('mode').agg({
        'n': 'sum',
        'wr': 'mean',
        'pf': 'mean',
        'net': 'sum'
    })
    print(mode_summary)

    print("\n→ Coherence interpretation:")
    forward_wr = df_results[df_results['mode'] == 'forward']['wr'].mean()
    inverted_wr = df_results[df_results['mode'] == 'inverted']['wr'].mean()
    reversed_wr = df_results[df_results['mode'] == 'reversed']['wr'].mean()

    if forward_wr > 30 and inverted_wr < 10 and reversed_wr < 10:
        print("  ✓ DIRECTIONAL COHERENCE: Forward wins, inverted/reversed lose → signal is directional")
    elif forward_wr > 30 and inverted_wr > 30 and reversed_wr > 30:
        print("  ★ TEMPORAL COHERENCE: All 3 modes win → true signal across time directions")
    elif forward_wr < 10 and inverted_wr < 10 and reversed_wr < 10:
        print("  ✗ NO COHERENCE: All modes lose → regime artifact or structural problem")
    else:
        print("  ~ MIXED COHERENCE: Partial consistency across modes")

    print("\n" + "="*160)
else:
    print("No results generated.")
