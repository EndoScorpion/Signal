"""rebuild_history.py - build a clean EURUSD history (M1..MN) from the complete FXOpen raw zip with ONE consistent clock.
Clock: MT4 server time = UTC+2, UTC+3 during US daylight saving (2nd Sunday March 07:00 UTC .. 1st Sunday Nov 06:00 UTC),
measured from the original server-time months (2019-2021, Aug 2025+). CSV times are UTC.
Output goes to mt4_tester2 only; existing copies there are MOVED to _old_patchwork_copy first. The originals (MT4_Backtest, USB backup) are not touched.
Streams in chunks (low RAM). Run: python -E -P data/rebuild_history.py"""
import zipfile, io, os, shutil, datetime, sys, time
import numpy as np, pandas as pd
Z = r"C:\Users\endos\Signal\data\quotes_download\2026-10-13_18-48-11\EURUSD_M1_2009-01-01-14-00-51_2026-10-06-00-00-00.zip"
SRC = r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server"   # only for the 148-byte headers
OUT = r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server"
OLD = os.path.join(os.path.dirname(OUT), "_old_patchwork_copy")
DT = np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"), ("tv", "<i8"), ("sp", "<i4"), ("rv", "<i8")]); assert DT.itemsize == 60
os.makedirs(OLD, exist_ok=True)
for f in os.listdir(OUT):
    if f.startswith("EURUSD") and f.endswith(".hst") and not os.path.exists(os.path.join(OLD, f)): shutil.move(os.path.join(OUT, f), os.path.join(OLD, f))
def nth_sunday(y, m, n):
    d = datetime.date(y, m, 1); d += datetime.timedelta(days=(6 - d.weekday()) % 7 + 7 * (n - 1)); return d
bounds = []
for y in range(2008, 2028):
    s = nth_sunday(y, 3, 2); e = nth_sunday(y, 11, 1)
    bounds += [int(datetime.datetime(s.year, s.month, s.day, 7).replace(tzinfo=datetime.timezone.utc).timestamp()), int(datetime.datetime(e.year, e.month, e.day, 6).replace(tzinfo=datetime.timezone.utc).timestamp())]
bounds = np.array(bounds)
def to_server(ts_utc):   # +2h, +3h inside US DST windows
    return ts_utc + 7200 + 3600 * (np.searchsorted(bounds, ts_utc, side="right") % 2)
def hdr(name):
    with open(os.path.join(SRC, name), "rb") as f: return f.read(148)
zf = zipfile.ZipFile(Z); name = next(n for n in zf.namelist() if "bid" in n.lower())
print("source csv:", name)
t0 = time.time(); n_written = 0; last = -1; first_t = None
with open(os.path.join(OUT, "EURUSD1.hst"), "wb") as fo:
    fo.write(hdr("EURUSD1.hst"))
    for ch in pd.read_csv(zf.open(name), header=None, usecols=[0, 1, 2, 3, 4, 5], names=["dt", "o", "h", "l", "c", "v"], chunksize=500_000, dtype={"o": "float64", "h": "float64", "l": "float64", "c": "float64", "v": "float64"}):
        ts = pd.to_datetime(ch["dt"], format="%Y.%m.%d %H:%M:%S").values.astype("datetime64[s]").astype("int64")
        ts = to_server(ts)
        cm = np.maximum.accumulate(np.concatenate([[last], ts]))[:-1]; keep = ts > cm
        if not keep.all(): ch = ch[keep]; ts = ts[keep]
        if len(ts) == 0: continue
        a = np.zeros(len(ts), DT); a["t"] = ts; a["o"] = ch["o"].values; a["h"] = ch["h"].values; a["l"] = ch["l"].values; a["c"] = ch["c"].values; a["tv"] = ch["v"].values.astype("int64")
        fo.write(a.tobytes()); last = int(ts[-1]); n_written += len(ts); first_t = first_t if first_t is not None else int(ts[0])
print(f"M1 written: {n_written:,} bars, {datetime.datetime.utcfromtimestamp(first_t):%Y-%m-%d %H:%M} .. {datetime.datetime.utcfromtimestamp(last):%Y-%m-%d %H:%M} (server clock) in {time.time()-t0:.0f}s")
m1 = np.memmap(os.path.join(OUT, "EURUSD1.hst"), dtype=DT, mode="r", offset=148); T = m1["t"]
def agg(block, key):
    k = key(block["t"]); idx = np.concatenate([[0], np.flatnonzero(np.diff(k)) + 1])
    out = np.zeros(len(idx), DT); out["t"] = k[idx]; out["o"] = block["o"][idx]
    out["h"] = np.maximum.reduceat(block["h"], idx); out["l"] = np.minimum.reduceat(block["l"], idx)
    ends = np.concatenate([idx[1:], [len(block)]]) - 1; out["c"] = block["c"][ends]; out["tv"] = np.add.reduceat(block["tv"], idx); return out
TFS = {"EURUSD5.hst": 300, "EURUSD15.hst": 900, "EURUSD30.hst": 1800, "EURUSD60.hst": 3600, "EURUSD240.hst": 14400, "EURUSD1440.hst": 86400}
files = {n: open(os.path.join(OUT, n), "wb") for n in TFS}
for n, f in files.items(): f.write(hdr(n))
daily = []; counts = {n: 0 for n in TFS}; pos = 0; N = len(T)
while pos < N:
    end = min(pos + 1_000_000, N)
    if end < N:   # cut at a server-day boundary so every bucket up to D1 stays inside one block
        d = T[end - 1] // 86400
        while end < N and T[end] // 86400 == d: end += 1
    blk = np.array(m1[pos:end])
    for n, secs in TFS.items():
        o = agg(blk, lambda t, s=secs: (t // s) * s); files[n].write(o.tobytes()); counts[n] += len(o)
        if n == "EURUSD1440.hst": daily.append(o)
    pos = end
for f in files.values(): f.close()
d1 = np.concatenate(daily)
def agg_big(key, name):
    k = key(d1["t"]); idx = np.concatenate([[0], np.flatnonzero(np.diff(k)) + 1]); out = np.zeros(len(idx), DT); out["t"] = k[idx]; out["o"] = d1["o"][idx]
    out["h"] = np.maximum.reduceat(d1["h"], idx); out["l"] = np.minimum.reduceat(d1["l"], idx); ends = np.concatenate([idx[1:], [len(d1)]]) - 1; out["c"] = d1["c"][ends]; out["tv"] = np.add.reduceat(d1["tv"], idx)
    with open(os.path.join(OUT, name), "wb") as f: f.write(hdr(name)); f.write(out.tobytes())
    counts[name] = len(out)
agg_big(lambda t: ((t // 86400) - (((t // 86400) + 4) % 7)) * 86400, "EURUSD10080.hst")                                  # week starts Sunday
agg_big(lambda t: (t.astype("datetime64[s]").astype("datetime64[M]").astype("datetime64[s]").astype("int64")), "EURUSD43200.hst")   # month start
print("bars per file:", {k: f"{v:,}" for k, v in counts.items()}, f"| total {time.time()-t0:.0f}s")
