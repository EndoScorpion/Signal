"""hist_integrity.py - integrity check of the EURUSD history, index and CSV files (read-only; never changes a data file).
  manifest : record size, mtime, CRC32 and SHA256 of the history files, symbols.raw (index), key CSVs and quote zips -> data/HIST_MANIFEST_<date>.csv (new file each run, 3 newest kept)
  verify   : recompute and compare against the newest manifest (reports changed, missing and new files)
  structure: per .hst: header version 401, size multiple of 60, strictly ascending unique timestamps, OHLC sanity, M15/H1 bars match aggregated M1 (random sample)
  zips     : ZipFile.testzip() = internal CRC of every member of the downloaded quote zips
  backup   : compares the D: flash copy against MT4_Backtest by SHA256
  all      : manifest-verify (or create one) + structure + zips + backup.  Report: data/HIST_INTEGRITY_REPORT.md
Run: python -I data/hist_integrity.py [manifest|verify|structure|zips|backup|all]. Exit code 2 if a problem is found."""
import os, sys, glob, csv, zlib, hashlib, zipfile, datetime, random
import numpy as np
D = r"C:\Users\endos\Signal\data"
HISTS = {"clean(mt4_tester2)": r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server",
         "MT4_Backtest": r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server",
         "mt4_tester": r"C:\Users\endos\Desktop\mt4_tester\history\FXOpenEU-ECN Live Server"}
BACKUP = r"D:\hst_backup_13Oct2026"
DT = np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"), ("tv", "<i8"), ("sp", "<i4"), ("rv", "<i8")])
problems = []; report = []
def say(s): print(s); report.append(s)
def hashes(p):
    c = 0; h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b: break
            c = zlib.crc32(b, c); h.update(b)
    return f"{c & 0xffffffff:08x}", h.hexdigest()
def tracked():
    out = []
    for lab, d in HISTS.items():
        out += sorted(glob.glob(os.path.join(d, "EURUSD*.hst")))
        s = os.path.join(d, "symbols.raw")
        if os.path.exists(s): out.append(s)
    out += sorted(glob.glob(os.path.join(D, "*.csv")))
    out += sorted(glob.glob(os.path.join(D, "quotes_download", "**", "*.zip"), recursive=True))
    return out
def do_manifest():
    day = datetime.date.today().strftime("%Y%m%d"); p = os.path.join(D, f"HIST_MANIFEST_{day}.csv"); rows = []
    for f in tracked():
        crc, sha = hashes(f); st = os.stat(f); rows.append([f, st.st_size, int(st.st_mtime), crc, sha])
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["path", "size", "mtime", "crc32", "sha256"]); w.writerows(rows)
    old = sorted(glob.glob(os.path.join(D, "HIST_MANIFEST_*.csv")))
    say(f"manifest written: {p} ({len(rows)} files)")
    for extra in old[:-3]: say(f"older manifest kept (delete by hand if you want): {os.path.basename(extra)}")
def do_verify():
    ms = sorted(glob.glob(os.path.join(D, "HIST_MANIFEST_*.csv")))
    if not ms: say("no manifest yet: creating one"); return do_manifest()
    old = {r["path"]: r for r in csv.DictReader(open(ms[-1]))}; now = set(tracked()); ch = 0
    say(f"verify against {os.path.basename(ms[-1])}")
    for p, r in old.items():
        if not os.path.exists(p): say(f"  MISSING   {p}"); problems.append(p); continue
        if os.path.getsize(p) == int(r["size"]) and int(os.stat(p).st_mtime) == int(r["mtime"]): continue   # unchanged size and mtime
        crc, sha = hashes(p)
        if sha != r["sha256"]: say(f"  CHANGED   {p} (size {r['size']} -> {os.path.getsize(p)}); expected for growing logs and weekly history updates, a problem otherwise"); ch += 1
    for p in sorted(now - set(old)): say(f"  NEW       {p}")
    say(f"  {len(old)} recorded, {ch} changed")
