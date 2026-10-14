"""Slow, polite, resumable Forex Factory month-page scraper (personal backtesting use only).

Run:  python -E -P news_calendar_scrape.py [--from 2011-01] [--to 2026-10] [--max N]
Walks months newest -> oldest, 1 request per 4-6 s (jittered). Appends rows to
news_calendar_ff.csv and records finished months in news_calendar_ff_progress.txt (resume).
Keeps EUR/USD events with impact High/Medium only. Times: FF 'dateline' is a UTC epoch
(independent of the viewer zone); page display zone was America/New_York (label only).
Stops on repeated blocks / Cloudflare challenge. Never redistribute the output.
"""
import sys, os, re, json, csv, time, random, gzip, datetime as dt
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "news_calendar_ff.csv")
PROG = os.path.join(HERE, "news_calendar_ff_progress.txt")
UA = "PersonalBacktestCalendarFetcher/1.0 (single user, personal research, slow ~1 req/5s)"
MON = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
FIELDS = ["date_utc", "time_utc_hhmm", "page_tz_label", "page_time_label", "currency", "impact",
          "title", "actual", "forecast", "previous", "time_flag", "utc_time", "mt4_server_time", "event_id"]


def nth_sunday(y, m, n):
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def us_dst(u):  # u: naive UTC datetime
    s = dt.datetime.combine(nth_sunday(u.year, 3, 2), dt.time(7, 0))   # 2:00 EST
    e = dt.datetime.combine(nth_sunday(u.year, 11, 1), dt.time(6, 0))  # 2:00 EDT
    return s <= u < e


def mt4(u):
    return u + dt.timedelta(hours=3 if us_dst(u) else 2)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                                               "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            b = gzip.decompress(b)
        return b.decode("latin-1")


def parse(html):
    if "cf-chl" in html[:5000] or "Just a moment" in html[:3000]:
        raise RuntimeError("CLOUDFLARE_CHALLENGE")
    i = html.find("days: [")
    if i < 0:
        raise ValueError("no days json")
    days, _ = json.JSONDecoder().raw_decode(html[i + 6:])
    return days


def rows_from(days):
    out = []
    for day in days:
        for e in day.get("events", []):
            if e.get("currency") not in ("EUR", "USD") or e.get("impactName") not in ("high", "medium"):
                continue
            lab = (e.get("timeLabel") or "").strip()
            has_time = bool(re.match(r"^\d{1,2}:\d{2}(am|pm)$", lab))
            u = dt.datetime.utcfromtimestamp(e["dateline"])
            if has_time:
                flag, d, t, ut, mt = "", u.strftime("%Y-%m-%d"), u.strftime("%H:%M"), u.strftime("%Y-%m-%d %H:%M"), mt4(u).strftime("%Y-%m-%d %H:%M")
            else:
                # all-day / tentative: date only. Derive the page-zone calendar date from the day header, not epoch.
                flag = "allday_or_tentative:" + (lab or "none")
                d = dt.datetime.utcfromtimestamp(e["dateline"]).strftime("%Y-%m-%d")
                t = ut = mt = ""
            out.append([d, t, "America/New_York(page display; utc from epoch)", lab, e["currency"],
                        e["impactName"], e["name"], e.get("actual", ""), e.get("forecast", ""),
                        e.get("previous", ""), flag, ut, mt, e["id"]])
    return out


def main():
    a = sys.argv[1:]
    def opt(k, dflt):
        return a[a.index(k) + 1] if k in a else dflt
    fy, fm = map(int, opt("--from", "2011-01").split("-"))
    ty, tm = map(int, opt("--to", "2026-10").split("-"))
    mx = int(opt("--max", "100000"))
    done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
    new = not os.path.exists(OUT)
    months = []
    y, m = ty, tm
    while (y, m) >= (fy, fm):
        months.append((y, m)); m -= 1
        if m == 0: y, m = y - 1, 12
    blocks = 0; n = 0; t0 = time.time()
    for y, m in months:
        key = f"{y}-{m:02d}"
        if key in done: continue
        if n >= mx: break
        url = f"https://www.forexfactory.com/calendar?month={MON[m-1]}.{y}"
        try:
            html = fetch(url); days = parse(html); del html
            blocks = 0
        except urllib.error.HTTPError as ex:
            ra = ex.headers.get("Retry-After")
            blocks += 1
            print(key, "HTTP", ex.code, "retry-after", ra, flush=True)
            if blocks >= 3 or ex.code in (403,) and blocks >= 2:
                print("STOP: repeated blocks"); sys.exit(2)
            time.sleep(min(int(ra), 600) if ra and ra.isdigit() else 60 * blocks * 2)
            continue
        except RuntimeError as ex:
            print("STOP:", ex); sys.exit(3)
        except Exception as ex:
            blocks += 1
            print(key, "ERR", repr(ex), flush=True)
            if blocks >= 3: print("STOP: repeated errors"); sys.exit(4)
            time.sleep(30); continue
        rows = rows_from(days)
        with open(OUT, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new: w.writerow(FIELDS); new = False
            w.writerows(rows)
        with open(PROG, "a") as f: f.write(key + "\n")
        n += 1
        print(key, len(rows), "rows", f"{time.time()-t0:.0f}s", flush=True)
        time.sleep(random.uniform(4.0, 6.0))
    print("finished", n, "months in", f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
