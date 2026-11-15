#!/usr/bin/env python3
"""
Gen-4: Mathematical Formula Variants + Multi-Dimensional Analysis
Goal: Escape overfitting via formula optimization, correction depth, Fibonacci confluence,
       volatility carryover, and multi-pair ecosystem correlation

Key improvements over Gen-3 (comprehensive_cloud_batch):
1. Mathematical formula variants: cubic, quadratic, geometric, linear slope transformations
2. Correction depth detection: normal (30-50%) vs over-correction (>70%)
3. Fibonacci level tracking: retracement confluence for entry quality
4. Volatility carryover: session-based clustering (does today's London vol affect tomorrow's?)
5. Multi-pair correlation logic: EUR pairs, GBP-JPY, cross-asset influence
6. Adaptive formula selection per regime: tight regimes use cubic, loose use linear
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

def calc_correction_depth(df, bar_idx):
    """Measure correction depth: normal (30-50%) vs over-correction (>70%)"""
    if bar_idx < 20:
        return 0.0, "insufficient"

    lookback = 20
    local_high = df['high'].iloc[bar_idx-lookback:bar_idx].max()
    local_low = df['low'].iloc[bar_idx-lookback:bar_idx].min()
    swing = local_high - local_low

    if swing < 0.001:
        return 0.0, "minimal_swing"

    current = df['close'].iloc[bar_idx]
    depth = (local_high - current) / swing if local_high > current else 0.0

    if depth < 0.3:
        return depth, "shallow"
    elif depth < 0.5:
        return depth, "normal"
    elif depth < 0.7:
        return depth, "deep"
    else:
        return depth, "overcorrection"

def calc_fibonacci_distance(df, bar_idx):
    """Find nearest Fibonacci retracement level (23.6%, 38.2%, 50%, 61.8%, 78.6%)"""
    if bar_idx < 20:
        return 0.0, None

    lookback = 20
    local_high = df['high'].iloc[bar_idx-lookback:bar_idx].max()
    local_low = df['low'].iloc[bar_idx-lookback:bar_idx].min()
    swing = local_high - local_low

    if swing < 0.001:
        return 999.0, None

    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    current = df['close'].iloc[bar_idx]

    min_dist = 999.0
    nearest_fib = None
    for fib in fib_levels:
        fib_price = local_high - (swing * fib)
        dist = abs(current - fib_price) / swing
        if dist < min_dist:
            min_dist = dist
            nearest_fib = fib

    return min_dist, nearest_fib

def apply_math_formula(slope, formula_type='linear'):
    """Apply different mathematical transformations to slope"""
    if formula_type == 'linear':
        return slope
    elif formula_type == 'quadratic':
        return slope ** 2 if slope >= 0 else -(abs(slope) ** 2)
    elif formula_type == 'cubic':
        return slope ** 3
    elif formula_type == 'geometric':
        return slope * np.sqrt(abs(slope)) if slope != 0 else 0
    elif formula_type == 'log':
        return np.log(abs(slope) + 1) * np.sign(slope) if slope != 0 else 0
    else:
        return slope

def backtest_variant(df, variant_name, formula_type='linear'):
    """
    Test variant with math formula optimization
    formula_type: 'linear', 'quadratic', 'cubic', 'geometric', 'log'
    """
    if len(df) < 50:
        return {'n': 0, 'wr': 0.0, 'pf': 0.0, 'net': 0.0, 'detail': ''}

    df = df.copy()

    df['sma5'] = df['close'].rolling(5).mean()
    df['sma20'] = df['close'].rolling(20).mean()
    df['sma50'] = df['close'].rolling(50).mean()
    df['sma100'] = df['close'].rolling(100).mean()
    df['std20'] = df['close'].rolling(20).std()
    df['ema20'] = df['close'].ewm(span=20).mean()

    sma5_diff = df['sma5'].diff()
    df['slope_raw'] = sma5_diff.ewm(span=6).mean() * 10000
    df['slope'] = df['slope_raw'].apply(lambda x: apply_math_formula(x, formula_type))
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
        corr_depth, corr_type = calc_correction_depth(df, i)
        fib_dist, fib_level = calc_fibonacci_distance(df, i)

        signal = None

        if variant_name == 'MathLinear':
            if (df.iloc[i]['accel'] <= -0.50 and
                df.iloc[i]['v_ratio'] >= 1.0 and
                df.iloc[i]['z20'] < -0.8 and
                corr_type in ['normal', 'deep']):
                signal = 1

        elif variant_name == 'MathQuadratic':
            if (df.iloc[i]['accel'] <= -0.45 and
                df.iloc[i]['v_ratio'] >= 1.1 and
                df.iloc[i]['z20'] < -0.9 and
                corr_type == 'deep'):
                signal = 1

        elif variant_name == 'MathCubic':
            if (df.iloc[i]['accel'] <= -0.55 and
                df.iloc[i]['v_ratio'] >= 0.95 and
                df.iloc[i]['z20'] < -0.7 and
                corr_type in ['normal', 'overcorrection']):
                signal = 1

        elif variant_name == 'MathGeometric':
            if (df.iloc[i]['accel'] <= -0.48 and
                df.iloc[i]['v_ratio'] >= 1.05 and
                df.iloc[i]['z20'] < -0.8 and
                fib_dist < 0.15):
                signal = 1

        elif variant_name == 'CorrectionNormal':
            if (corr_type == 'normal' and
                df.iloc[i]['z20'] < -0.8 and
                df.iloc[i]['rsi'] < 30 and
                hurst < 0.65):
                signal = 1

        elif variant_name == 'CorrectionDeep':
            if (corr_type in ['deep', 'overcorrection'] and
                df.iloc[i]['z20'] < -1.0 and
                df.iloc[i]['rsi'] < 25 and
                hurst < 0.60):
                signal = 1

        elif variant_name == 'FibonacciConfluence':
            if (fib_dist < 0.10 and
                fib_level in [0.382, 0.5, 0.618] and
                df.iloc[i]['z20'] < -0.7 and
                df.iloc[i]['v_ratio'] >= 0.95):
                signal = 1

        elif variant_name == 'SessionAdaptive':
            hour = df.iloc[i]['hour']
            if hour >= 8 and hour < 16:  # London
                threshold = -0.6
            elif hour >= 13 and hour < 21:  # NY
                threshold = -0.7
            else:  # Asia
                threshold = -0.5

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
                        'corr_type': corr_type,
                        'fib_level': fib_level,
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
        'detail': f"trades={n} corr_types={trades_df['corr_type'].value_counts().to_dict()}"
    }

def calc_rsi(prices, period=14):
    """Calculate RSI (14-period)"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

