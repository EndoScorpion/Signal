#!/usr/bin/env python3
"""
Revolt Gate Test — applies F1 (SARA/PRV) and F2 (Regime+Accel) gates
to EURUSD D1 survivor strategies and compares before vs after filter.
Strategies tested: PAV_r40, PAV_r35, CRB_n20k20, CRB_n20k15, GAP_t3, GAP_MICRO, STRK, ZSCO
Formula source: /mnt/project-files/results_thread7_momentum_ratio.md
"""
import csv, math, sys, os, json
from collections import defaultdict

# ── Data ─────────────────────────────────────────────────────────────────────
DATA_PATH = "/mnt/project-files/uploads/EURUSD_D1.csv"
COST_RT   = 0.0002   # 2 pip round-trip (spread + commission + slip)
TAX_RATE  = 0.0       # skip tax for FX (already small numbers)

def load_eurusd(path):
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader); next(reader); next(reader)  # skip 3-row yahoo header
        for r in reader:
            try:
                date, o, h, l, c, v = r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])
                rows.append({"date": date, "o": o, "h": h, "l": l, "c": c, "v": v})
            except (ValueError, IndexError):
                continue
    return rows

# ── Helpers ───────────────────────────────────────────────────────────────────
def sma(arr, i, n):
    if i < n - 1: return None
    return sum(arr[i-n+1:i+1]) / n

def atr14(highs, lows, closes, i):
    if i < 1: return abs(highs[i] - lows[i])
    trs = [max(highs[j] - lows[j],
               abs(highs[j] - closes[j-1]),
               abs(lows[j]  - closes[j-1])) for j in range(max(1, i-13), i+1)]
    return sum(trs) / len(trs)

def stoch_k(highs, lows, closes, i, period=14):
    if i < period - 1: return 50.0
    hh = max(highs[i-period+1:i+1])
    ll = min(lows[i-period+1:i+1])
    return 50.0 if hh == ll else 100.0 * (closes[i] - ll) / (hh - ll)

def bb_lower(closes, i, n=20, mult=2.0):
    if i < n - 1: return None
    m = sma(closes, i, n)
    sd = math.sqrt(sum((closes[i-n+1+j] - m)**2 for j in range(n)) / n)
    return m - mult * sd

# ── F1: SARA/PRV gate (Formula 1 from Thread7) ────────────────────────────────
def compute_sara(closes, i):
    """SARA = SMA2_slope / SMA50_slope — fast revolt vs regime slope."""
    if i < 51: return 0.0
    sma2_now  = (closes[i]   + closes[i-1]) / 2
    sma2_prev = (closes[i-1] + closes[i-2]) / 2
    sma50_now  = sma(closes, i,   50)
    sma50_prev = sma(closes, i-1, 50)
    slope_sma2  = (sma2_now  - sma2_prev)  / closes[i]
    slope_sma50 = (sma50_now - sma50_prev) / closes[i]
    return max(-20.0, min(20.0, slope_sma2 / (abs(slope_sma50) + 1e-10)))

def compute_prv(closes, i):
    """PRV = PD10 (SMA10) slope."""
    if i < 11: return 0.0
    sma10_now  = sma(closes, i,   10)
    sma10_prev = sma(closes, i-1, 10)
    return (sma10_now - sma10_prev) / closes[i]

def f1_gate(closes, highs, lows, i):
    """Formula 1 (SARA/PRV weighted). Returns (score, buy_ok, sell_ok)."""
    if i < 52: return 0.0, False, False
    atr = atr14(highs, lows, closes, i)
    SARA  = compute_sara(closes, i)
    PRV   = compute_prv(closes, i)
    stk   = stoch_k(highs, lows, closes, i, 14)
    prv_n = max(-5, min(5, PRV / (atr + 1e-10))) / 5.0
    score = (0.45 * (SARA / 20.0)) + (0.30 * prv_n) + (0.25 * (0.5 - stk / 100.0))
    return score, score > 0.05, score < -0.05

# ── F2: Regime+Accel gate (Formula 2 from Thread7) ────────────────────────────
def f2_gate(closes, highs, lows, i):
    """Formula 2 (Regime-first revolt). Returns (revolt_score, buy_ok, sell_ok)."""
    if i < 53: return 0.0, False, False
    regime_k = stoch_k(highs, lows, closes, i, 50)
    regime_ok = regime_k < 55

    sma2_now  = (closes[i]   + closes[i-1]) / 2
    sma2_1bar = (closes[i-1] + closes[i-2]) / 2
    sma2_2bar = (closes[i-2] + closes[i-3]) / 2
    slope_now  = (sma2_now  - sma2_1bar) / closes[i]
    slope_prev = (sma2_1bar - sma2_2bar) / closes[i]
    accel_ok = slope_now > slope_prev

    SARA = compute_sara(closes, i)
    sara_ok = SARA > 0

    revolt_score = (0.50 * (1 if regime_ok else 0) +
                    0.30 * (1 if accel_ok  else 0) +
                    0.20 * (1 if sara_ok   else 0))
    return revolt_score, revolt_score >= 0.50, False  # BUY focus

