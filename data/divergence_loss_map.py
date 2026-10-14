"""divergence_loss_map.py - maps every base-system trade (clean-history MT4 reports, 8 unseen years) to the SMA-slope state at entry and finds
win logic / loss-prevention buckets. Features at the last completed M15 bar before entry (server clock, clean history):
  SSR = slope(SMA20)/slope(SMA200) state (aligned 0.2..5 / opposite / extreme), SMA10..200 slope-stack std-dev (converging = shrinking vs prior bar),
  SMA20-SMA50 slope gap converging/diverging, flat fast slope. Output: data/DIVERGENCE_LOSS_MAP.md (derived, offline; never live approval).
Run: python -I data/divergence_loss_map.py [report_glob_prefix, default clean/WIN_GEN1_*_real.htm]"""
import re, struct, glob, os, math, datetime, sys
from collections import defaultdict
HST = r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server\EURUSD15.hst"
pat = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\endos\Desktop\hst_out\clean\WIN_GEN1_*_real.htm"
raw = open(HST, "rb").read()[148:]; n = len(raw) // 60; T = []; C = []
for i in range(n):
    t, o, h, l, c, tv, sp, rv = struct.unpack_from("<qddddqiq", raw, i * 60); T.append(t); C.append(c)
def slopes(p):
    out = [0.0] * n; s = 0.0; prev = None
    for i, v in enumerate(C):
        s += v
        if i >= p: s -= C[i - p]
        if i >= p - 1:
            m = s / p
            if prev is not None: out[i] = (m - prev) * 1e5
            prev = m
    return out
SL = {p: slopes(p) for p in (10, 20, 50, 100, 200)}
def sd5(i): v = [SL[p][i] for p in SL]; m = sum(v) / 5; return math.sqrt(sum((x - m) ** 2 for x in v) / 5)
import bisect
def feats(ts):
    i = bisect.bisect_right(T, ts - 900) - 1          # last completed M15 bar before entry
    if i < 210: return None
    f, s = SL[20][i], SL[200][i]; r = (f / s) if abs(s) > 0.05 else None
    ssr = "n/a" if r is None else ("opposite" if r < 0 else ("aligned" if 0.2 <= r <= 5 else "extreme"))
    st = "stack_converging" if sd5(i) < sd5(i - 1) else "stack_diverging"
    gap = "gap_converging" if abs(SL[20][i] - SL[50][i]) < abs(SL[20][i - 1] - SL[50][i - 1]) else "gap_diverging"
    flat = "flat_fast" if abs(f) < 1.0 else "moving_fast"
    d0 = sd5(i); d4 = sd5(i - 4); ch = (d0 - d4) / (d4 + 1e-9)
    chg = "stack_sd_falling>10%" if ch < -0.10 else ("stack_sd_rising>10%" if ch > 0.10 else "stack_sd_steady")
    lvl = "stack_sd_low" if d0 < 2.0 else ("stack_sd_mid" if d0 < 5.0 else "stack_sd_high")
    return {"ssr": ssr, "stack": st, "gap": gap, "flat": flat, "stack_change": chg, "stack_level": lvl, "combo": f"{ssr}|{st}"}
trades = []
for fpath in sorted(glob.glob(pat)):
    html = open(fpath, encoding="utf-8", errors="ignore").read(); opens = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(c) >= 8 and c[2] in ("buy", "sell") and re.match(r"\d{4}\.\d\d\.\d\d", c[1]):
            opens[c[3]] = (c[1], c[2], float(c[4]))
        elif len(c) >= 10 and c[2] in ("s/l", "t/p", "close", "close at stop") and c[3] in opens and c[8]:
            try: pnl = float(c[8].replace(" ", ""))
            except ValueError: continue
            tm, side, size = opens.pop(c[3])
            ts = int(datetime.datetime.strptime(tm, "%Y.%m.%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp())
            trades.append((tm[:4], side, ts, pnl / size))   # pts = profit / lots
print("trades parsed:", len(trades))
buckets = defaultdict(lambda: defaultdict(lambda: [0, 0, 0.0]))   # feature -> value -> n, wins, sum pts
for y, side, ts, pts in trades:
    f = feats(ts)
    if f is None: continue
    for k, v in f.items():
        b = buckets[k][v]; b[0] += 1; b[1] += pts > 0; b[2] += pts
tot = sum(b[2] for b in buckets["ssr"].values()); N = sum(b[0] for b in buckets["ssr"].values())
out = ["# Divergence / convergence loss map (auto-generated)", "",
       f"Base trades mapped: {N}, total {tot:.0f} pts, average {tot/max(1,N):.1f} pts/trade (pts = profit / lots). Negative avg = loss bucket; skipping it is a loss-prevention rule candidate.", ""]
for k in ("ssr", "stack", "gap", "flat", "stack_change", "stack_level", "combo"):
    out += [f"## {k}", "", "| state | trades | win % | avg pts | total pts |", "|---|---|---|---|---|"]
    for v, (cnt, w, s) in sorted(buckets[k].items(), key=lambda kv: kv[1][2]):
        out.append(f"| {v} | {cnt} | {100*w/cnt:.1f} | {s/cnt:.1f} | {s:.0f} |")
    out.append("")
worst = sorted([(s, k, v, cnt) for k in buckets for v, (cnt, w, s) in buckets[k].items() if cnt >= 100])[:5]
out += ["## Biggest loss buckets (n >= 100)", ""] + [f"- {k} = {v}: {cnt} trades, {s:.0f} pts" for s, k, v, cnt in worst]
open(r"C:\Users\endos\Signal\data\DIVERGENCE_LOSS_MAP.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:46]))
