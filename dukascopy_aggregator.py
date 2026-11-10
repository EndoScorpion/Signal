#!/usr/bin/env python3
"""
Dukascopy tick aggregator.
Converts raw tick CSVs to OHLCV bars (M1, M5, M30) in UTC.
Compatible with existing FXOpen CSV format: Timestamp,Open,High,Low,Close,Volume
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

def aggregate_ticks_to_ohlcv(tick_csv_path, timeframes=['M1', 'M5', 'M30'], output_dir=None):
    """
    Aggregate tick data to OHLCV bars.

    Args:
        tick_csv_path: Path to tick CSV (columns: Timestamp, Ask, Bid, Ask_Volume, Bid_Volume)
        timeframes: List of timeframes to generate ('M1', 'M5', 'M30')
        output_dir: Where to save output CSVs

    Returns:
        Dict mapping timeframe -> DataFrame
    """

    print(f"Reading tick data: {tick_csv_path}")
    df_ticks = pd.read_csv(tick_csv_path)

    # Convert Timestamp to datetime
    df_ticks['Timestamp'] = pd.to_datetime(df_ticks['Timestamp'], utc=True)

    # Use mid-price (average of bid/ask) as close price
    # (more representative than bid or ask alone)
    df_ticks['Mid'] = (df_ticks['Ask'] + df_ticks['Bid']) / 2.0
    df_ticks['Volume'] = df_ticks['Ask_Volume'] + df_ticks['Bid_Volume']

    print(f"✓ Loaded {len(df_ticks)} ticks, {df_ticks['Timestamp'].min()} to {df_ticks['Timestamp'].max()}")

    # Set index for resampling
    df_ticks.set_index('Timestamp', inplace=True)

    results = {}

    for tf in timeframes:
        print(f"\nAggregating to {tf}...")

        # Resample parameters
        if tf == 'M1':
            freq = '1min'
        elif tf == 'M5':
            freq = '5min'
        elif tf == 'M30':
            freq = '30min'
        else:
            print(f"✗ Unknown timeframe: {tf}")
            continue

        # OHLCV aggregation
        ohlcv = df_ticks['Mid'].resample(freq).agg([
            ('Open', 'first'),
            ('High', 'max'),
            ('Low', 'min'),
            ('Close', 'last'),
        ])

        # Volume aggregation
        volume = df_ticks['Volume'].resample(freq).sum()
        ohlcv['Volume'] = volume

        # Drop NaN bars (no ticks in that period)
        ohlcv = ohlcv.dropna()

        # Convert index back to column (Timestamp)
        ohlcv.reset_index(inplace=True)
        ohlcv['Timestamp'] = ohlcv['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Reorder columns to match FXOpen format
        ohlcv = ohlcv[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]

        print(f"✓ Generated {len(ohlcv)} bars")
        print(f"  Range: {ohlcv['Timestamp'].iloc[0]} to {ohlcv['Timestamp'].iloc[-1]}")
        print(f"  OHLC sample: O={ohlcv['Open'].iloc[0]:.5f}, H={ohlcv['High'].iloc[0]:.5f}, L={ohlcv['Low'].iloc[0]:.5f}, C={ohlcv['Close'].iloc[0]:.5f}")

        # Save to CSV
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Extract symbol and date from source filename
            base_name = Path(tick_csv_path).stem  # e.g., "EURUSD_20260615_1400_ticks"
            parts = base_name.split('_')
            if len(parts) >= 3:
                symbol = parts[0]
                date_str = parts[1]
                hour_str = parts[2]
            else:
                symbol = 'EURUSD'
                date_str = datetime.now().strftime('%Y%m%d')
                hour_str = '0000'

            csv_filename = f"{symbol}_{date_str}_{tf}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            ohlcv.to_csv(csv_path, index=False)
            print(f"✓ Saved to {csv_path}")

        results[tf] = ohlcv

    return results


def batch_aggregate_day(year, month, day, tick_dir="./dukascopy_ticks", output_dir=None):
    """
    Aggregate all tick files from a day.
    """
    tick_files = sorted(Path(tick_dir).glob(f"EURUSD_{year}{month:02d}{day:02d}_*_ticks.csv"))

    if not tick_files:
        print(f"✗ No tick files found for {year}-{month:02d}-{day:02d}")
        return

    print(f"\n{'='*60}")
    print(f"Batch aggregating {len(tick_files)} tick files")
    print(f"{'='*60}\n")

    all_results = {tf: [] for tf in ['M1', 'M5', 'M30']}

    for tick_file in tick_files:
        print(f"Processing: {tick_file.name}")
        results = aggregate_ticks_to_ohlcv(str(tick_file), output_dir=output_dir)

        for tf, df in results.items():
            all_results[tf].append(df)

    # Concatenate all bars for each timeframe
    print(f"\n{'='*60}")
    print("Daily summaries:")
    print(f"{'='*60}\n")

    for tf in ['M1', 'M5', 'M30']:
        if all_results[tf]:
            combined = pd.concat(all_results[tf], ignore_index=True)
            print(f"{tf}: {len(combined)} total bars")

            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                csv_filename = f"EURUSD_{year}{month:02d}{day:02d}_{tf}_daily.csv"
                csv_path = os.path.join(output_dir, csv_filename)
                combined.to_csv(csv_path, index=False)
                print(f"  Saved daily to {csv_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tick_csv = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./dukascopy_ohlcv"
        tfs = sys.argv[3].split(',') if len(sys.argv) > 3 else ['M1', 'M5', 'M30']
        aggregate_ticks_to_ohlcv(tick_csv, timeframes=tfs, output_dir=output_dir)
    else:
        # Demonstrate on a sample tick file (if it exists)
        sample_tick = "./dukascopy_ticks/EURUSD_20260615_1400_ticks.csv"
        if os.path.exists(sample_tick):
            print(f"Testing on {sample_tick}\n")
            aggregate_ticks_to_ohlcv(sample_tick, output_dir="./dukascopy_ohlcv")
        else:
            print(f"No sample tick file found at {sample_tick}")
            print("Run dukascopy_downloader.py first, then run aggregator on its output.")
