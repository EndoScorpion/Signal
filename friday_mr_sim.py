#!/usr/bin/env python3
"""
EURUSD Friday Mean-Reversion Simulator

Strategy: On Friday, if price has moved >= threshold from Monday open,
buy/sell the reversion back toward week-open. Hold until Friday close.
Net of costs from cost_model.json.

Usage:
    python3 friday_mr_sim.py --data data/history/EURUSD.csv --cost cost_model.json

Input CSV format: date,open,high,low,close,volume  (daily bars, 5-digit prices)
Expected FXOpen ECN spreads: ~2pt M15 for EURUSD. This script uses daily bars
so spread is estimated from cost_model cost_model[spread_bps][stock] by default;
override with --spread-pts for EURUSD-specific value.
"""
import csv, json, argparse, os
from datetime import datetime, date
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data/history/EURUSD.csv")
ap.add_argument("--cost", default="cost_model.json")
ap.add_argument("--threshold-pips", type=float, default=80,
                help="Min pip move Mon-open to Fri-open to trigger signal")
ap.add_argument("--spread-pts", type=float, default=2,
                help="FXOpen ECN EURUSD spread in broker points (default 2)")
ap.add_argument("--commission-pts", type=float, default=8,
                help="Round-turn commission in broker points (FXOpen max)")
ap.add_argument("--min-n", type=int, default=30,
                help="Minimum trades per period to report")
a = ap.parse_args()

COST = json.load(open(a.cost))
TAX = COST["tax_short_term_pct"] / 100

# 1 pip = 10 points on 5-digit EURUSD; convert spread/commission to pips
SPREAD_PIPS = a.spread_pts / 10
COMM_PIPS   = a.commission_pts / 10
COST_ROUND_TRIP_PIPS = SPREAD_PIPS + COMM_PIPS  # per side * 2 already in commission

def load_daily(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                d = datetime.strptime(r["date"].strip(), "%Y-%m-%d").date()
                rows.append({
                    "date": d,
                    "open":  float(r["open"]),
                    "high":  float(r["high"]),
                    "low":   float(r["low"]),
                    "close": float(r["close"]),
                })
            except Exception:
                continue
    return sorted(rows, key=lambda x: x["date"])

def period_label(d):
    y = d.year
    if y < 2020: return "2015-19"
    if y < 2023: return "2020-22"
    return "2023-26"

def run(rows):
    # Group by ISO week
    weeks = defaultdict(list)
    for r in rows:
        wk = r["date"].isocalendar()[:2]  # (year, week)
        weeks[wk].append(r)

    results = defaultdict(lambda: {"n": 0, "wins": 0, "gross": 0.0, "net": 0.0, "at": 0.0})

    for wk, days in sorted(weeks.items()):
        days = sorted(days, key=lambda x: x["date"])
        # Need Mon (weekday 0) and Fri (weekday 4)
        mon = next((d for d in days if d["date"].weekday() == 0), None)
        fri = next((d for d in days if d["date"].weekday() == 4), None)
        if not mon or not fri:
            continue
        if fri["date"] < "2015-01-01".__class__(2015, 1, 1):
            continue

        mon_open = mon["open"]
        fri_open = fri["open"]
        fri_close = fri["close"]

        move_pips = (fri_open - mon_open) * 10000  # 5-digit: 1 pip = 0.0001

        if abs(move_pips) < a.threshold_pips:
            continue

        # Signal: if price ran up >= threshold, fade it (sell); if ran down, buy
        if move_pips >= a.threshold_pips:
            direction = "SELL"
            gross_pips = (fri_open - fri_close) * 10000  # profit if price falls
        else:
            direction = "BUY"
            gross_pips = (fri_close - fri_open) * 10000  # profit if price rises

        net_pips = gross_pips - COST_ROUND_TRIP_PIPS
        at_pips  = net_pips * (1 - TAX) if net_pips > 0 else net_pips

        per = period_label(fri["date"])
        r = results[per]
        r["n"]     += 1
        r["wins"]  += net_pips > 0
        r["gross"] += gross_pips
        r["net"]   += net_pips
        r["at"]    += at_pips

    return results

def main():
    if not os.path.exists(a.data):
        print(f"[ERROR] Data file not found: {a.data}")
        print("Run fetch_history.py first to get EURUSD daily bars.")
        return

    rows = load_daily(a.data)
    if not rows:
        print("[ERROR] No rows loaded — check CSV format (date,open,high,low,close,volume)")
        return

    print(f"Loaded {len(rows)} daily bars from {rows[0]['date']} to {rows[-1]['date']}")
    print(f"Threshold: {a.threshold_pips} pips Mon-to-Fri-open")
    print(f"Cost: {COST_ROUND_TRIP_PIPS:.1f} pips/round-trip "
          f"(spread {SPREAD_PIPS:.1f} + commission {COMM_PIPS:.1f})")
    print()

    results = run(rows)

    header = f"{'Period':<12} {'N':>5} {'WR%':>7} {'AvgGross':>10} {'AvgNet':>10} {'AvgAfterTax':>13} {'Pass?':>6}"
    print(header)
    print("-" * len(header))

    all_n, all_wins, all_net = 0, 0, 0.0
    for per in ["2015-19", "2020-22", "2023-26"]:
        r = results.get(per, {"n": 0, "wins": 0, "gross": 0.0, "net": 0.0, "at": 0.0})
        n = r["n"]
        if n == 0:
            print(f"{per:<12} {'N/A':>5}")
            continue
        wr    = 100 * r["wins"] / n
        ag    = r["gross"] / n
        an    = r["net"]   / n
        aat   = r["at"]    / n
        flag  = "n<30" if n < a.min_n else ("PASS" if an > 0 else "FAIL")
        print(f"{per:<12} {n:>5} {wr:>7.1f} {ag:>10.2f} {an:>10.2f} {aat:>13.2f} {flag:>6}")
        all_n += n; all_wins += r["wins"]; all_net += r["net"]

    if all_n:
        print("-" * len(header))
        print(f"{'ALL':<12} {all_n:>5} {100*all_wins/all_n:>7.1f} "
              f"{'':>10} {all_net/all_n:>10.2f}")

    print()
    print("Note: Past results ≠ future results. Net of spread+commission+tax.")
    print("      Reject if n<30 in any period or inconsistent across periods.")
    print("      FXOpen ECN EURUSD 5-digit data required for production use.")
    os.makedirs("results", exist_ok=True)
    out = "results/friday_mr.txt"
    with open(out, "w") as f:
        f.write(f"Friday MR sim  threshold={a.threshold_pips}pip  cost={COST_ROUND_TRIP_PIPS:.1f}pip\n")
        for per, r in results.items():
            n = r["n"]
            if n:
                f.write(f"{per}  n={n}  wr={100*r['wins']/n:.1f}%  avg_net={r['net']/n:.2f}pip  avg_at={r['at']/n:.2f}pip\n")
    print(f"Results written to {out}")

if __name__ == "__main__":
    main()
