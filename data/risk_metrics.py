"""risk_metrics.py - drawdown view of the finished candidates: max and average yearly drawdown (% of the 10,000 sim deposit), points per drawdown point,
and the leader's numbers on one line (used by the phone reports). Read-only. Backtest only."""
import json, os
D = r"C:\Users\endos\Signal\data"; LOT = 0.16
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
rows = []
for n, t in T.items():
    o = t.get("oos") or {}
    if len(o) < 6: continue
    pts = sum(v["profit"] for v in o.values()) / LOT; tr = sum(v["trades"] for v in o.values())
    if tr < 100: continue
    dds = [v.get("dd", 0) for v in o.values()]
    rows.append((pts, n, max(dds), sum(dds) / len(dds), pts / max(1e-9, max(dds))))
rows.sort(reverse=True)
if rows:
    p, n, mx, av, r = rows[0]; best_r = max(rows, key=lambda x: x[4])
    print(f"RISK leader {n}: max DD {mx:.1f}%, avg DD {av:.1f}%, {r:.0f} pts per DD%; best pts/DD% {best_r[1]} ({best_r[4]:.0f}, max DD {best_r[2]:.1f}%)")
