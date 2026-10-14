"""dsr_check.py - Deflated Sharpe Ratio (Bailey and Lopez de Prado) for the leader, using per-trade results from the clean-history 'real' reports of every candidate.
It answers: after trying N variants, is the leader's Sharpe still unlikely to be luck? DSR near 1 = likely real; below about 0.95 = could be selection luck.
Per-trade Sharpe SR = mean/sd of per-trade pts. Expected maximum SR under the null: SR0 = sqrt(Var[SR across candidates]) * ((1-g)*Z(1-1/N) + g*Z(1-1/(N*e))), g = Euler-Mascheroni.
DSR = Phi( (SR - SR0) * sqrt(T-1) / sqrt(1 - skew*SR + (kurt-1)/4*SR^2) ). Formulas from memory of the paper: verify constants before relying on it. Offline, backtest only.
Run: python -E -P data/dsr_check.py. Output: data/DSR_REPORT.md"""
import re, glob, os, math, json, statistics
from statistics import NormalDist
CL = r"C:\Users\endos\Desktop\hst_out\clean"; D = r"C:\Users\endos\Signal\data"; N01 = NormalDist()
def trades(name):
    out = []
    for fp in sorted(glob.glob(os.path.join(CL, f"LOOP_{name}_[0-9][0-9][0-9][0-9]_real.htm"))):
        html = open(fp, encoding="utf-8", errors="ignore").read(); op = {}
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
            c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            if len(c) >= 8 and c[2] in ("buy", "sell") and re.match(r"\d{4}\.", c[1]): op[c[3]] = float(c[4])
            elif len(c) >= 10 and c[2] in ("s/l", "t/p", "close") and c[3] in op and c[8]:
                try: p = float(c[8].replace(" ", ""))
                except ValueError: continue
                out.append(p / op.pop(c[3]))
    return out
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
res = {}
for n, t in T.items():
    if not t.get("oos"): continue
    x = trades(n)
    if len(x) >= 30 and statistics.pstdev(x) > 0: res[n] = x
def moments(x):
    m = statistics.fmean(x); s = statistics.pstdev(x); sk = sum(((v - m) / s) ** 3 for v in x) / len(x); ku = sum(((v - m) / s) ** 4 for v in x) / len(x)
    return m, s, m / s, sk, ku
srs = {n: moments(x)[2] for n, x in res.items()}
N = len(res); var_sr = statistics.pvariance(list(srs.values())) if N > 1 else 0.0
g = 0.5772156649; sr0 = math.sqrt(var_sr) * ((1 - g) * N01.inv_cdf(1 - 1 / N) + g * N01.inv_cdf(1 - 1 / (N * math.e))) if N > 1 else 0.0
rows = []
for n, x in res.items():
    m, s, sr, sk, ku = moments(x); T_ = len(x); den = math.sqrt(max(1e-9, 1 - sk * sr + (ku - 1) / 4 * sr * sr))
    rows.append((N01.cdf((sr - sr0) * math.sqrt(T_ - 1) / den), n, T_, sr, m))
rows.sort(reverse=True)
md = ["# Deflated Sharpe Ratio check (auto-generated, per-trade, real-cost reports)", "", f"Candidates with >=30 trades: {N}. Expected best per-trade SR by luck alone (SR0) = {sr0:.3f}.", "DSR >= 0.95 suggests the result is unlikely to be selection luck. Small trade counts weaken the test.", "",
      "| Candidate | DSR | trades | per-trade SR | avg pts/trade |", "|---|---|---|---|---|"] + [f"| {n} | {d:.3f} | {t} | {sr:.3f} | {m:.1f} |" for d, n, t, sr, m in rows[:15]]
open(os.path.join(D, "DSR_REPORT.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md[:12]))