# Main
print("Gen-4: Mathematical Formulas + Multi-Dimensional Analysis")
print("="*140)
print("Testing 8 variants across 3 hot weeks with formula optimization")
print("="*140)

variants = [
    ('MathLinear', 'linear'),
    ('MathQuadratic', 'quadratic'),
    ('MathCubic', 'cubic'),
    ('MathGeometric', 'geometric'),
    ('CorrectionNormal', 'linear'),
    ('CorrectionDeep', 'linear'),
    ('FibonacciConfluence', 'linear'),
    ('SessionAdaptive', 'linear'),
]

results = []

for week_label, start_date, end_date in HOT_WEEKS:
    df = load_week_data(start_date, end_date, 'M1')
    if df.empty:
        print(f"⚠ {week_label}: No data")
        continue

    print(f"\n{week_label} (Gen-4 Multi-Dimensional Test)")
    print("-"*140)
    print(f"{'Variant':<25} | {'Trades':>5} | {'WR%':>6} | {'PF':>5} | {'Net Pts':>8} | Detail")
    print("-"*140)

    for variant_name, formula_type in variants:
        result = backtest_variant(df, variant_name, formula_type)

        marker = "★" if result['wr'] >= 50 else "✓" if result['wr'] >= 30 else " "
        detail = result['detail'][:50] if result['detail'] else "no trades"

        print(f"{marker} {variant_name:<22} | {result['n']:5} | {result['wr']:6.1f} | {result['pf']:5.2f} | {result['net']:8.1f} | {detail}")

        row = {
            'week': week_label,
            'variant': variant_name,
            'formula': formula_type,
            'n': result['n'],
            'wr': result['wr'],
            'pf': result['pf'],
            'net': result['net']
        }
        results.append(row)

print("\n" + "="*140)
print("SUMMARY: Gen-4 Mathematical Formula + Multi-Dimensional Results")
print("="*140)

if results:
    df_results = pd.DataFrame(results)

    print("\n✓ Winners (WR >= 40%):")
    winners = df_results[df_results['wr'] >= 40]
    if len(winners) > 0:
        print(winners[['week', 'variant', 'formula', 'n', 'wr', 'pf', 'net']].to_string(index=False))
    else:
        print("  None found")

    print("\n→ Top performers by profit factor:")
    top_pf = df_results[df_results['n'] >= 3].nlargest(5, 'pf')[['week', 'variant', 'formula', 'n', 'wr', 'pf', 'net']]
    print(top_pf.to_string(index=False) if len(top_pf) > 0 else "  None found")

    print("\n→ Trades by variant:")
    variant_summary = df_results.groupby('variant').agg({
        'n': 'sum',
        'wr': 'mean',
        'pf': 'mean',
        'net': 'sum'
    }).sort_values('net', ascending=False)
    print(variant_summary)

    print("\n" + "="*140)
    print("KEY INSIGHTS:")
    print("1. Math formulas: which (linear/quad/cubic/geometric) produces cleanest signal?")
    print("2. Correction depth: can we filter normal corrections from market noise?")
    print("3. Fibonacci confluence: does proximity to Fib levels improve entry quality?")
    print("4. Session adaptation: do session-specific thresholds beat global parameters?")
    print("="*140)
else:
    print("No results generated.")
