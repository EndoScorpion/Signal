import numpy as np, datetime, os, collections
NEW = r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server"; OLD = r"C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server"
DT = np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"), ("tv", "<i8"), ("sp", "<i4"), ("rv", "<i8")])
def mm(p): return np.memmap(p, dtype=DT, mode="r", offset=148)
dt = datetime.datetime.utcfromtimestamp
for f, exp in (("EURUSD15.hst", 1990), ("EURUSD60.hst", 497)):
    a = mm(os.path.join(NEW, f)); T = a["t"]; d = np.diff(T)
    big = np.flatnonzero(d > 4 * 86400)
    per = collections.Counter((dt(int(t)).year, dt(int(t)).month) for t in T[::max(1, 1)])
    thin = [(y, m, c) for (y, m), c in sorted(per.items()) if c < 0.8 * exp and not (y == 2009 and m == 1) and not (y == 2026 and m >= 10)]
    print(f"{f}: {len(T):,} bars | strictly increasing: {bool(np.all(d > 0))} | gaps > 4 days: " + (", ".join(f"{dt(int(T[i])):%Y-%m-%d}->{dt(int(T[i+1])):%Y-%m-%d}" for i in big) or "none") + f" | thin months: {thin if thin else 'none'}")
# alignment check against the original server-time months
n = mm(os.path.join(NEW, "EURUSD1.hst")); o = mm(os.path.join(OLD, "EURUSD1.hst"))
for label, a0, a1 in (("2019 H1", "2019-01-15", "2019-03-01"), ("2019 summer", "2019-04-01", "2019-10-25"), ("2020 H2", "2020-06-16", "2020-10-10"), ("2021 H2", "2021-04-01", "2021-10-30"), ("Sep-Oct 2025", "2025-09-01", "2025-10-28"), ("2025 Jan-Feb (old = shifted)", "2025-01-05", "2025-02-20"), ("2023 summer (old = shifted)", "2023-05-01", "2023-09-30")):
    s = int(datetime.datetime.fromisoformat(a0).replace(tzinfo=datetime.timezone.utc).timestamp()); e = int(datetime.datetime.fromisoformat(a1).replace(tzinfo=datetime.timezone.utc).timestamp())
    i0, i1 = np.searchsorted(n["t"], [s, e]); seg = np.array(n[i0:i1:25])
    idx = np.searchsorted(o["t"], seg["t"]); ok = idx < len(o); idx = np.where(ok, idx, 0); same_t = ok & (o["t"][idx] == seg["t"])
    close_ok = same_t & (np.abs(o["c"][idx] - seg["c"]) < 2e-5)
    print(f"{label:30} sampled {len(seg):6d} | old file has the same minute: {100*same_t.mean():5.1f}% | and same close within 2 pts: {100*close_ok.mean():5.1f}%")
print("first/last M1 (server clock):", dt(int(n['t'][0])), dt(int(n['t'][-1])))
