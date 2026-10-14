"""news_proximity.py - do trades near high-impact EUR/USD news behave differently? Joins trades (clean-history 'real' reports, server clock) with data/news_calendar_ff.csv
(mt4_server_time column). Buckets by minutes to the nearest high-impact EUR or USD event. Offline, read-only. python -E -P data/news_proximity.py [candidate_prefix]"""
import re, glob, os, csv, sys, bisect, datetime
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"
ev = []
for r in csv.DictReader(open(os.path.join(D, "news_calendar_ff.csv"), encoding="utf-8", errors="ignore")):
    if r["impact"] == "high" and r["currency"] in ("EUR", "USD") and r["mt4_server_time"]:
        try: ev.append(int(datetime.datetime.strptime(r["mt4_server_time"], "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp()))
        except ValueError: pass
ev = sorted(set(ev))
def trades(pattern):
    out = []
    for fp in sorted(glob.glob(pattern)):
        h = open(fp, encoding="utf-8", errors="ignore").read(); op = {}
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S):
            c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            if len(c) >= 8 and c[2] in ("buy", "sell") and re.match(r"\d{4}\.", c[1]): op[c[3]] = (c[1], float(c[4]))
            elif len(c) >= 10 and c[2] in ("s/l", "t/p", "close") and c[3] in op and c[8]:
                try: p = float(c[8].replace(" ", ""))
                except ValueError: continue
                tm, sz = op.pop(c[3]); out.append((int(datetime.datetime.strptime(tm, "%Y.%m.%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp()), p / sz))
    return out
def study(label, pattern):
    tr = trades(pattern); b = {"within 2h before": [], "within 2h after": [], "same day, other": [], "no event that day": []}
    for ts, pts in tr:
        i = bisect.bisect_left(ev, ts); nxt = ev[i] - ts if i < len(ev) else 10**9; prv = ts - ev[i - 1] if i > 0 else 10**9
        if 0 <= nxt <= 7200: b["within 2h before"].append(pts)
        elif 0 <= prv <= 7200: b["within 2h after"].append(pts)
        elif min(nxt, prv) <= 86400: b["same day, other"].append(pts)
        else: b["no event that day"].append(pts)
    print(f"\n{label}: {len(tr)} trades, {len(ev)} high-impact EUR/USD events in calendar")
    for k, v in b.items(): print(f"  {k:<20} {len(v):>5} trades  avg {sum(v)/max(1,len(v)):+7.1f} pts  win {100*sum(1 for x in v if x>0)/max(1,len(v)):4.1f}%")
study("BASE system (8 unseen years, real cost)", os.path.join(CL, "WIN_GEN1_[0-9][0-9][0-9][0-9]_real.htm"))
pre = sys.argv[1] if len(sys.argv) > 1 else "th_g2_AtrCapPts_90_hours_00-03"
study(f"valid clone {pre}", os.path.join(CL, f"LOOP_{pre}_[0-9][0-9][0-9][0-9]_real.htm"))
