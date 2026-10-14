"""telegram_status_bot.py - READ-ONLY status bot. Commands: /status /help. No trade, pause or file-write commands exist.
Needs env TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (set in your shell, never in this file). Only that chat id is answered."""
import json, os, urllib.request, urllib.parse, time
TOK = os.environ["TELEGRAM_BOT_TOKEN"]; CHAT = int(os.environ["TELEGRAM_CHAT_ID"])
LOG = r"C:\Users\endos\Signal\data\evolve_log.txt"
PAUSES = [r"C:\Users\endos\Desktop\hst_out\MT4_PAUSE", r"C:\Users\endos\MT4_Backtest\PAUSE"]
api = lambda m, **kw: json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{TOK}/{m}?" + urllib.parse.urlencode(kw), timeout=70))
def status():
    tail = open(LOG, encoding="utf-8", errors="ignore").read().splitlines()[-4:]
    return ("PAUSED" if any(os.path.exists(p) for p in PAUSES) else "not paused") + "\n" + "\n".join(tail) + "\n(backtest only, no live trading)"
off = 0
while True:
    try:
        for u in api("getUpdates", offset=off, timeout=60)["result"]:
            off = u["update_id"] + 1; m = u.get("message") or {}
            if m.get("chat", {}).get("id") != CHAT: continue
            t = (m.get("text") or "").split()[:1]
            api("sendMessage", chat_id=CHAT, text=status() if t == ["/status"] else "Commands: /status (read-only)")
    except Exception as e: print("warn", e, flush=True); time.sleep(10)
