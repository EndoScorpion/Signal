"""reject_audit.py - SILENT REJECT AUDIT replay. Reads reject_audit_b53.csv (written by MR_RegimeSwitch_b53 in the tester's MQL4\Files).
CLOCK: all times are MT4 SERVER time (UTC+2, UTC+3 US DST), same as the CLEAN history in mt4_tester2 (FXOpen raw M1 bid, rebuilt 2026-10-14).
For each raw z-signal that was blocked (gate = busy/spread/rollover/atrcap/mmr/calm_*/sidemode/regime) or TAKEN, replays: entry = bid/ask at signal,
exit after HOLD M15 bars or SL, in POINTS net of COST (default 5 commission + 1.4 spread; --cost N to change). Prints per-gate n, avg pts, win%, years positive.
A gate whose blocked signals average > 0 net (and stable across years) is a LEAD for new win logic / clone generations (never auto-applied; MT4 multi-period test + WIN rule needed).
Usage: python -E -P reject_audit.py <reject_audit_b53.csv> [--hold 48] [--sl 600] [--cost 6.4]. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>."""
import sys, csv, struct, datetime, bisect
from collections import defaultdict
a = sys.argv; opt = lambda n, d: float(a[a.index(n) + 1]) if n in a else d
HOLD, SL, COST = int(opt("--hold", 48)), opt("--sl", 600), opt("--cost", 6.4)
H = r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server\EURUSD15.hst"
raw = open(H, "rb").read()[148:]; n = len(raw) // 60
T, Hi, Lo, Cl = [], [], [], []
for k in range(n):
    t, o, h, l, c, *_ = struct.unpack_from("<qddddqiq", raw, k * 60); T.append(t); Hi.append(h); Lo.append(l); Cl.append(c)
res = defaultdict(list)
for r in csv.reader(open(a[1], encoding="utf-8", errors="ignore")):
    try:
        ts = int(datetime.datetime.strptime(r[0], "%Y.%m.%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp()); d = int(r[1]); bid, ask, gate = float(r[3]), float(r[4]), r[6]
    except Exception: continue
    i = bisect.bisect_right(T, ts) - 1
    if i < 0 or i + HOLD >= n: continue
    e = bid if d < 0 else ask; out = None
    for j in range(i + 1, i + 1 + HOLD):
        if d < 0 and Hi[j] >= e + SL * 1e-5: out = -SL; break
        if d > 0 and Lo[j] <= e - SL * 1e-5: out = -SL; break
    if out is None: out = (e - Cl[i + HOLD]) * 1e5 if d < 0 else (Cl[i + HOLD] - e) * 1e5
    res[gate].append((datetime.datetime.utcfromtimestamp(ts).year, out - COST))
print("gate | n | avg net pts | win% | years positive")
for g, v in sorted(res.items(), key=lambda kv: -sum(x for _, x in kv[1]) / len(kv[1])):
    ys = defaultdict(float)
    for y, x in v: ys[y] += x
    print(f"{g:10} | {len(v):5d} | {sum(x for _, x in v)/len(v):+7.1f} | {100*sum(x > 0 for _, x in v)/len(v):4.0f} | {sum(s > 0 for s in ys.values())}/{len(ys)}")