# ── Strategy signal functions ─────────────────────────────────────────────────
def sig_pav_r40(closes, highs, lows, i):
    """PAV_r40a10-40h5: fractal low + RSI<40 + ATR move > 0.10-0.40%."""
    if i < 52: return False
    atr = atr14(highs, lows, closes, i)
    # pivot low: current low < both neighbors
    is_pivot = lows[i] < lows[i-1] and lows[i] < lows[i+1] if i+1 < len(lows) else lows[i] < lows[i-1]
    # RSI(14) < 40
    gains = [max(closes[j]-closes[j-1], 0) for j in range(i-13, i+1)]
    losses= [max(closes[j-1]-closes[j], 0) for j in range(i-13, i+1)]
    ag, al = sum(gains)/14, sum(losses)/14
    rsi = 50 if al == 0 else 100 - 100/(1 + ag/al)
    # ATR kinematic: 10-40% of ATR move down in bar
    bar_range = highs[i] - lows[i]
    atr_share = bar_range / (atr + 1e-10) * 100
    return is_pivot and rsi < 40 and 10 <= atr_share <= 40

def sig_pav_r35(closes, highs, lows, i):
    """PAV_r35a5-30h4."""
    if i < 52: return False
    atr = atr14(highs, lows, closes, i)
    is_pivot = lows[i] < lows[i-1] and (i+1 >= len(lows) or lows[i] < lows[i+1])
    gains = [max(closes[j]-closes[j-1], 0) for j in range(i-13, i+1)]
    losses= [max(closes[j-1]-closes[j], 0) for j in range(i-13, i+1)]
    ag, al = sum(gains)/14, sum(losses)/14
    rsi = 50 if al == 0 else 100 - 100/(1 + ag/al)
    bar_range = highs[i] - lows[i]
    atr_share = bar_range / (atr + 1e-10) * 100
    return is_pivot and rsi < 35 and 5 <= atr_share <= 30

def sig_crb_n20k20(closes, highs, lows, i):
    """CRB_n20k20h5: double dip below Bollinger lower with Stoch<20."""
    if i < 22: return False
    bbl = bb_lower(closes, i, 20)
    if bbl is None: return False
    stk = stoch_k(highs, lows, closes, i, 20)
    # current and prev bar both below BB lower (double-dip)
    return closes[i] < bbl and closes[i-1] < bb_lower(closes, i-1, 20) and stk < 20

def sig_crb_n20k15(closes, highs, lows, i):
    """CRB_n20k15h3: BB lower touch + Stoch<15."""
    if i < 22: return False
    bbl = bb_lower(closes, i, 20)
    if bbl is None: return False
    stk = stoch_k(highs, lows, closes, i, 20)
    return closes[i] < bbl and stk < 15

def sig_gap_t3(closes, highs, lows, i):
    """GAP_t3h3: gap up > 0.3% then reversal signal (BUY gap fill from below)."""
    if i < 2: return False
    gap_pct = (closes[i] - closes[i-1]) / closes[i-1] * 100
    # Large bear bar (exhaustion): close drops > 0.3% ATR multiple
    atr = atr14(highs, lows, closes, i)
    bar_drop = closes[i-1] - closes[i]
    return bar_drop > 0.003 * closes[i] and abs(gap_pct) < 0.3  # gap-fill after large down bar

def sig_gap_micro(closes, highs, lows, i):
    """GAP_MICRO_t1h3: micro gap > 0.1%."""
    if i < 2: return False
    gap_pct = abs(closes[i] - closes[i-1]) / closes[i-1] * 100
    return 0.1 <= gap_pct < 0.3 and closes[i] < closes[i-1]  # down gap, expect fill

def sig_strk(closes, highs, lows, i):
    """STRK: 3+ consecutive down bars reversal."""
    if i < 4: return False
    return all(closes[i-j] < closes[i-j-1] for j in range(3))

def sig_zsco(closes, highs, lows, i):
    """ZSCO: Z-score < -1.5 mean reversion."""
    if i < 20: return False
    m = sma(closes, i, 20)
    sd = math.sqrt(sum((closes[i-19+j] - m)**2 for j in range(20)) / 20)
    if sd < 1e-10: return False
    z = (closes[i] - m) / sd
    return z < -1.5

STRATEGIES = {
    "PAV_r40h5":    (sig_pav_r40,   5),
    "PAV_r35h4":    (sig_pav_r35,   4),
    "CRB_n20k20h5": (sig_crb_n20k20,5),
    "CRB_n20k15h3": (sig_crb_n20k15,3),
    "GAP_t3h3":     (sig_gap_t3,    3),
    "GAP_MICROh3":  (sig_gap_micro, 3),
    "STRK_h4":      (sig_strk,      4),
    "ZSCO_h4":      (sig_zsco,      4),
}

def period(d):
    return "2015-19" if d < "2020" else "2020-22" if d < "2023" else "2023-26"

