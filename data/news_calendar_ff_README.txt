news_calendar_ff.csv - EUR/USD high/medium impact economic events, 2011-01 .. 2026-10
SOURCE: Forex Factory public calendar month pages (forexfactory.com/calendar?month=mon.year), scraped 2026-10-14
  by news_calendar_scrape.py (1 request per 4-6 s, honest User-Agent, no login/proxy). robots.txt checked: no Disallow rules.
FILTER: currency EUR or USD; impact high (red) or medium (orange) only (includes 'Speaks' events at those levels).
TIME ZONE: pages were served in America/New_York (page default, label only). The embedded per-event
  'dateline' is a UTC epoch; utc_time / time_utc_hhmm come from it directly (not from the displayed text).
  mt4_server_time = UTC+2, UTC+3 during US DST (2nd Sun Mar 07:00 UTC .. 1st Sun Nov 06:00 UTC).
  All-day/tentative rows (time_flag != empty): no time; date_utc is epoch-derived and may be +-1 day of the intended date.
  Validated: NFP 13:30 UTC winter / 12:30 UTC summer; ECB decisions consistent with 13:45 CET (2011-2022), 14:15 CET (from 2022-07).
CAVEATS: personal backtesting use only; Forex Factory ToS apply; do not redistribute. Append-only; actual/forecast/previous
  are as shown on scrape date (revisions possible). Progress file: news_calendar_ff_progress.txt (months done).
