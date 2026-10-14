"""tech_watch.py - major TECHNICAL move tracker for EURUSD (FXOpen clean D1/H4 history). Flags: new 20/50/250-day high or low, close beyond Bollinger(20,2) bands, RSI14 below 30 or above 70,
SMA50/SMA200 cross state, today's range vs ATR14, and distance to key levels (data/key_levels.json, editable). Writes data/tech_watch_state.json (de-dup) and prints one summary line.
With --notify it sends a short ntfy message only for NEW flags. Offline, advisory only, no trading. History freshness is printed (the files update with the weekly history update).
Run: python -E -P data/tech_watch.py [--notify]"""
import numpy as np, os, json, sys, datetime, urllib.request
D = r"C:\Users\endos\Signal\data"; H = r"C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server"
DT = np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"), ("tv", "<i8"), ("sp", "<i4"), ("rv", "<i8")])
a = np.memmap(os.path.join(H, "EURUSD1440.hst"), dtype=DT, mode="r", offset=148); n = len(a)
t = np.asarray(a["t"]); o, h, l, c = (np.asarray(a[k]) for k in "ohlc")
last = datetime.datetime.fromtimestamp(int(t[-1]), datetime.timezone.utc)
fresh = (datetime.datetime.now(datetime.timezone.utc) - last).total_seconds() / 3600
def sma(x, p): return x[-p:].mean()
def rsi(x, p=14):
    d = np.diff(x[-(p * 4):]); up = np.where(d > 0, d, 0); dn = np.where(d < 0, -d, 0); au = up[:p].mean(); ad = dn[:p].mean()
    for u, v in zip(up[p:], dn[p:]): au = (au * (p - 1) + u) / p; ad = (ad * (p - 1) + v) / p
    return 100 - 100 / (1 + au / ad) if ad else 100
flags = []; px = c[-1]
for N, lab in ((20, "20-day"), (50, "50-day"), (250, "1-year")):
    if h[-1] >= h[-N - 1:-1].max(): flags.append(f"NEW {lab} HIGH {h[-1]:.4f}")
    if l[-1] <= l[-N - 1:-1].min(): flags.append(f"NEW {lab} LOW {l[-1]:.4f}")
m20, s20 = sma(c, 20), c[-20:].std()
if px > m20 + 2 * s20: flags.append("CLOSE ABOVE upper Bollinger(20,2)")
if px < m20 - 2 * s20: flags.append("CLOSE BELOW lower Bollinger(20,2)")
r = rsi(c)
if r < 30: flags.append(f"RSI14 OVERSOLD {r:.0f}")
if r > 70: flags.append(f"RSI14 OVERBOUGHT {r:.0f}")
s50, s200 = sma(c, 50), sma(c, 200); s50p, s200p = c[-51:-1].mean(), c[-201:-1].mean()
if s50 > s200 and s50p <= s200p: flags.append("GOLDEN CROSS SMA50 over SMA200")
if s50 < s200 and s50p >= s200p: flags.append("DEATH CROSS SMA50 under SMA200")
atr = np.mean(np.maximum(h[-15:-1] - l[-15:-1], np.abs(h[-15:-1] - c[-16:-2]))); rng = h[-1] - l[-1]
if atr and rng > 2 * atr: flags.append(f"RANGE SPIKE {rng/atr:.1f}x ATR14")
lv = json.load(open(os.path.join(D, "key_levels.json"))) if os.path.exists(os.path.join(D, "key_levels.json")) else {"levels": {"1.1100": "support", "1.1161": "2026 low", "1.1200": "round/support", "1.1330": "resistance", "1.1360": "resistance", "1.1500": "100-day MA/38.2% fib", "1.1600": "50-day area"}}
near = []
for k, why in lv["levels"].items():
    d = (px - float(k)) * 1e4
    if abs(d) <= 25: near.append(f"{k} ({why}) {d:+.0f} pips")
    if t.size > 1 and ((o[-1] < float(k) <= px) or (o[-1] > float(k) >= px)): flags.append(f"CROSSED {k} ({why})")
sp = os.path.join(D, "tech_watch_state.json"); st = json.load(open(sp)) if os.path.exists(sp) else {"sent": {}}
today = last.strftime("%Y-%m-%d"); new = [f for f in flags if st["sent"].get(f) != today]
msg = f"EURUSD D1 {px:.4f} (bar {today}, history {fresh:.0f} h old) | RSI {r:.0f} | SMA50 {s50:.4f} SMA200 {s200:.4f} | " + ("FLAGS: " + "; ".join(flags) if flags else "no major technical flags") + (" | near: " + ", ".join(near) if near else "")
if "--notify" in sys.argv and new:
    try:
        topic = open(os.path.join(D, "ntfy_topic.txt")).read().strip()
        urllib.request.urlopen(urllib.request.Request(f"https://ntfy.sh/{topic}", data=("EURUSD technical: " + "; ".join(new) + f" (price {px:.4f}, advisory only)").encode()[:900], headers={"Title": "EURUSD technical move", "Priority": "high"}), timeout=10)
        for f in new: st["sent"][f] = today
    except Exception: pass
json.dump(st, open(sp, "w"), indent=1); print(msg)
