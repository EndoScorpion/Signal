#!/usr/bin/env python3
"""
Dukascopy EURUSD tick data downloader.
Downloads hourly .bi5 files, decompresses LZMA, parses 20-byte tick records.
Outputs CSV: Timestamp,Ask,Bid,Ask_Volume,Bid_Volume (UTC).
"""

import struct
import lzma
import urllib.request
import pandas as pd
import datetime
import sys
import os
from pathlib import Path

def download_and_parse_dukascopy(year, month, day, hour, symbol="EURUSD", output_dir=None):
    """
    Download and parse a single hour of Dukascopy tick data.

    Args:
        year, month, day, hour: Date/time in UTC
        symbol: Currency pair (default "EURUSD")
        output_dir: Where to save CSV (default: ./dukascopy_ticks/)

    Returns:
        pandas.DataFrame with columns [Timestamp, Ask, Bid, Ask_Volume, Bid_Volume]
        or None if download fails.
    """

    # Adjust for 0-indexed month system (January=00, December=11)
    zero_indexed_month = f"{month - 1:02d}"
    day_str = f"{day:02d}"
    hour_str = f"{hour:02d}"

    url = f"https://datafeed.dukascopy.com/datafeed/{symbol}/{year}/{zero_indexed_month}/{day_str}/{hour_str}h_ticks.bi5"
    print(f"Fetching: {url}")

    try:
        # 1. Stream the compressed file from the server
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            compressed_data = response.read()

        # 2. Decompress LZMA binary layer
        raw_bytes = lzma.decompress(compressed_data)

        # 3. Step through file chunks (20 bytes per tick)
        tick_size = 20
        ticks_count = len(raw_bytes) // tick_size

        base_time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
        parsed_ticks = []

        for i in range(ticks_count):
            start = i * tick_size
            end = start + tick_size
            chunk = raw_bytes[start:end]

            # Unpack format: > (Big Endian), 3I (Three u32 integers), 2f (Two floats)
            ms_offset, ask_raw, bid_raw, ask_vol, bid_vol = struct.unpack(">3I2f", chunk)

            # Reconstruct absolute timestamp
            tick_time = base_time + datetime.timedelta(milliseconds=ms_offset)

            # Format raw integers into real FX decimal quotes
            ask_price = ask_raw / 100000.0
            bid_price = bid_raw / 100000.0

            parsed_ticks.append([tick_time.isoformat(), ask_price, bid_price, ask_vol, bid_vol])

        # Convert list matrix into structured DataFrame
        df = pd.DataFrame(parsed_ticks, columns=['Timestamp', 'Ask', 'Bid', 'Ask_Volume', 'Bid_Volume'])

        print(f"✓ Parsed {ticks_count} ticks")

        # Save to CSV if output_dir specified
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            csv_filename = f"{symbol}_{year}{month:02d}{day:02d}_{hour:02d}00_ticks.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            df.to_csv(csv_path, index=False)
            print(f"✓ Saved to {csv_path}")

        return df

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"✗ No data found for {hour_str}:00 (market likely closed / weekend)")
        else:
            print(f"✗ HTTP Error: {e.code}")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def download_day_range(year, month, day, output_dir=None, symbol="EURUSD"):
    """
    Download all 24 hours of tick data for a given day.
    Returns combined DataFrame.
    """
    all_dfs = []
    for hour in range(24):
        df = download_and_parse_dukascopy(year, month, day, hour, symbol, output_dir)
        if df is not None:
            all_dfs.append(df)

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        print(f"\n✓ Day total: {len(combined)} ticks")
        return combined
    return None


if __name__ == "__main__":
    # Example: Download June 15, 2026 at 14:00 UTC
    output_dir = "./dukascopy_ticks"

    if len(sys.argv) > 1:
        # Command line: python3 dukascopy_downloader.py 2026 6 15 14
        year, month, day, hour = map(int, sys.argv[1:5])
        df = download_and_parse_dukascopy(year, month, day, hour, output_dir=output_dir)
    else:
        # Test: June 15, 2026 14:00 UTC
        print("=" * 60)
        print("Testing Dukascopy Downloader (June 15, 2026 14:00 UTC)")
        print("=" * 60)
        df = download_and_parse_dukascopy(2026, 6, 15, 14, output_dir=output_dir)

    if df is not None:
        print("\nFirst 5 rows:")
        print(df.head())
        print(f"\nShape: {df.shape}")
        print(f"Ask range: {df['Ask'].min():.5f} - {df['Ask'].max():.5f}")
        print(f"Bid range: {df['Bid'].min():.5f} - {df['Bid'].max():.5f}")
