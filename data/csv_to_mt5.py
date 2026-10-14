"""
csv_to_mt5.py  -  Push EURUSD M1 history into MT5 custom symbol via Python MT5 API.
Replaces csv_to_hst.py for the MT5 pipeline.

Requires: pip install MetaTrader5
MT5 must be installed and logged in at least once before running.

MMR (c) Nasif Hossain 2019. Commission: 6 pts FXOpen ECN (confirmed 2026-10-13).

Run: python -I data/csv_to_mt5.py
"""

import os, sys, struct, datetime, zipfile, csv
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────────
ZIP_DIR      = r"C:\Users\endos\Signal\data\quotes_download"   # FXOpen QuotesDownloader output
CUSTOM_SYM   = "EURUSD_Custom"
DIGITS       = 5
SPREAD_PTS   = 6          # FXOpen ECN max commission, confirmed 2026-10-13

# MT5 bar struct fields required by CustomRatesReplace
# datetime (int64 UTC seconds), open, high, low, close, tick_volume, spread, real_volume
MT5_DTYPE = np.dtype([
    ('time',        np.int64),
    ('open',        np.float64),
    ('high',        np.float64),
    ('low',         np.float64),
    ('close',       np.float64),
    ('tick_volume', np.int64),
    ('spread',      np.int32),
    ('real_volume', np.int64),
])

# ── parse FXOpen QuotesDownloader M1 csv zips ──────────────────────────────────

def parse_csv_in_zip(zp):
    bars = {}
    with zipfile.ZipFile(zp) as z:
        for name in z.namelist():
            if not name.endswith('.csv'): continue
            with z.open(name) as f:
                for line in f:
                    try:
                        row = line.decode('utf-8', errors='ignore').strip().split(',')
                        if len(row) < 6: continue
                        dt = datetime.datetime.strptime(row[0].strip() + ' ' + row[1].strip(),
                                                        '%Y.%m.%d %H:%M')
                        ts = int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())
                        o, h, l, c = float(row[2]), float(row[3]), float(row[4]), float(row[5])
                        vol = int(float(row[6])) if len(row) > 6 else 1
                        bars[ts] = (ts, o, h, l, c, vol)
                    except Exception:
                        pass
    return bars

def load_all_zips():
    zips = sorted([os.path.join(ZIP_DIR, f)
                   for f in os.listdir(ZIP_DIR) if f.endswith('.zip')])
    bars = {}
    for zp in zips:
        print(f"  {os.path.basename(zp)}")
        try:
            b = parse_csv_in_zip(zp)
            bars.update(b)
            print(f"    {len(b):,} bars")
        except Exception as e:
            print(f"    SKIP ({e})")
    return bars

# ── MT5 custom symbol setup ────────────────────────────────────────────────────

def setup_custom_symbol(mt5):
    """Create or update EURUSD_Custom with FXOpen ECN 5-digit properties."""
    symbols = [s.name for s in mt5.symbols_get()]
    if CUSTOM_SYM not in symbols:
        print(f"  Creating custom symbol: {CUSTOM_SYM}")
        # CustomSymbolCreate: name, path (group), source_symbol
        if not mt5.symbol_select(CUSTOM_SYM, True):
            # Create from template of real EURUSD
            result = mt5.custom_symbol_create(CUSTOM_SYM, "Forex\\Custom", "EURUSD")
            if result != 0:
                print(f"  ERROR creating symbol: {result}")
                return False
    else:
        print(f"  Symbol {CUSTOM_SYM} already exists")

    # Set key properties
    props = [
        (mt5.SYMBOL_DIGITS,           DIGITS),
        (mt5.SYMBOL_SPREAD_FLOAT,     1),          # floating spread
        (mt5.SYMBOL_SPREAD,           SPREAD_PTS), # starting spread in points
        (mt5.SYMBOL_TRADE_CONTRACT_SIZE, 100000),
        (mt5.SYMBOL_VOLUME_MIN,       0.01),
        (mt5.SYMBOL_VOLUME_MAX,       500.0),
        (mt5.SYMBOL_VOLUME_STEP,      0.01),
    ]
    for prop_id, val in props:
        mt5.custom_symbol_set_integer(CUSTOM_SYM, prop_id, val)

    mt5.symbol_select(CUSTOM_SYM, True)
    print(f"  {CUSTOM_SYM} configured: digits={DIGITS}, spread={SPREAD_PTS}pts")
    return True

# ── push bars to MT5 ───────────────────────────────────────────────────────────

def push_rates(mt5, bars_dict):
    """Push M1 bars via CustomRatesReplace in chronological chunks."""
    sorted_bars = sorted(bars_dict.values(), key=lambda x: x[0])
    print(f"\n  Pushing {len(sorted_bars):,} M1 bars to {CUSTOM_SYM}...")

    CHUNK = 100_000
    total_pushed = 0
    for start in range(0, len(sorted_bars), CHUNK):
        chunk = sorted_bars[start:start + CHUNK]
        arr = np.array(
            [(b[0], b[1], b[2], b[3], b[4], b[5], SPREAD_PTS, 0) for b in chunk],
            dtype=MT5_DTYPE
        )
        res = mt5.custom_rates_replace(CUSTOM_SYM, arr)
        if res < 0:
            print(f"  ERROR at chunk {start}: {mt5.last_error()}")
        else:
            total_pushed += len(chunk)
        if start % (CHUNK * 5) == 0:
            pct = start / len(sorted_bars) * 100
            print(f"  {total_pushed:,} / {len(sorted_bars):,} ({pct:.0f}%)", flush=True)

    print(f"\n  Done: {total_pushed:,} bars pushed to {CUSTOM_SYM}")
    return total_pushed

# ── main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== csv_to_mt5.py ===\n")

    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("ERROR: MetaTrader5 package not installed.")
        print("  Run: pip install MetaTrader5")
        print("  Then install MT5 from FXOpen and log in once manually.")
        sys.exit(1)

    # Init MT5
    if not mt5.initialize():
        print(f"ERROR: MT5 init failed: {mt5.last_error()}")
        print("  Make sure MT5 is installed and has been opened at least once.")
        sys.exit(1)
    print(f"  MT5 {mt5.version()} initialized\n")

    # Load CSV data
    print("Loading M1 bars from zip files...")
    bars = load_all_zips()
    if not bars:
        print("No bars loaded. Check ZIP_DIR path.")
        mt5.shutdown()
        sys.exit(1)

    ts_sorted = sorted(bars.keys())
    print(f"\n  Total unique M1 bars: {len(bars):,}")
    print(f"  Range: {datetime.datetime.utcfromtimestamp(ts_sorted[0]).date()} -> "
          f"{datetime.datetime.utcfromtimestamp(ts_sorted[-1]).date()}\n")

    # Setup custom symbol
    print("Setting up custom symbol...")
    if not setup_custom_symbol(mt5):
        mt5.shutdown()
        sys.exit(1)

    # Push rates
    pushed = push_rates(mt5, bars)

    mt5.shutdown()
    print(f"\nAll done. {pushed:,} M1 bars in {CUSTOM_SYM}.")
    print("MT5 will auto-build M5/M15/H1/H4/D1 from this data.")
    print(f"Next: run run_tester_mt5.ps1 with your MQL5 EA.\n")

if __name__ == '__main__':
    main()
