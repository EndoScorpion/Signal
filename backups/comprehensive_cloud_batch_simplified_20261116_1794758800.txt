#!/usr/bin/env python3
"""
Comprehensive Cloud Batch — Simplified Phase 4
SessionAdaptive + Formula Variants only (reduce dimension filters for now)
Purpose: Test formula variants on confirmed entries, apply cost model
"""

import pandas as pd
import numpy as np
import glob
from datetime import datetime

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

def formula_variants(z20, accel):
    """Apply 4 formula variants"""
    linear = z20 * accel
    quad = z20 * (accel ** 2) if accel != 0 else 0
    cubic = z20 * (accel ** 3) if accel != 0 else 0
    geo = z20 * np.sqrt(abs(accel)) * np.sign(accel) if accel != 0 else 0
    return {'linear': linear, 'quad': quad, 'cubic': cubic, 'geo': geo}

def backtest_formulas(df):
    """Test all 4 formula variants on SessionAdaptive entries"""
    if len(df) < 50:
        return []

    df = df.copy()

    # Basic indicators
    df['sma5'] = df['close'].rolling(5).mean()
    sma5_diff = df['sma5'].diff()
    df['slope_raw'] = sma5_diff.ewm(span=6).mean() * 10000
    df['accel'] = df['slope_raw'].diff()

    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()

    df['sma20'] = df['close'].rolling(20).mean()
    std20 = df['close'].rolling(20).std()
    df['z20'] = (df['close'] - df['sma20']) / std20.replace(0, 0.01)

    df['hour'] = df['time'].dt.hour
    df['rsi'] = calc_rsi(df['close'])

    trades = []

    for i in range(40, len(df) - 12):
        hour = df.iloc[i]['hour']
        z20 = df.iloc[i]['z20']
        accel = df.iloc[i]['accel']
        hurst = calc_hurst_quick(df['close'].iloc[i-29:i+1].values)
        rsi = df.iloc[i]['rsi']

        # Session-adaptive thresholds
        if hour >= 8 and hour < 16:
            threshold = -0.6
            session = 'london'
        elif hour >= 13 and hour < 21:
            threshold = -0.7
            session = 'ny'
        else:
            threshold = -0.5
            session = 'asia'

        # Entry gate (base SessionAdaptive)
        if not ((z20 < threshold) and (accel <= -0.50) and (hurst < 0.7)):
            continue

        # Entry confirmed
        entry = df.iloc[i]['close']
        entry_time = df.iloc[i]['time']

        # Test all formula variants
        formulas = formula_variants(z20, accel)

        for formula_name, formula_val in formulas.items():
            # Exit search (12 bars forward)
            for exit_bar in range(i+1, min(i+13, len(df))):
                exit_p = df.iloc[exit_bar]['close']
                gross_pnl = (exit_p - entry) * 100000 * LOTS
                net_pnl = gross_pnl - COMM_RT_PTS

                tp_trigger = net_pnl > TP_PTS * 0.0001 * 100000 * LOTS
                sl_trigger = net_pnl < -SL_PTS * 0.0001 * 100000 * LOTS

                if tp_trigger or sl_trigger:
                    trades.append({
                        'formula': formula_name,
                        'session': session,
                        'z20': round(z20, 3),
                        'accel': round(accel, 3),
                        'hurst': round(hurst, 3),
                        'rsi': round(rsi, 1),
                        'entry': round(entry, 5),
                        'exit': round(exit_p, 5),
                        'gross_pnl': round(gross_pnl, 1),
                        'net_pnl': round(net_pnl, 1),
                        'win': net_pnl > 0,
                        'bars': exit_bar - i,
                    })
                    break

    return trades

# Main
print("="*160)
print("COMPREHENSIVE CLOUD BATCH — Simplified Phase 4")
print("SessionAdaptive + All 4 Formula Variants")
print("="*160)

all_trades = []

for week_label, start_date, end_date in HOT_WEEKS:
    print(f"\n{week_label}: Loading data...")
    df = load_week_data(start_date, end_date, 'M1')

    if df.empty:
        print(f"  No data")
        continue

    print(f"  Data loaded: {len(df)} bars")

    trades = backtest_formulas(df)

    if not trades:
        print(f"  No trades generated")
        continue

    for trade in trades:
        trade['week'] = week_label
        all_trades.append(trade)

    # Summary
    trades_df = pd.DataFrame(trades)
    n = len(trades_df)
    wr = 100.0 * trades_df['win'].sum() / n if n > 0 else 0
    wins_pnl = trades_df[trades_df['net_pnl'] > 0]['net_pnl'].sum() or 1
    loss_pnl = abs(trades_df[trades_df['net_pnl'] <= 0]['net_pnl'].sum()) or 1
    pf = wins_pnl / loss_pnl
    net = trades_df['net_pnl'].sum()

    print(f"  Results: {n} trades | WR {wr:.1f}% | PF {pf:.2f} | Net {net:.1f} pts")

    # By formula
    for formula in ['linear', 'quad', 'cubic', 'geo']:
        f_trades = trades_df[trades_df['formula'] == formula]
        if len(f_trades) > 0:
            f_wr = 100.0 * f_trades['win'].sum() / len(f_trades)
            f_net = f_trades['net_pnl'].sum()
            print(f"    {formula:8s}: {len(f_trades):3d} trades | WR {f_wr:5.1f}% | Net {f_net:7.1f} pts")

# Aggregate
if all_trades:
    print("\n" + "="*160)
    print("AGGREGATE ANALYSIS")
    print("="*160)

    all_df = pd.DataFrame(all_trades)
    total_n = len(all_df)
    total_wr = 100.0 * all_df['win'].sum() / total_n
    total_wins = all_df[all_df['net_pnl'] > 0]['net_pnl'].sum() or 1
    total_loss = abs(all_df[all_df['net_pnl'] <= 0]['net_pnl'].sum()) or 1
    total_pf = total_wins / total_loss
    total_net = all_df['net_pnl'].sum()
    total_avg = total_net / total_n

    print(f"\nTotal: {total_n} trades | WR {total_wr:.1f}% | PF {total_pf:.2f} | Net {total_net:.1f} pts | Avg {total_avg:.1f} pts/trade")

    # By formula
    print("\nBy formula variant:")
    for formula in ['linear', 'quad', 'cubic', 'geo']:
        f_df = all_df[all_df['formula'] == formula]
        if len(f_df) > 0:
            f_wr = 100.0 * f_df['win'].sum() / len(f_df)
            f_net = f_df['net_pnl'].sum()
            f_avg = f_net / len(f_df)
            print(f"  {formula:8s}: {len(f_df):4d} trades | WR {f_wr:5.1f}% | Net {f_net:7.1f} pts | Avg {f_avg:6.1f}")

    # By session
    print("\nBy session:")
    for session in ['london', 'ny', 'asia']:
        s_df = all_df[all_df['session'] == session]
        if len(s_df) > 0:
            s_wr = 100.0 * s_df['win'].sum() / len(s_df)
            s_net = s_df['net_pnl'].sum()
            s_avg = s_net / len(s_df)
            print(f"  {session:8s}: {len(s_df):4d} trades | WR {s_wr:5.1f}% | Net {s_net:7.1f} pts | Avg {s_avg:6.1f}")

    # Export
    all_df.to_csv('/home/user/Signal/results/comprehensive_results_simplified_20261116.csv', index=False)
    print(f"\n✓ Results exported")
else:
    print("\n⚠ No trades generated")

print("\n" + "="*160)
print("PHASE 4 SIMPLIFIED — COMPLETE")
print("="*160)
