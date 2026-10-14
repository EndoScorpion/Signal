import re, os
S = r"C:\Users\endos\Signal"; changed = []
def sub(path, pairs, regex=False):
    if not os.path.exists(path): print("missing", path); return
    t = open(path, encoding="utf-8").read(); o = t
    for a, b in pairs: t = re.sub(a, b, t) if regex else t.replace(a, b)
    if t != o: open(path, "w", encoding="utf-8").write(t); changed.append(path)
HOUR = "UTC hours 20-22 (the CSV clock). In MT4 server time (UTC+2, UTC+3 in US DST) the rollover spread spike is about 22:00-01:00 with the peak 23:00-00:00"
sub(S + r"\data\RED_ZONES.md", [("server hours 20-22 spike", HOUR + " (spike"), ("Avoid new entries in hours 21-22.", "Avoid new entries in SERVER hours 23-01 (UTC 21-22).")])
sub(S + r"\data\SPREAD_COMMISSION_RECORDS.md", [("Mean spread by server hour, 2023-2026 (pts):", "Mean spread by UTC hour (CSV clock; NOT server hour), 2023-2026 (pts):"),
    ("-> avoid new entries in server hours 20-22 (rollover).", "-> in MT4 server time (UTC+2, UTC+3 in US DST) the spike is about 22:00-01:00, peak 23:00-00:00: avoid new entries in server hours 23-01.")])
sub(r"C:\Users\endos\.claude\projects\C--Users-endos-Signal\memory\feedback_commission_fxopen.md", [("Rollover hours spike (server hour 21 avg 17 pts, hour 22 avg 7.7, hour 20 2.5)", "Rollover spread spike by UTC hour (CSV clock): UTC 21 avg 17 pts, UTC 22 avg 7.7, UTC 20 2.5 (= MT4 server time about 22:00-01:00, peak 23:00-00:00, server clock UTC+2/+3 US DST)")])
sub(S + r"\data\spread_stats.py", [('Streams the two CSVs inside the full-history zip', 'TIME ZONE: the CSV clock is UTC, so the "hour" columns are UTC hours (MT4 server time = UTC+2, UTC+3 in US DST).\nSOURCE: FXOpen QuotesDownloader raw M1 bid+ask (EURUSD, FXOpenEU-ECN). Streams the two CSVs inside the full-history zip')])
for f, note in (("shadow_audit.py", "TIME NOTE: SPR hour keys are UTC hours (CSV clock) while the M15 .hst used here carries a mixed (patchwork) clock; hour-based costs are approximate. Redo on the clean history (mt4_tester2, server clock UTC+2/+3 US DST)."),
                ("scalp_lab.py", "TIME NOTE: SPR hour keys are UTC hours (CSV clock) while the M15 .hst used here carries a mixed (patchwork) clock; the 20-22 rollover exclusion is approximate. Redo on the clean history (mt4_tester2, server clock UTC+2/+3 US DST).")):
    sub(S + "\\data\\" + f, [('"""', '"""' + note + "\n", )]) if False else None
    p = S + "\\data\\" + f
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        if "TIME NOTE" not in t: open(p, "w", encoding="utf-8").write(t.replace('"""', '"""\n' + note + "\n", 1)); changed.append(p)
print("updated:", [os.path.basename(c) for c in changed])
