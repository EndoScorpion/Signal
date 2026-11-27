#!/usr/bin/env python3
"""
Dukascopy tick data storage engine with Parquet + DuckDB.
Serverless, file-based time-series storage optimized for backtesting.

Storage schema:
- Partitioned by Year/Month/Day: data/dukascopy/{year}/{month:02d}/{day:02d}/
- Each hour file: {symbol}_{hour:02d}.parquet
- Columns: timestamp, symbol, bid_price, ask_price, bid_volume, ask_volume (all numeric)

Query via DuckDB for instant M1/M5/M30 OHLCV aggregation.
"""

import struct
import lzma
import urllib.request
import pandas as pd
import datetime
import sys
import os
from pathlib import Path
from typing import Optional

try:
    import pyarrow.parquet as pq
    import pyarrow as pa
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    print("Warning: pyarrow not installed. Install with: pip install pyarrow")

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    print("Warning: duckdb not installed. Install with: pip install duckdb")


def download_and_parse_dukascopy_parquet(
    year, month, day, hour,
    symbol="EURUSD",
    storage_dir="./data/dukascopy"
):
    """
    Download Dukascopy tick data and save directly to Parquet.

    Args:
        year, month, day, hour: UTC date/time
        symbol: Currency pair (e.g., "EURUSD")
        storage_dir: Root directory for partitioned Parquet storage

    Returns:
        Parquet file path if successful, None otherwise
    """

    if not PARQUET_AVAILABLE:
        print("✗ pyarrow not available. Install: pip install pyarrow")
        return None

    # Adjust for 0-indexed month system
    zero_indexed_month = f"{month - 1:02d}"
    day_str = f"{day:02d}"
    hour_str = f"{hour:02d}"

    url = f"https://datafeed.dukascopy.com/datafeed/{symbol}/{year}/{zero_indexed_month}/{day_str}/{hour_str}h_ticks.bi5"
    print(f"Fetching: {url}")

    try:
        # Download and decompress
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            compressed_data = response.read()

        raw_bytes = lzma.decompress(compressed_data)

        # Parse 20-byte tick records
        tick_size = 20
        ticks_count = len(raw_bytes) // tick_size

        base_time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
        parsed_ticks = []

        for i in range(ticks_count):
            start = i * tick_size
            end = start + tick_size
            chunk = raw_bytes[start:end]

            ms_offset, ask_raw, bid_raw, ask_vol, bid_vol = struct.unpack(">3I2f", chunk)

            tick_time = base_time + datetime.timedelta(milliseconds=ms_offset)
            ask_price = ask_raw / 100000.0
            bid_price = bid_raw / 100000.0

            parsed_ticks.append({
                'timestamp': tick_time.isoformat(),
                'symbol': symbol,
                'bid_price': bid_price,
                'ask_price': ask_price,
                'bid_volume': bid_vol,
                'ask_volume': ask_vol,
            })

        print(f"✓ Parsed {ticks_count} ticks")

        # Create partitioned directory structure
        partition_dir = os.path.join(storage_dir, str(year), f"{month:02d}", f"{day:02d}")
        Path(partition_dir).mkdir(parents=True, exist_ok=True)

        # Convert to Parquet
        df = pd.DataFrame(parsed_ticks)

        # Cast to efficient dtypes
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df['bid_price'] = df['bid_price'].astype('float32')
        df['ask_price'] = df['ask_price'].astype('float32')
        df['bid_volume'] = df['bid_volume'].astype('float32')
        df['ask_volume'] = df['ask_volume'].astype('float32')

        # Convert to PyArrow table
        table = pa.Table.from_pandas(df)

        # Save to Parquet with compression
        parquet_path = os.path.join(partition_dir, f"{symbol}_{hour_str}.parquet")
        pq.write_table(table, parquet_path, compression='snappy')

        print(f"✓ Saved to {parquet_path}")
        return parquet_path

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"✗ No data found for {hour_str}:00 (market closed / weekend)")
        else:
            print(f"✗ HTTP Error: {e.code}")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def duckdb_resample_ohlcv(
    storage_dir="./data/dukascopy",
    symbol="EURUSD",
    year=2026,
    month=6,
    day=15,
    timeframe="M5"
):
    """
    Query Parquet files via DuckDB and resample to OHLCV candles.

    Args:
        storage_dir: Root Parquet storage directory
        symbol: Currency pair
        year, month, day: Date to query
        timeframe: 'M1', 'M5', 'M30', 'H1'

    Returns:
        pandas DataFrame with OHLCV data
    """

    if not DUCKDB_AVAILABLE:
        print("✗ duckdb not available. Install: pip install duckdb")
        return None

    # Map timeframe to SQL interval
    tf_map = {
        'M1': "INTERVAL '1 minute'",
        'M5': "INTERVAL '5 minutes'",
        'M30': "INTERVAL '30 minutes'",
        'H1': "INTERVAL '1 hour'",
    }

    if timeframe not in tf_map:
        print(f"✗ Unknown timeframe: {timeframe}")
        return None

    interval = tf_map[timeframe]

    # Construct Parquet glob pattern for the day
    partition_path = os.path.join(storage_dir, str(year), f"{month:02d}", f"{day:02d}")
    parquet_pattern = os.path.join(partition_path, f"{symbol}_*.parquet")

    print(f"Querying Parquet files: {parquet_pattern}")
    print(f"Timeframe: {timeframe} ({interval})")

    try:
        # DuckDB SQL query
        con = duckdb.connect(':memory:')

        query = f"""
        WITH ticks AS (
            SELECT * FROM read_parquet('{parquet_pattern}')
        )
        SELECT
            date_trunc('{timeframe}', timestamp) AS timestamp,
            symbol,
            FIRST(bid_price ORDER BY timestamp) AS bid_open,
            MAX(bid_price) AS bid_high,
            MIN(bid_price) AS bid_low,
            LAST(bid_price ORDER BY timestamp) AS bid_close,
            FIRST(ask_price ORDER BY timestamp) AS ask_open,
            MAX(ask_price) AS ask_high,
            MIN(ask_price) AS ask_low,
            LAST(ask_price ORDER BY timestamp) AS ask_close,
            SUM(bid_volume) AS bid_volume_total,
            SUM(ask_volume) AS ask_volume_total,
            COUNT(*) AS tick_count
        FROM ticks
        GROUP BY date_trunc('{timeframe}', timestamp), symbol
        ORDER BY timestamp ASC
        """

        result = con.execute(query).fetch_all()
        columns = [desc[0] for desc in con.description]

        df = pd.DataFrame(result, columns=columns)

        # Use mid-price for OHLCV
        df['Open'] = (df['bid_open'] + df['ask_open']) / 2.0
        df['High'] = (df['bid_high'] + df['ask_high']) / 2.0
        df['Low'] = (df['bid_low'] + df['ask_low']) / 2.0
        df['Close'] = (df['bid_close'] + df['ask_close']) / 2.0
        df['Volume'] = df['bid_volume_total'] + df['ask_volume_total']

        # Final output columns
        df_out = df[['timestamp', 'symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'tick_count']]
        df_out['Timestamp'] = df_out['timestamp'].astype(str)

        return df_out[['Timestamp', 'symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'tick_count']]

    except Exception as e:
        print(f"✗ DuckDB query failed: {e}")
        return None


def batch_download_day(year, month, day, storage_dir="./data/dukascopy"):
    """
    Download all 24 hours for a given day.
    """
    print(f"\n{'='*60}")
    print(f"Batch downloading {year}-{month:02d}-{day:02d}")
    print(f"{'='*60}\n")

    success = 0
    for hour in range(24):
        result = download_and_parse_dukascopy_parquet(year, month, day, hour, storage_dir=storage_dir)
        if result:
            success += 1

    print(f"\n✓ Downloaded {success}/24 hours")
    return success


if __name__ == "__main__":

    if len(sys.argv) > 1:
        # Command line: python3 dukascopy_parquet_storage.py download 2026 6 15 14
        # or: python3 dukascopy_parquet_storage.py query 2026 6 15 M5

        cmd = sys.argv[1]

        if cmd == "download":
            year, month, day = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
            hour = int(sys.argv[5]) if len(sys.argv) > 5 else None

            if hour is not None:
                download_and_parse_dukascopy_parquet(year, month, day, hour)
            else:
                batch_download_day(year, month, day)

        elif cmd == "query":
            year, month, day = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
            timeframe = sys.argv[5] if len(sys.argv) > 5 else "M5"

            df = duckdb_resample_ohlcv(year=year, month=month, day=day, timeframe=timeframe)
            if df is not None:
                print(f"\n{timeframe} Candles ({len(df)} bars):")
                print(df)

    else:
        # Demo: Download June 15, 2026 14:00 UTC
        print("=" * 60)
        print("Demo: Dukascopy Parquet Storage")
        print("=" * 60)

        if PARQUET_AVAILABLE:
            print("\n1. Downloading sample hour (2026-06-15 14:00 UTC)...")
            parquet_file = download_and_parse_dukascopy_parquet(2026, 6, 15, 14)

            if parquet_file and DUCKDB_AVAILABLE:
                print("\n2. Querying M5 candles via DuckDB...")
                df_ohlcv = duckdb_resample_ohlcv(year=2026, month=6, day=15, timeframe="M5")
                if df_ohlcv is not None:
                    print(f"\nGenerated {len(df_ohlcv)} M5 candles:")
                    print(df_ohlcv.head(10))
        else:
            print("✗ Install pyarrow: pip install pyarrow duckdb")
