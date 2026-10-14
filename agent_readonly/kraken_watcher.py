"""kraken_watcher.py - READ-ONLY BTC/USD price alert (public Ticker endpoint, no API key, no orders).
Alerts via ntfy using the topic in data/ntfy_topic.txt. Run: python -I kraken_watcher.py"""
import json, time, urllib.request, os
D = r"C:\Users\endos\Signal\data"
BELOW = float(os.environ.get("BTC_ALERT_BELOW", 60000)); EVERY = 60
def price():
    r = json.load(urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", timeout=10))
    return float(next(iter(r["result"].values()))["c"][0])
def notify(msg):
    topic = open(os.path.join(D, "ntfy_topic.txt")).read().strip()
    urllib.request.urlopen(urllib.request.Request(f"https://ntfy.sh/{topic}", data=msg.encode(), headers={"Title": "BTC alert"}), timeout=10)
sent = False
while True:
    try:
        p = price(); print(time.strftime("%H:%M:%S"), f"BTC {p:,.2f}", flush=True)
        if p < BELOW and not sent: notify(f"BTC {p:,.0f} below {BELOW:,.0f} (advisory only)"); sent = True
        elif p >= BELOW: sent = False
    except Exception as e: print("warn", e, flush=True)
    time.sleep(EVERY)