def check_hst(lab, path):
    name = os.path.basename(path); sz = os.path.getsize(path)
    if sz < 148 or (sz - 148) % 60: say(f"  BAD SIZE  {name}: {sz} bytes is not 148 + n*60"); problems.append(path); return None
    ver = int(np.fromfile(path, "<i4", 1)[0])
    if ver != 401: say(f"  BAD HEADER {name}: version {ver}, expected 401"); problems.append(path)
    a = np.memmap(path, dtype=DT, mode="r", offset=148); n = len(a)
    if n == 0: say(f"  EMPTY     {name}"); return None
    t = np.asarray(a["t"]); bad_order = int((np.diff(t) <= 0).sum())
    o, h, l, c = (np.asarray(a[k]) for k in "ohlc")
    bad_ohlc = int(((h < np.maximum(o, c) - 1e-9) | (l > np.minimum(o, c) + 1e-9) | (o <= 0) | (c <= 0)).sum())
    flag = "OK " if not bad_order and not bad_ohlc else "BAD"
    if flag == "BAD": problems.append(path)
    say(f"  {flag} {lab}/{name}: {n:,} bars {datetime.datetime.fromtimestamp(int(t[0]), datetime.timezone.utc):%Y-%m-%d}..{datetime.datetime.fromtimestamp(int(t[-1]), datetime.timezone.utc):%Y-%m-%d}, out-of-order/duplicate {bad_order}, bad OHLC {bad_ohlc}")
    return a
def agg_check(lab, d, tf, m1, rng):
    p = os.path.join(d, f"EURUSD{tf}.hst")
    if m1 is None or not os.path.exists(p): return
    a = np.memmap(p, dtype=DT, mode="r", offset=148); mt = np.asarray(m1["t"]); bad = 0; tested = 0
    for i in rng.sample(range(len(a)), min(1500, len(a))):
        t0 = int(a["t"][i]); lo = np.searchsorted(mt, t0); hi = np.searchsorted(mt, t0 + tf * 60)
        if hi <= lo: continue
        seg = m1[lo:hi]; tested += 1
        if abs(seg["o"][0] - a["o"][i]) > 1e-7 or abs(seg["c"][-1] - a["c"][i]) > 1e-7 or abs(seg["h"].max() - a["h"][i]) > 1e-7 or abs(seg["l"].min() - a["l"][i]) > 1e-7: bad += 1
    flag = "OK " if bad == 0 else "BAD"
    if bad: problems.append(p)
    say(f"  {flag} {lab}/M{tf} vs M1 aggregate: {bad} mismatches in {tested} sampled bars")
def do_structure():
    say("structure checks (.hst):"); rng = random.Random(7)
    for lab, d in HISTS.items():
        if not os.path.isdir(d): say(f"  skip {lab}: folder not found"); continue
        m1 = None
        for f in sorted(glob.glob(os.path.join(d, "EURUSD*.hst"))):
            a = check_hst(lab, f)
            if os.path.basename(f) == "EURUSD1.hst": m1 = a
        for tf in (15, 60): agg_check(lab, d, tf, m1, rng)
def do_zips():
    say("quote zips (internal CRC of every member):")
    for z in sorted(glob.glob(os.path.join(D, "quotes_download", "**", "*.zip"), recursive=True)):
        try: r = zipfile.ZipFile(z).testzip()
        except Exception as e: r = f"unreadable: {e}"
        say(f"  {'OK ' if r is None else 'BAD'} {os.path.basename(z)}" + ("" if r is None else f" first bad member: {r}"))
        if r is not None: problems.append(z)
def do_backup():
    say(f"flash backup {BACKUP} vs MT4_Backtest (SHA256):")
    if not os.path.isdir(BACKUP): say("  backup folder not found (flash drive not connected?)"); return
    for f in sorted(glob.glob(os.path.join(BACKUP, "EURUSD*.hst"))):
        src = os.path.join(HISTS["MT4_Backtest"], os.path.basename(f))
        if not os.path.exists(src): say(f"  no source for {os.path.basename(f)}"); continue
        same = hashes(f)[1] == hashes(src)[1]
        say(f"  {'same    ' if same else 'DIFFERS '} {os.path.basename(f)}" + ("" if same else "  (MT4_Backtest changed since the backup: re-backup after a deliberate update)"))
mode = sys.argv[1] if len(sys.argv) > 1 else "all"
if mode == "manifest": do_manifest()
elif mode == "verify": do_verify()
elif mode == "structure": do_structure()
elif mode == "zips": do_zips()
elif mode == "backup": do_backup()
else: do_verify(); do_structure(); do_zips(); do_backup()
say("PROBLEMS: " + (str(len(problems)) + " (see above)" if problems else "none"))
open(os.path.join(D, "HIST_INTEGRITY_REPORT.md"), "w", encoding="utf-8").write("# History integrity report " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n```\n" + "\n".join(report) + "\n```\n")
sys.exit(2 if problems else 0)
