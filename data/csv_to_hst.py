"""
MT4 HST v401 merger + timeframe builder
Merges FXOpen QuotesDownloader csv_zip files into EURUSD .hst files
in both MT4 installs, rebuilds M5/M15/M30/H1/H4/D1 from merged M1.

Bar format v401 (60 bytes):
  time(int64) + open(double) + high(double) + low(double) + close(double)
  + tick_volume(int64) + spread(int32) + real_volume(int64)

Run: python csv_to_hst.py
     (MT4 must be fully closed first)
"""

import struct, os, shutil, zipfile, datetime, sys

HIST_DIRS = [
    r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server",
    r"C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\history\FXOpenEU-ECN Live Server",
    r"C:\Users\endos\Desktop\mt4_tester\history\FXOpenEU-ECN Live Server",
]
CSV_ZIP_DIR = r"C:\Users\endos\Signal\data\quotes_download"
SYMBOL = "EURUSD"
DIGITS = 5

BAR_FMT = '<qddddqiq'
BAR_SIZE = struct.calcsize(BAR_FMT)
assert BAR_SIZE == 60
HDR_SIZE = 148


def read_hst(path):
    with open(path, 'rb') as f:
        hdr = f.read(HDR_SIZE)
        data = f.read()
    bars = {}
    n = len(data) // BAR_SIZE
    for i in range(n):
        t, o, h, l, c, tv, sp, rv = struct.unpack_from(BAR_FMT, data, i * BAR_SIZE)
        bars[t] = (o, h, l, c, tv, sp, rv)
    print(f"  Read {n:,} bars from {os.path.basename(path)}")
    return hdr, bars


def make_header(symbol, period, digits=5):
    hdr = bytearray(HDR_SIZE)
    struct.pack_into('<i', hdr, 0, 401)
    struct.pack_into('64s', hdr, 4, b'(C)opyright 2000-2014, MetaQuotes Software Corp.')
    struct.pack_into('12s', hdr, 68, symbol.encode('ascii'))
    struct.pack_into('<i', hdr, 80, period)
    struct.pack_into('<i', hdr, 84, digits)
    return bytes(hdr)


def write_hst(path, bars_dict, period, header=None):
    sorted_times = sorted(bars_dict.keys())
    if header is None:
        header = make_header(SYMBOL, period, DIGITS)
    with open(path, 'wb') as f:
        f.write(header)
        for t in sorted_times:
            o, h, l, c, tv, sp, rv = bars_dict[t]
            f.write(struct.pack(BAR_FMT, t, o, h, l, c, tv, sp, rv))
    print(f"  Wrote {len(sorted_times):,} bars -> {os.path.basename(path)}")


def parse_csv_in_zip(zip_path):
    bars = {}
    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_name = next(n for n in zf.namelist() if 'bid' in n.lower())
        import io
        with zf.open(csv_name) as f:
            reader = io.TextIOWrapper(f, encoding='utf-8')
            for line in reader:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) < 6:
                    continue
                try:
                    dt = datetime.datetime.strptime(parts[0], '%Y.%m.%d %H:%M:%S')
                    o, h, l, c, v = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), int(parts[5])
                    ts = int(dt.timestamp())
                    bars[ts] = (o, h, l, c, v)
                except (ValueError, IndexError):
                    continue
    return bars


def build_higher_tf(m1_bars, period_minutes):
    secs = period_minutes * 60
    tf_bars = {}
    for ts in sorted(m1_bars.keys()):
        o, h, l, c, tv, sp, rv = m1_bars[ts]
        tf_ts = (ts // secs) * secs
        if tf_ts not in tf_bars:
            tf_bars[tf_ts] = [o, h, l, c, tv, sp, rv]
        else:
            b = tf_bars[tf_ts]
            b[1] = max(b[1], h)
            b[2] = min(b[2], l)
            b[3] = c
            b[4] += tv
    return {t: tuple(v) for t, v in tf_bars.items()}


def main():
    print("=== MT4 HST Merger + Timeframe Builder ===\n")

    # 1. Read M1 from largest available source
    print("[1] Reading existing EURUSD1.hst (picking largest)...")
    best_hdr, existing_bars = None, {}
    for hist_dir in HIST_DIRS:
        p = os.path.join(hist_dir, "EURUSD1.hst")
        if os.path.exists(p):
            hdr, bars = read_hst(p)
            if len(bars) > len(existing_bars):
                existing_bars, best_hdr = bars, hdr
                print(f"  -> using {p}")
    if not existing_bars:
        print("ERROR: no EURUSD1.hst found"); return
    times = sorted(existing_bars.keys())
    print(f"  Range: {datetime.datetime.utcfromtimestamp(times[0]).date()} -> {datetime.datetime.utcfromtimestamp(times[-1]).date()}")

    # 2. Parse all CSV zips
    print("\n[2] Parsing downloaded CSV zips...")
    new_bars = {}
    zips = []
    for root, dirs, files in os.walk(CSV_ZIP_DIR):
        for f in files:
            if f.endswith('.zip') and 'EURUSD_M1' in f:
                zips.append(os.path.join(root, f))
    for zp in sorted(zips):
        print(f"  {os.path.basename(zp)}")
        try:
            b = parse_csv_in_zip(zp)
            print(f"    {len(b):,} bars")
            new_bars.update(b)
        except Exception as e:
            print(f"    SKIP ({e})")
    print(f"  Total CSV bars: {len(new_bars):,}")

    # 3. Merge gaps
    print("\n[3] Merging...")
    added = 0
    for ts, (o, h, l, c, v) in new_bars.items():
        if ts not in existing_bars:
            existing_bars[ts] = (o, h, l, c, v, 0, 0)
            added += 1
    print(f"  Added {added:,} new | already present {len(new_bars)-added:,} | total M1 {len(existing_bars):,}")

    # 4. Build all timeframes
    print("\n[4] Building higher timeframes...")
    tf_map = {1: "EURUSD1.hst", 5: "EURUSD5.hst", 15: "EURUSD15.hst",
              30: "EURUSD30.hst", 60: "EURUSD60.hst", 240: "EURUSD240.hst",
              1440: "EURUSD1440.hst"}
    tf_data = {1: existing_bars}
    for period in [5, 15, 30, 60, 240, 1440]:
        tf_data[period] = build_higher_tf(existing_bars, period)
        print(f"  M{period if period < 60 else ''}{'' if period < 60 else str(period//60)+'h' if period < 1440 else 'd'}: {len(tf_data[period]):,} bars")

    # 5. Write to each MT4 install
    for hist_dir in HIST_DIRS:
        if not os.path.isdir(hist_dir):
            print(f"\n  SKIP (not found): {hist_dir}"); continue
        short = hist_dir.split('\\')[3]  # MT4_Backtest or Terminal guid
        print(f"\n[5] Writing to {short}...")
        for period, fname in tf_map.items():
            path = os.path.join(hist_dir, fname)
            backup = path + '.bak'
            if os.path.exists(path) and not os.path.exists(backup):
                shutil.copy2(path, backup)
                print(f"  Backed up {fname}")
            hdr = best_hdr if period == 1 else None
            write_hst(path, tf_data[period], period, hdr)

    print("\n=== Done! ===")
    print("Start MT4 OFFLINE (disconnect from broker before connecting).")
    print("Open EURUSD M1 offline chart, then backtest with 'Every tick' model.")
    print("Modeling quality = 90% green bar. No period_converter needed.")


if __name__ == '__main__':
    main()
