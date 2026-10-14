import os, re, importlib.util
H = r"C:\Users\endos\Desktop\hst_out"; LOT = 0.16
spec = importlib.util.spec_from_file_location("pr", r"C:\Users\endos\Signal\data\parse_results.py"); pr = importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
YRS8 = ["2010", "2013", "2014", "2015", "2016", "2018", "2023", "2024"]; YRS4 = ["2015", "2018", "2023", "2024"]
def num(s):
    try: return float(re.sub(r"[^\d\.\-]", "", s.replace(" ", "")))
    except Exception: return 0.0
def rep(path):
    h = open(path, encoding="utf-8", errors="ignore").read()
    def f(p): m = re.search(p, h, re.I | re.S); return m.group(1) if m else "0"
    wins = int(f(r"Profit trades \(% of total\).*?<td[^>]*>(\d+)")); tr = int(f(r"Total trades.*?<td[^>]*>(\d+)</td>"))
    return dict(trades=tr, wins=wins, gp=num(f(r"Gross profit.*?<td[^>]*>([\-\d\., ]+)</td>")), gl=num(f(r"Gross loss.*?<td[^>]*>([\-\d\., ]+)</td>")), net=num(f(r"Total net profit.*?<td[^>]*>([\-\d\., ]+)</td>")))
def agg(name, yrs):
    t = dict(trades=0, wins=0, gp=0.0, gl=0.0, net=0.0); n = 0
    for y in yrs:
        p = os.path.join(H, (f"WIN_GEN1_{y}_sp5.htm" if name == "BASE" else f"LOOP_{name}_{y}_sp5.htm"))
        if not os.path.exists(p): return None
        r = rep(p); n += 1
        for k in t: t[k] += r[k]
    return t
rows = [("BASE", "base b31 (WIN_GEN1)"), ("u_regime_2400", "regime 2400"), ("k_hurst_trend", "Hurst-trend gate"), ("l_dailydd", "daily DD freeze"), ("b5_sell_z25_n10", "b50 mean-reversion"), ("m5_sell_atr60", "b51 + ATR cap 60"), ("m5_sell_calm", "b51 + calm gate")]
for label, yrs in (("8 unseen years", YRS8), ("4 common years 2015/18/23/24", YRS4)):
    print(f"\n{label} (points, sp5)")
    print(f"{'candidate':22} {'trades':>6} {'win%':>5} {'avg win':>8} {'avg loss':>9} {'PF':>5} {'gross loss':>11} {'net':>9}")
    for key, name in rows:
        t = agg(key, yrs)
        if not t or t["trades"] == 0: continue
        w, l = t["wins"], t["trades"] - t["wins"]
        print(f"{name:22} {t['trades']:6d} {100*w/t['trades']:5.1f} {t['gp']/LOT/max(w,1):8.0f} {t['gl']/LOT/max(l,1):9.0f} {abs(t['gp']/t['gl']) if t['gl'] else 0:5.2f} {t['gl']/LOT:11.0f} {t['net']/LOT:9.0f}")
