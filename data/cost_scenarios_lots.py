"""cost_scenarios_lots.py - LOT-AWARE post-processing for the sim-balance runs (b63 UseLotSim). No MT4, no tester, read-only on reports.
For each finished clean report whose candidate name starts with sim_ (or --all for every LOOP_*.htm) it reads each CLOSED deal (lots, profit, balance after),
re-prices commission/spread per deal: net = profit - lots * (target_total_cost_pts - 5) USD (the tester ran at sp5 total cost; 1 pt = 1 USD per 1.00 lot on EURUSD, i.e. pts = USD/lots).
Scenarios: label from the name (tier7@500 -> commission 7 pts RT) plus spread 1 and 2 pts, and fixed 3.45pt / 5pt / 6pt / 8pt. Reports per year: trades, avg lots, net USD, return % of SimDeposit, max drawdown % from the balance column.
Writes a NEW csv data/cost_scenarios_lots_<stamp>.csv (never overwrites). Run: python -E -P data/cost_scenarios_lots.py [--all]"""
import re, glob, os, csv, sys, time
CL = r"C:\Users\endos\Desktop\hst_out\clean"; D = r"C:\Users\endos\Signal\data"
TIER = {"sim_tier7_at_500": (7.0, 500), "sim_tier5_at_1000": (5.0, 1000), "sim_tier5_at_1100": (5.0, 1100), "sim_tier3p6_at_25000": (3.6, 25000),
        "sim_tier3p6_at_27500": (3.6, 27500), "sim_tier3p0_at_250000": (3.0, 250000), "sim_tier3p0_at_275000": (3.0, 275000), "sim_tier3p6_at_50000": (3.6, 50000), "sim_tier5_at_5000": (5.0, 5000), "sim_tier5_at_10000": (5.0, 10000)}   # published USD basis; EUR-base is a separate unverified sensitivity
ROW = re.compile(r'<tr[^>]*><td>\d+</td><td class=msdate>[\d\. :]+</td><td>(close|s/l|t/p)[^<]*</td><td>\d+</td><td class=mspt>([\d\.]+)</td>(?:<td[^>]*>[^<]*</td>){3}<td class=mspt>(-?[\d\. ]+)</td><td class=mspt>(-?[\d\. ]+)</td>', re.S)
def num(s): return float(s.replace(" ", ""))
rows = []
for f in sorted(glob.glob(os.path.join(CL, "LOOP_*.htm"))):
    m = re.match(r"LOOP_(.+?)_(\d{4})_(?:real|sp5)\.htm$", os.path.basename(f))
    if not m or (not m.group(1).startswith("sim_") and "--all" not in sys.argv): continue
    name, year = m.groups(); comm, dep = TIER.get(name, (None, 10000))
    deals = [(float(a), num(b), num(c)) for _, a, b, c in ROW.findall(open(f, encoding="utf-8", errors="ignore").read())]
    if not deals: continue
    scen = {"3.45pt": 3.45, "5pt": 5.0, "6pt": 6.0, "8pt": 8.0}
    if comm: scen.update({f"tier{comm}+spr{s}": comm + s for s in (1, 2)})
    for lab, cost in scen.items():
        bal = dep; peak = dep; dd = 0.0; net = 0.0
        for lots, prof, _ in deals:
            p = prof - lots * (cost - 5.0); net += p; bal += p; peak = max(peak, bal); dd = max(dd, (peak - bal) / peak * 100)
        rows.append((name, year, lab, cost, len(deals), round(sum(d[0] for d in deals) / len(deals), 3), round(net, 2), round(net / dep * 100, 1), round(dd, 1)))
out = os.path.join(D, "cost_scenarios_lots_" + time.strftime("%Y%m%d_%H%M") + ".csv")
with open(out, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["candidate", "year", "scenario", "total_cost_pts", "trades", "avg_lots", "net_usd", "return_pct_of_simdeposit", "max_dd_pct"]); w.writerows(rows)
print(out, len(rows), "rows;", len(set(r[0] for r in rows)), "candidates")
