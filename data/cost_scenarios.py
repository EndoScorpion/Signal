"""cost_scenarios.py - POST-PROCESSING ONLY (no MT4, no tester). Re-prices every finished clean-history test under labelled cost scenarios.
Cost is linear in trades, so profit_new = profit_sp5 - (cost_new - 5) * 0.16 * trades (fixed 0.16 lot, the MR EAs have no SimDeposit/UseLotSim input, so balance-dependent lot size is NOT modelled here).
Scenarios: 5pt (total 5), 6pt (total 6, Nasif's max), and tier<comm>+spr<s> using the PUBLISHED USD basis (<1k 7, 1k-25k 5, 25k-250k 3.6, >250k 3.0 pts RT commission) with spread 1 and 2 pts. EUR basis (8.05/5.75/4.14/3.45) is a separate unverified scenario family labelled eur<comm>+spr<s>.
Writes a NEW file data/cost_scenarios_<YYYYMMDD_HHMM>.csv (never overwrites) and prints the top rows. Run: python -E -P data/cost_scenarios.py"""
import json, os, csv, time
D = r"C:\Users\endos\Signal\data"; SP = 5; LOT = 0.16
T = {}
for f in ("loop_state.json", "loop_state_clean.json"):
    try: T.update(json.load(open(os.path.join(D, f)))["tested"])
    except Exception: pass
sc = {"3.0pt": 3.0, "3.45pt": 3.45, "5pt": 5.0, "6pt": 6.0, "8pt": 8.0}   # 3.45pt = cheapest commission, EUR-base figure (USD published >250k bracket is 3.0, shown as tier3.0+spr rows); order 3.45 -> 5 -> 6 -> 8   # commission sequence 5 -> 6 -> 8 pts (8 = old global default), each labelled, never mixed
for c in (7, 5, 3.6, 3.0):
    for s in (1, 2): sc[f"tier{c}+spr{s}"] = c + s
for c in (8.05, 5.75, 4.14, 3.45):
    for s in (1, 2): sc[f"eur{c}+spr{s}"] = c + s
rows = []
for n, t in T.items():
    oos = t.get("oos") or {}
    if not oos: continue
    tr = sum(v["trades"] for v in oos.values())
    if tr < 1: continue
    base = sum(v["profit"] for v in oos.values())   # sp5 total profit in USD at 0.16 lot
    for lab, cost in sc.items():
        pts = (base - (cost - SP) * LOT * tr) / LOT
        rows.append((n, lab, cost, len(oos), tr, round(pts)))
out = os.path.join(D, "cost_scenarios_" + time.strftime("%Y%m%d_%H%M") + ".csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["candidate", "scenario", "total_cost_pts", "years", "trades", "net_pts_all_years"]); w.writerows(rows)
print(out, len(rows), "rows;", len(set(r[0] for r in rows)), "candidates")
for r in sorted([r for r in rows if r[1] == "6pt" and r[4] >= 100], key=lambda r: -r[5])[:8]: print("6pt", r[0][:50], r[3], "yrs", r[4], "trades", r[5], "pts")
