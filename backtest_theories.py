#!/usr/bin/env python3
"""
Theory backtester: GAP, CRB, PBR, PAV families
EURUSD D1, net of costs (spread + commission)
"""
import csv, math, sys
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# ---- Cost model (from cost_model.json equiv, EURUSD D1) ----
SPREAD_PIPS   = 1.0    # typical EURUSD ECN spread pips
COMMISSION    = 0.00007  # ~0.7 pips per side round-trip in price terms
SLIPPAGE      = 0.00003  # 0.3 pips
COST_RT       = (SPREAD_PIPS * 0.0001) + COMMISSION + SLIPPAGE  # round-trip cost

@dataclass
class Bar:
    date: str
    o: float; h: float; l: float; c: float; v: float

def load_eurusd(path: str) -> List[Bar]:
    bars = []
    with open(path) as f:
        lines = f.readlines()
    # yfinance multi-header: skip first 3 rows
    # Price, Close, High, Low, Open, Volume
    for line in lines[3:]:
        parts = line.strip().split(',')
        if len(parts) < 6: continue
        try:
            date, c, h, l, o, v = parts[0], float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5]) if parts[5] else 0
            if c > 0:
                bars.append(Bar(date, o, h, l, c, v))
        except:
            pass
    return bars

def ema(data: List[float], n: int) -> List[float]:
    result = [None]*len(data)
    if len(data) < n: return result
    result[n-1] = sum(data[:n])/n
    k = 2/(n+1)
    for i in range(n, len(data)):
        result[i] = data[i]*k + result[i-1]*(1-k)
    return result

def sma(data: List[float], n: int) -> List[float]:
    result = [None]*len(data)
    for i in range(n-1, len(data)):
        result[i] = sum(data[i-n+1:i+1])/n
    return result

def stdev(data: List[float], n: int) -> List[float]:
    result = [None]*len(data)
    for i in range(n-1, len(data)):
        s = data[i-n+1:i+1]
        m = sum(s)/n
        result[i] = math.sqrt(sum((x-m)**2 for x in s)/n)
    return result

def atr(bars: List[Bar], n: int) -> List[Optional[float]]:
    trs = [None]
    for i in range(1, len(bars)):
        tr = max(bars[i].h - bars[i].l,
                 abs(bars[i].h - bars[i-1].c),
                 abs(bars[i].l - bars[i-1].c))
        trs.append(tr)
    result = [None]*len(bars)
    if len(bars) >= n+1:
        result[n] = sum(trs[1:n+1])/n
        for i in range(n+1, len(bars)):
            result[i] = (result[i-1]*(n-1) + trs[i])/n
    return result

def rsi(closes: List[float], n: int=14) -> List[Optional[float]]:
    result = [None]*len(closes)
    if len(closes) < n+1: return result
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d,0)); losses.append(max(-d,0))
    ag = sum(gains[:n])/n; al = sum(losses[:n])/n
    def rs2rsi(ag,al): return 100 - 100/(1+ag/al) if al>0 else 100
    result[n] = rs2rsi(ag, al)
    for i in range(n, len(gains)):
        ag = (ag*(n-1)+gains[i])/n; al = (al*(n-1)+losses[i])/n
        result[i+1] = rs2rsi(ag, al)
    return result

def period_tag(date: str) -> str:
    y = int(date[:4])
    if 2015 <= y <= 2019: return 'P1'
    if 2020 <= y <= 2022: return 'P2'
    if 2023 <= y <= 2026: return 'P3'
    return 'P0'

def run_backtest(signals: List[Tuple], bars: List[Bar], hold: int, label: str) -> Dict:
    """signals: list of (entry_idx, direction, entry_price)"""
    trades = []; period_stats = {'P1':[], 'P2':[], 'P3':[]}
    for idx, direction, entry in signals:
        exit_idx = min(idx + hold, len(bars)-1)
        exit_price = bars[exit_idx].c
        raw = (exit_price - entry)/entry * direction
        net = raw - COST_RT/entry  # normalize by entry
        # simpler: net in price terms
        net_price = (exit_price - entry)*direction - COST_RT
        net_pct = net_price / entry * 100
        trades.append(net_pct)
        p = period_tag(bars[idx].date)
        if p != 'P0': period_stats[p].append(net_pct)

    if not trades:
        return {'label':label,'n':0,'win_pct':0,'avg_net_pct':0,'periods':{}}

    wins = sum(1 for t in trades if t > 0)
    per = {}
    for p, ts in period_stats.items():
        if ts:
            per[p] = {'n':len(ts),'win_pct':sum(1 for t in ts if t>0)/len(ts)*100,'avg':sum(ts)/len(ts)}

    return {
        'label': label,
        'n': len(trades),
        'win_pct': wins/len(trades)*100,
        'avg_net_pct': sum(trades)/len(trades),
        'periods': per
    }

