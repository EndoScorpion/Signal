"""cost_flags.py - COST-SENSITIVITY flags for every candidate, entry trigger and clone branch (Nasif 2026-10-14: if wins only exist when commission and spread are low,
that is a yellow or red flag). Uses the three cost passes the loop already runs per year (clean-history reports):
  cheap = sp3 report with 0.45 pt/trade added back as cost (FXOpen cheapest tier 3.45 pts), mid = sp5 (commission ceiling 5 pts), real = 'real' report (5 pts + average real spread, report 'Spread' cell).
For each candidate: pts and trades at each cost, trade-weighted cost, break-even round-trip cost (pts = 0), and a flag:
  GREEN  profit > 0 at the real cost AND break-even >= 9 pts (survives 1.5x of the realistic cost)
  YELLOW profit > 0 at the real cost but break-even < 9 pts, or real-cost profit < 50% of the cheap-tier profit
  RED    profit <= 0 at the real cost (wins only when commission/spread are low)
Genes (inputs changed vs the leader) inherit the worst flag share across the candidates carrying them. Output: data/COST_FLAGS.md and data/cost_flags.json.
Read-only on reports. Backtest tooling only, never live approval. Run: python -E -P data/cost_flags.py"""
import re, glob, os, json, collections
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"; LOT = 0.16
def cell(h, pat):
    m = re.search(pat, h, re.S); return float(m.group(1).replace(" ", "")) if m else None
def rep(path):
    h = open(path, encoding="utf-8", errors="ignore").read()
    return cell(h, r"Total net profit</td><td align=right>([\-\d\. ]+)"), cell(h, r"Total trades</td><td align=right>(\d+)"), cell(h, r"Spread</td><td align=right>(\d+)")
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
out = {}
for n, t in T.items():
    if not t.get("oos"): continue
    acc = {k: [0.0, 0, 0.0] for k in ("cheap", "mid", "real")}   # pts, trades, sum cost*trades
    for y in t["oos"]:
        for k, suf in (("cheap", "sp3_T3p45"), ("mid", "sp5"), ("real", "real")):
            p = os.path.join(CL, f"LOOP_{n}_{y}_{suf}.htm")
            if not os.path.exists(p): continue
            pr, tr, sp = rep(p)
            if pr is None or tr is None: continue
            cost = 3.45 if k == "cheap" else (5.0 if k == "mid" else float(sp or 0))
            pts = pr / LOT - (0.45 * tr if k == "cheap" else 0)
            acc[k][0] += pts; acc[k][1] += int(tr); acc[k][2] += cost * tr
    if acc["real"][1] == 0 or acc["cheap"][1] == 0: continue
    c = {k: (v[2] / v[1] if v[1] else 0) for k, v in acc.items()}
    slope = (acc["cheap"][0] - acc["real"][0]) / max(1e-9, (c["real"] - c["cheap"]))   # pts lost per 1 pt of extra round-trip cost
    be = c["cheap"] + acc["cheap"][0] / slope if slope > 0 else None
    pr_ = acc["real"][0]; pc = acc["cheap"][0]
    flag = "RED" if pr_ <= 0 else ("YELLOW" if (be is not None and be < 9) or (pc > 0 and pr_ < 0.5 * pc) else "GREEN")
    out[n] = {"flag": flag, "pts_cheap": round(pc), "pts_mid": round(acc["mid"][0]), "pts_real": round(pr_), "trades": acc["real"][1], "cost_real": round(c["real"], 1), "break_even": None if be is None else round(be, 1)}
cands = [n for n in out if out[n]["trades"] >= 100]
gene = collections.defaultdict(lambda: collections.Counter())
leader = max(cands, key=lambda n: out[n]["pts_real"]) if cands else None
lp = {k: v for k, v in T[leader]["patch"].items() if k != "_expert"} if leader else {}
for n in out:
    for k, v in T[n]["patch"].items():
        if k != "_expert" and lp.get(k) != v: gene[f"{k}={v}"][out[n]["flag"]] += 1
json.dump({"candidates": out, "leader": leader}, open(os.path.join(D, "cost_flags.json"), "w"), indent=1)
rows = sorted(((out[n]["pts_real"], n) for n in cands), reverse=True)
md = ["# Cost-sensitivity flags (auto-generated)", "", "pts over the unseen years at the cheapest tier (3.45), 5 pts, and the realistic cost (5 + avg spread). Break-even = round-trip cost at which profit reaches 0.", "",
      "| Candidate | flag | pts cheap | pts @5 | pts real | trades | real cost | break-even |", "|---|---|---|---|---|---|---|---|"]
md += [f"| {n} | {out[n]['flag']} | {out[n]['pts_cheap']} | {out[n]['pts_mid']} | {out[n]['pts_real']} | {out[n]['trades']} | {out[n]['cost_real']} | {out[n]['break_even']} |" for _, n in rows[:25]]
md += ["", "## Inputs (genes) by flag of the candidates that carry them (vs leader)", "", "| gene | GREEN | YELLOW | RED |", "|---|---|---|---|"]
md += [f"| {g} | {c['GREEN']} | {c['YELLOW']} | {c['RED']} |" for g, c in sorted(gene.items(), key=lambda kv: -kv[1]["RED"])[:20]]
open(os.path.join(D, "COST_FLAGS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
cnt = collections.Counter(out[n]["flag"] for n in cands)
print(f"leader {leader}: {out[leader]['flag'] if leader else '?'} (cheap {out[leader]['pts_cheap']}, @5 {out[leader]['pts_mid']}, real {out[leader]['pts_real']}, break-even {out[leader]['break_even']} pts)" if leader else "no leader"); print(f"flags over {len(cands)} candidates with >=100 trades: {dict(cnt)}")
for _, n in rows[:6]: print(" ", n, out[n]["flag"], out[n]["pts_cheap"], out[n]["pts_mid"], out[n]["pts_real"], out[n]["break_even"])
