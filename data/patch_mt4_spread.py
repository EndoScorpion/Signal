"""
patch_mt4_spread.py  -  Force fixed offline spread in MT4 symbols.raw
Run ONLY while MT4_Backtest terminal is fully closed.

FXOpen ECN EURUSD max commission confirmed = 6 pts (Nasif Hossain, 2026-10-13).

Run: python -I data/patch_mt4_spread.py
"""

import struct, os, shutil, datetime

SYMBOLS_RAW  = r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\symbols.raw"
TARGET_SYM   = "EURUSD"
NEW_SPREAD   = 6      # pts — FXOpen ECN max commission
RECORD_SIZE  = 1936
SPREAD_OFF   = 284

def patch_spread(path, symbol, spread_pts):
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        return False

    # backup
    bak = path + f".bak_{datetime.date.today()}"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print(f"  Backup -> {bak}")

    with open(path, 'r+b') as f:
        data = f.read()
        n = len(data) // RECORD_SIZE
        for i in range(n):
            off = i * RECORD_SIZE
            name = data[off:off+12].split(b'\x00')[0].decode('ascii', errors='ignore')
            if name == symbol:
                current = struct.unpack_from('<i', data, off + SPREAD_OFF)[0]
                print(f"  Found {symbol} at entry {i}")
                print(f"  Current spread: {current} pts")
                f.seek(off + SPREAD_OFF)
                f.write(struct.pack('<i', spread_pts))
                print(f"  Patched to: {spread_pts} pts")
                return True
        print(f"  ERROR: {symbol} not found in {n} entries")
        return False

def verify(path, symbol):
    with open(path, 'rb') as f:
        data = f.read()
    n = len(data) // RECORD_SIZE
    for i in range(n):
        off = i * RECORD_SIZE
        name = data[off:off+12].split(b'\x00')[0].decode('ascii', errors='ignore')
        if name == symbol:
            val = struct.unpack_from('<i', data, off + SPREAD_OFF)[0]
            print(f"  Verify {symbol} spread: {val} pts {'OK' if val == NEW_SPREAD else 'MISMATCH'}")
            return val
    return None

if __name__ == '__main__':
    print("=== patch_mt4_spread.py ===")
    print("WARNING: MT4_Backtest must be fully closed before running this.\n")
    ok = patch_spread(SYMBOLS_RAW, TARGET_SYM, NEW_SPREAD)
    if ok:
        verify(SYMBOLS_RAW, TARGET_SYM)
        print("\nDone. Now re-run the tester.")
    else:
        print("\nFailed.")