# ===================== THEORY FAMILIES =====================

def theory_GAP(bars: List[Bar], threshold: float=0.005, hold: int=5, invert: bool=False) -> List[Tuple]:
    """Gap-up >= threshold vs prior close that closes below open -> fill short"""
    signals = []
    for i in range(1, len(bars)):
        gap = (bars[i].o - bars[i-1].c) / bars[i-1].c
        if gap >= threshold and bars[i].c < bars[i].o:
            direction = -1 if not invert else 1
            signals.append((i, direction, bars[i].c))
    return signals

def theory_CRB(bars: List[Bar], bb_n: int=20, bb_k: float=2.0, hold: int=5, invert: bool=False) -> List[Tuple]:
    """2 bars below lower BB then closes back above with green bar -> exhaustion bounce long"""
    closes = [b.c for b in bars]
    ma = sma(closes, bb_n)
    sd = stdev(closes, bb_n)
    signals = []
    for i in range(bb_n+2, len(bars)):
        if ma[i] is None or sd[i] is None: continue
        lb = ma[i] - bb_k*sd[i]
        lb1 = ma[i-1] - bb_k*sd[i-1] if sd[i-1] else lb
        lb2 = ma[i-2] - bb_k*sd[i-2] if sd[i-2] else lb
        if (bars[i-2].c < lb2 and bars[i-1].c < lb1 and
            bars[i].c > lb and bars[i].c > bars[i].o):  # green recovery bar
            direction = 1 if not invert else -1
            signals.append((i, direction, bars[i].c))
    return signals

def theory_PBR(bars: List[Bar], ema_n: int=21, hold: int=5, invert: bool=False) -> List[Tuple]:
    """Price dips below EMA for 2 bars then crosses back above -> trend continuation long"""
    closes = [b.c for b in bars]
    em = ema(closes, ema_n)
    signals = []
    for i in range(ema_n+2, len(bars)):
        if em[i] is None or em[i-1] is None or em[i-2] is None: continue
        if (bars[i-2].c < em[i-2] and bars[i-1].c < em[i-1] and bars[i].c > em[i]):
            direction = 1 if not invert else -1
            signals.append((i, direction, bars[i].c))
    return signals

def theory_PAV(bars: List[Bar], rsi_thresh: float=40, atr_min: float=1.0, atr_max: float=4.0, hold: int=5, invert: bool=False) -> List[Tuple]:
    """Fractal pivot swing low + RSI<40, swing height 1-4x ATR -> long"""
    closes = [b.c for b in bars]
    rs = rsi(closes, 14)
    at = atr(bars, 14)
    signals = []
    for i in range(16, len(bars)-1):
        if rs[i] is None or at[i] is None or at[i] == 0: continue
        # confirmed swing low: bar[i-1].l < neighbors
        if (bars[i-1].l < bars[i-2].l and bars[i-1].l < bars[i].l and
            rs[i] < rsi_thresh):
            swing_h = bars[i].h - bars[i-1].l
            atr_ratio = swing_h / at[i]
            if atr_min <= atr_ratio <= atr_max:
                direction = 1 if not invert else -1
                signals.append((i, direction, bars[i].c))
    return signals

# ===================== HIGH-LYA WINDOWS =====================
def high_lya_mask(bars: List[Bar], window: int=50, top_pct: float=0.3) -> List[bool]:
    """Flag bars in top 30% of realized volatility windows"""
    closes = [b.c for b in bars]
    vols = []
    for i in range(window, len(bars)):
        s = closes[i-window:i]
        rets = [(s[j]-s[j-1])/s[j-1] for j in range(1,len(s))]
        vols.append(math.sqrt(sum(r*r for r in rets)/(len(rets)-1)) if len(rets)>1 else 0)
    if not vols: return [False]*len(bars)
    thresh = sorted(vols)[int(len(vols)*(1-top_pct))]
    mask = [False]*window
    for v in vols:
        mask.append(v >= thresh)
    return mask

def run_in_lya(bars: List[Bar], signals: List[Tuple], hold: int, label: str) -> Dict:
    mask = high_lya_mask(bars)
    lya_signals = [(i,d,e) for i,d,e in signals if i < len(mask) and mask[i]]
    return run_backtest(lya_signals, bars, hold, label + '_LYA')