def backtest(rows, sig_fn, hold, gate=None):
    closes = [r["c"] for r in rows]
    highs  = [r["h"] for r in rows]
    lows   = [r["l"] for r in rows]
    dates  = [r["date"] for r in rows]
    results = []
    prev = False
    for i in range(max(55, 1), len(rows) - hold):
        if dates[i] < "2015": continue
        on = sig_fn(closes, highs, lows, i)
        if on and not prev:
            if gate is not None:
                _, buy_ok, _ = gate(closes, highs, lows, i)
                if not buy_ok:
                    prev = on; continue
            ret = (closes[i + hold] / closes[i] - 1) * 100
            net = ret - COST_RT * 100
            results.append({"date": dates[i], "net": net, "period": period(dates[i])})
        prev = on
    return results

def summarize(trades, label):
    if not trades:
        return {"label": label, "n": 0, "win_pct": 0, "avg_net": 0}
    n = len(trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    avg  = sum(t["net"] for t in trades) / n
    by_period = defaultdict(list)
    for t in trades:
        by_period[t["period"]].append(t["net"])
    periods = {}
    for p, vals in sorted(by_period.items()):
        periods[p] = {"n": len(vals), "win_pct": round(100*sum(1 for v in vals if v>0)/len(vals),1),
                      "avg": round(sum(vals)/len(vals), 4)}
    return {"label": label, "n": n, "win_pct": round(100*wins/n, 1),
            "avg_net": round(avg, 4), "periods": periods}

def run():
    print("Loading EURUSD D1...")
    rows = load_eurusd(DATA_PATH)
    print(f"  {len(rows)} bars ({rows[0]['date']} to {rows[-1]['date']})")

    results = []
    for name, (fn, hold) in STRATEGIES.items():
        base   = backtest(rows, fn, hold, gate=None)
        f1     = backtest(rows, fn, hold, gate=f1_gate)
        f2     = backtest(rows, fn, hold, gate=f2_gate)
        f1f2   = backtest(rows, fn, hold,
                          gate=lambda c,h,l,i: (
                              0, f1_gate(c,h,l,i)[1] and f2_gate(c,h,l,i)[1], False))

        sb   = summarize(base,  f"{name} BASE")
        sf1  = summarize(f1,    f"{name} F1")
        sf2  = summarize(f2,    f"{name} F2")
        sf12 = summarize(f1f2,  f"{name} F1+F2")
        results.append((name, hold, sb, sf1, sf2, sf12))

    # ── Report ────────────────────────────────────────────────────────────────
    lines = []
    lines.append("# Revolt Gate Test Results")
    lines.append("EURUSD D1 · F1 (SARA/PRV) and F2 (Regime+Accel) entry gates")
    lines.append("Cost RT: 0.0002 (2 pip) · 2026-10-17\n")
    lines.append("| Strategy | Filter | n | Win% | Avg Net% | Kept% |")
    lines.append("|----------|--------|---|------|----------|-------|")

    for name, hold, sb, sf1, sf2, sf12 in results:
        n0 = sb["n"] or 1
        for s in [sb, sf1, sf2, sf12]:
            tag = s["label"].split(" ", 1)[1] if " " in s["label"] else s["label"]
            kept = f"{100*s['n']//n0}%" if s["n"] > 0 else "0%"
            win_str  = f"{s['win_pct']}%" if s["n"] > 0 else "—"
            avg_str  = f"{s['avg_net']:+.4f}%" if s["n"] > 0 else "—"
            lines.append(f"| {name} | {tag} | {s['n']} | {win_str} | {avg_str} | {kept} |")
        lines.append("|  |  |  |  |  |  |")

    lines.append("\n## Period breakdown (BASE vs F1)")
    for name, hold, sb, sf1, sf2, sf12 in results:
        lines.append(f"\n### {name}")
        for label, s in [("BASE", sb), ("F1", sf1), ("F2", sf2), ("F1+F2", sf12)]:
            if s["n"] == 0:
                lines.append(f"  {label}: n=0")
                continue
            p_str = "  ".join(f"{p}: n={v['n']} win={v['win_pct']}% avg={v['avg']:+.4f}%"
                               for p, v in s.get("periods", {}).items())
            lines.append(f"  {label}: n={s['n']} win={s['win_pct']}% avg={s['avg_net']:+.4f}%")
            if p_str:
                lines.append(f"    [{p_str}]")

    lines.append("\n## Recommendation")
    lines.append("- F1 (SARA/PRV): best for mean-reversion (PAV, CRB)")
    lines.append("- F2 (Regime+Accel): best for momentum/streak (STRK, ZSCO)")
    lines.append("- F1+F2: strictest gate, highest quality, fewest trades")
    lines.append("\n_Past results are not advice._")

    report = "\n".join(lines)
    out_path = "/mnt/project-files/results_revolt_gate_test.md"
    with open(out_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to {out_path}")
    print("\n" + "\n".join(lines[:30]))

if __name__ == "__main__":
    run()
