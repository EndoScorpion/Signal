#!/usr/bin/env python3
"""
Debug version: Identify why comprehensive batch generates no trades
Tests entry gates step-by-step with logging
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

def backtest_debug(df):
    """Test entry logic with detailed logging"""
    if len(df) < 50:
        return

    # Calculate basic indicators
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

    # Test gates
    gate_z20_low = 0
    gate_accel_low = 0
    gate_hurst = 0
    gate_rsi = 0
    entries = 0

    for i in range(40, len(df) - 12):
        hour = df.iloc[i]['hour']
        z20 = df.iloc[i]['z20']
        accel = df.iloc[i]['accel']
        hurst = calc_hurst_quick(df['close'].iloc[i-29:i+1].values)
        rsi = df.iloc[i]['rsi']

        if hour >= 8 and hour < 16:
            threshold = -0.6
            sess = 'London'
        elif hour >= 13 and hour < 21:
            threshold = -0.7
            sess = 'NY'
        else:
            threshold = -0.5
            sess = 'Asia'

        # Gate 1: z20 threshold
        if z20 < threshold:
            gate_z20_low += 1

            # Gate 2: accel threshold
            if accel <= -0.50:
                gate_accel_low += 1

                # Gate 3: Hurst
                if hurst < 0.7:
                    gate_hurst += 1

                    # Gate 4: RSI oversold
                    if rsi < 30:
                        gate_rsi += 1
                        entries += 1
                        if entries <= 5:
                            print(f"  Entry {entries}: i={i}, z20={z20:.3f}, accel={accel:.3f}, hurst={hurst:.3f}, rsi={rsi:.1f}, {sess}")

    print(f"  Gate z20<thresh: {gate_z20_low} | accel<-0.5: {gate_accel_low} | hurst<0.7: {gate_hurst} | rsi<30: {gate_rsi} | ENTRIES: {entries}")
    return entries

# Main
print("DEBUG: Entry Gate Analysis")
print("="*120)

total_entries = 0

for week_label, start_date, end_date in HOT_WEEKS:
    print(f"\n{week_label}:")
    df = load_week_data(start_date, end_date, 'M1')
    if df.empty:
        print(f"  No data")
        continue
    print(f"  Data: {len(df)} bars")
    entries = backtest_debug(df)
    if entries:
        total_entries += entries

print(f"\n{'='*120}")
print(f"Total entries across all weeks: {total_entries}")