def fmt_result(r: Dict) -> str:
    if r['n'] == 0: return f"  {r['label']}: n=0 (no signals)"
    p_str = '  '.join(
        f"{k}: n={v['n']} win={v['win_pct']:.1f}% avg={v['avg']:.4f}%"
        for k,v in sorted(r['periods'].items()) if v['n']>=5
    )
    flag = " *** NET POSITIVE ***" if r['win_pct']>=51 and r['n']>=30 else ""
    return (f"  {r['label']}: n={r['n']} win={r['win_pct']:.1f}% avg_net={r['avg_net_pct']:.4f}%{flag}\n"
            f"    [{p_str}]")

def main():
    bars = load_eurusd('/home/user/Signal/data/history/EURUSD.csv')
    print(f"Loaded {len(bars)} EURUSD D1 bars ({bars[0].date} - {bars[-1].date})")

    results_text = f"# Theory Test Results — GAP CRB PBR PAV\nEURUSD D1 · {bars[0].date} to {bars[-1].date} · n={len(bars)} bars\nCost RT: {COST_RT:.5f} ({COST_RT*10000:.1f} pips)\n\n"
    all_results = []

    # -------- GAP --------
    results_text += "## GAP — Gap-up gap-fill short\n"
    for thresh, hold in [(0.003, 3), (0.005, 5), (0.008, 7)]:
        for inv, tag in [(False,''), (True,'_INV')]:
            sig = theory_GAP(bars, threshold=thresh, hold=hold, invert=inv)
            r = run_backtest(sig, bars, hold, f"GAP_t{int(thresh*1000)}h{hold}{tag}")
            results_text += fmt_result(r) + "\n"
            all_results.append(r)
            if not inv:
                r2 = run_in_lya(bars, sig, hold, f"GAP_t{int(thresh*1000)}h{hold}")
                results_text += fmt_result(r2) + "\n"
                all_results.append(r2)
    # autopsy: GAP is rare on D1 FX (small gaps at open)
    results_text += "  _Autopsy: FX D1 gaps at open are small; threshold 0.3-0.5% rarely triggers. Adapted: GAP_MICRO (0.1% threshold)_\n"
    sig = theory_GAP(bars, threshold=0.001, hold=3)
    r = run_backtest(sig, bars, 3, "GAP_MICRO_t1h3")
    results_text += fmt_result(r) + "\n"
    all_results.append(r)

    # -------- CRB --------
    results_text += "\n## CRB — Double-dip below lower BB exhaustion bounce\n"
    for bb_n, bb_k, hold in [(20,2.0,5), (20,1.5,3), (14,2.0,4)]:
        for inv, tag in [(False,''), (True,'_INV')]:
            sig = theory_CRB(bars, bb_n=bb_n, bb_k=bb_k, hold=hold, invert=inv)
            r = run_backtest(sig, bars, hold, f"CRB_n{bb_n}k{int(bb_k*10)}h{hold}{tag}")
            results_text += fmt_result(r) + "\n"
            all_results.append(r)
            if not inv:
                r2 = run_in_lya(bars, sig, hold, f"CRB_n{bb_n}k{int(bb_k*10)}h{hold}")
                results_text += fmt_result(r2) + "\n"
                all_results.append(r2)
    results_text += "  _Autopsy: CRB signals cluster at trend reversals; inverted (short after double-dip) may capture trend continuation failures_\n"
    sig_a = theory_CRB(bars, bb_n=20, bb_k=1.8, hold=4)
    r_a = run_backtest(sig_a, bars, 4, "CRB_ADAPTED_n20k18h4")
    results_text += fmt_result(r_a) + "\n"
    all_results.append(r_a)

    # -------- PBR --------
    results_text += "\n## PBR — EMA dip-cross trend continuation\n"
    for ema_n, hold in [(21,5), (50,7), (14,3)]:
        for inv, tag in [(False,''), (True,'_INV')]:
            sig = theory_PBR(bars, ema_n=ema_n, hold=hold, invert=inv)
            r = run_backtest(sig, bars, hold, f"PBR_e{ema_n}h{hold}{tag}")
            results_text += fmt_result(r) + "\n"
            all_results.append(r)
            if not inv:
                r2 = run_in_lya(bars, sig, hold, f"PBR_e{ema_n}h{hold}")
                results_text += fmt_result(r2) + "\n"
                all_results.append(r2)
    results_text += "  _Autopsy: EMA pullback quality improves with trend filter; adapted version adds 200EMA trend guard_\n"
    # adapted: only trade when close > EMA(200) (uptrend)
    closes = [b.c for b in bars]
    em200 = ema(closes, 200)
    sig_pbr_trend = []
    base_sigs = theory_PBR(bars, ema_n=21, hold=5)
    for i, d, e in base_sigs:
        if em200[i] and bars[i].c > em200[i]:
            sig_pbr_trend.append((i, d, e))
    r_a = run_backtest(sig_pbr_trend, bars, 5, "PBR_ADAPTED_e21h5_trend200")
    results_text += fmt_result(r_a) + "\n"
    all_results.append(r_a)

    # -------- PAV --------
    results_text += "\n## PAV — Fractal pivot + RSI + ATR kinematic entry\n"
    for rsi_t, atr_min, atr_max, hold in [(40,1,4,5), (35,0.5,3,4), (45,1.5,5,6)]:
        for inv, tag in [(False,''), (True,'_INV')]:
            sig = theory_PAV(bars, rsi_thresh=rsi_t, atr_min=atr_min, atr_max=atr_max, hold=hold, invert=inv)
            r = run_backtest(sig, bars, hold, f"PAV_r{rsi_t}a{int(atr_min*10)}-{int(atr_max*10)}h{hold}{tag}")
            results_text += fmt_result(r) + "\n"
            all_results.append(r)
            if not inv:
                r2 = run_in_lya(bars, sig, hold, f"PAV_r{rsi_t}a{int(atr_min*10)}-{int(atr_max*10)}h{hold}")
                results_text += fmt_result(r2) + "\n"
                all_results.append(r2)
    results_text += "  _Autopsy: PAV swing-low quality varies; adapted adds volume confirmation (close vol > 5d avg vol)_\n"
    vols = [b.v for b in bars]
    vol_ma5 = sma(vols, 5)
    base_pav = theory_PAV(bars, rsi_thresh=40, atr_min=1, atr_max=4, hold=5)
    sig_pav_vol = [(i,d,e) for i,d,e in base_pav
                   if vol_ma5[i] and bars[i].v > vol_ma5[i]]
    r_a = run_backtest(sig_pav_vol, bars, 5, "PAV_ADAPTED_vol_r40")
    results_text += fmt_result(r_a) + "\n"
    all_results.append(r_a)

    # ---- SURVIVORS ----
    survivors = [r for r in all_results if r['n']>=30 and r['win_pct']>=51]
    # check period consistency: >=2 of 3 periods positive
    def period_positive_count(r):
        return sum(1 for p,v in r['periods'].items() if v.get('avg',0) > 0 and v.get('n',0)>=5)

    survivors = [r for r in survivors if period_positive_count(r) >= 2]

    results_text += "\n## SURVIVORS (n>=30, win>=51%, net positive in >=2/3 periods)\n"
    if survivors:
        for r in sorted(survivors, key=lambda x: -x['win_pct']):
            results_text += fmt_result(r) + "\n"
    else:
        results_text += "  None passed all filters on this dataset.\n"

    # ---- LEADERBOARD ----
    top10 = sorted([r for r in all_results if r['n']>=10],
                   key=lambda x: (x['win_pct'] - 50) * math.log(max(x['n'],1)),
                   reverse=True)[:10]
    results_text += "\n## LEADERBOARD (top 10 by win% × log(n))\n"
    results_text += "| Rank | Strategy | n | Win% | Avg Net% |\n|------|----------|---|------|----------|\n"
    for i, r in enumerate(top10, 1):
        results_text += f"| {i} | {r['label']} | {r['n']} | {r['win_pct']:.1f}% | {r['avg_net_pct']:.4f}% |\n"

    results_text += "\n---\n_Data: EURUSD D1 2003-2026 via yfinance. Cost RT = 1.0 pip spread + 0.7 pip commission + 0.3 pip slippage. Past results are not advice._\n"

    with open('/mnt/project-files/results_thread2.md', 'w') as f:
        f.write(results_text)
    print(results_text)

    # print survivors for immediate reporting
    print("\n=== SURVIVORS FOR CHAT ===")
    for r in survivors:
        print(f"  {r['label']}: win={r['win_pct']:.1f}% avg={r['avg_net_pct']:.4f}% n={r['n']}")
    if not survivors:
        print("  None")
    print("\n=== TOP 3 LEADERBOARD ===")
    for i,r in enumerate(top10[:3],1):
        print(f"  {i}. {r['label']}: win={r['win_pct']:.1f}% n={r['n']} avg={r['avg_net_pct']:.4f}%")

if __name__ == '__main__':
    main()
