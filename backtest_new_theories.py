"""
Backtest: VQZ, VWD, MTF, ACG, RVL — EURUSD D1
Net of costs; survivor filter: n>=30, win%>=51, net-positive in >=2/3 periods.
Cost model: SPREAD=1pip, COMMISSION=0.00007, SLIPPAGE=0.00003 → RT=0.00020
"""
import csv, math, sys
from typing import List, Dict, Optional, Tuple

SPREAD_PIPS = 1.0
COMMISSION  = 0.00007
SLIPPAGE    = 0.00003
COST_RT     = (SPREAD_PIPS * 0.0001) + COMMISSION + SLIPPAGE  # 0.00020

DATA_PATH = "data/history/EURUSD.csv"

# Period boundaries
P1_START, P1_END = "2015-01-01", "2019-12-31"
P2_START, P2_END = "2020-01-01", "2022-12-31"
P3_START, P3_END = "2023-01-01", "2029-12-31"

def load_eurusd(path: str):
    bars = []
    with open(path) as f:
        lines = f.readlines()
    # Skip yfinance 3-row header (Price/Ticker/Date rows)
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and stripped[0].isdigit():
            start = i
            break
    for line in lines[start:]:
        parts = line.strip().split(',')
        if len(parts) < 6:
            continue
        try:
            date = parts[0]
            close = float(parts[1])
            high  = float(parts[2])
            low   = float(parts[3])
            open_ = float(parts[4])
            bars.append({'date': date, 'open': open_, 'high': high, 'low': low, 'close': close})
        except (ValueError, IndexError):
            continue
    return bars

def sma(data, n):
    r = [None] * len(data)
    for i in range(n - 1, len(data)):
        window = [x for x in data[i - n + 1:i + 1] if x is not None]
        if len(window) == n:
            r[i] = sum(window) / n
    return r

def stdev(data, n):
    r = [None] * len(data)
    for i in range(n - 1, len(data)):
        window = [x for x in data[i - n + 1:i + 1] if x is not None]
        if len(window) == n:
            mean = sum(window) / n
            r[i] = math.sqrt(sum((x - mean) ** 2 for x in window) / n)
    return r

def rsi(close, n=14):
    r = [None] * len(close)
    gains, losses = [], []
    for i in range(1, len(close)):
        d = close[i] - close[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    for i in range(n, len(close)):
        idx = i - 1  # offset into gains/losses
        ag = sum(gains[idx - n + 1:idx + 1]) / n
        al = sum(losses[idx - n + 1:idx + 1]) / n
        if al == 0:
            r[i] = 100.0
        else:
            rs = ag / al
            r[i] = 100 - (100 / (1 + rs))
    return r

def atr(bars, n=14):
    tr_list = [None]
    for i in range(1, len(bars)):
        h, l, pc = bars[i]['high'], bars[i]['low'], bars[i-1]['close']
        tr_list.append(max(h - l, abs(h - pc), abs(l - pc)))
    r = [None] * len(bars)
    for i in range(n, len(bars)):
        window = [x for x in tr_list[i - n + 1:i + 1] if x is not None]
        if len(window) == n:
            r[i] = sum(window) / n
    return r

def stoch(bars, k=14, d=3):
    """Returns %K values"""
    r = [None] * len(bars)
    for i in range(k - 1, len(bars)):
        hh = max(b['high'] for b in bars[i - k + 1:i + 1])
        ll = min(b['low'] for b in bars[i - k + 1:i + 1])
        if hh != ll:
            r[i] = 100 * (bars[i]['close'] - ll) / (hh - ll)
        else:
            r[i] = 50.0
    return r

def bb_bands(close, n=20, k=2.0):
    """Returns (mid, upper, lower, width) lists"""
    mid = sma(close, n)
    sd = stdev(close, n)
    upper = [mid[i] + k * sd[i] if mid[i] is not None else None for i in range(len(close))]
    lower = [mid[i] - k * sd[i] if mid[i] is not None else None for i in range(len(close))]
    width = [upper[i] - lower[i] if upper[i] is not None else None for i in range(len(close))]
    return mid, upper, lower, width

def percentile_rank(data, i, window=20):
    """Rank of data[i] within the prior `window` values (0-100)"""
    if i < window:
        return None
    hist = [x for x in data[i - window:i] if x is not None]
    if not hist:
        return None
    below = sum(1 for x in hist if x < data[i])
    return 100 * below / len(hist)

def run_backtest(signals, bars, hold, label) -> Dict:
    trades = []
    for idx in signals:
        if idx + hold >= len(bars):
            continue
        entry = bars[idx]['close']
        exit_ = bars[idx + hold]['close']
        ret = (exit_ - entry) / entry - COST_RT
        period = bars[idx]['date']
        trades.append({'ret': ret, 'date': period})
    if not trades:
        return {'label': label, 'n': 0, 'win_pct': 0, 'avg_net': 0,
                'p1': (0, 0), 'p2': (0, 0), 'p3': (0, 0), 'survivor': False}
    rets = [t['ret'] for t in trades]
    wins = sum(1 for r in rets if r > 0)
    n = len(rets)
    win_pct = 100 * wins / n
    avg_net = sum(rets) / n * 100

    def period_stats(s, e):
        pts = [t for t in trades if s <= t['date'] <= e]
        if not pts:
            return (0, 0)
        pr = [t['ret'] for t in pts]
        return (100 * sum(1 for r in pr if r > 0) / len(pr), sum(pr) / len(pr) * 100)

    p1 = period_stats(P1_START, P1_END)
    p2 = period_stats(P2_START, P2_END)
    p3 = period_stats(P3_START, P3_END)

    pos_periods = sum(1 for p in [p1, p2, p3] if p[1] > 0)
    survivor = (n >= 30 and win_pct >= 51 and pos_periods >= 2)
    return {
        'label': label, 'n': n, 'win_pct': round(win_pct, 1),
        'avg_net': round(avg_net, 4), 'p1': p1, 'p2': p2, 'p3': p3,
        'survivor': survivor, 'pos_periods': pos_periods
    }

# ─── Theory implementations ────────────────────────────────────────────────

def theory_VQZ(bars, pct_thresh=30, rsi_bars=2, hold=5, invert=False):
    """Volatility Squeeze + Momentum: BB width below Nth percentile AND expanding AND RSI rising."""
    close = [b['close'] for b in bars]
    _, _, _, width = bb_bands(close)
    r = rsi(close)
    signals = []
    for i in range(40, len(bars) - hold):
        if width[i] is None or r[i] is None:
            continue
        if width[i-1] is None:
            continue
        rank = percentile_rank(width, i, 20)
        if rank is None:
            continue
        expanding = width[i] > width[i-1]
        rsi_rising = all(
            r[i - j] is not None and r[i - j] > r[i - j - 1]
            for j in range(rsi_bars - 1, -1, -1)
            if r[i - j] is not None and r[i - j - 1] is not None
        )
        if not invert:
            if rank <= pct_thresh and expanding and rsi_rising:
                signals.append(i)
        else:
            if rank <= pct_thresh and expanding and not rsi_rising:
                signals.append(i)
    return signals

def theory_VWD(bars, threshold=0.005, hold=5, invert=False):
    """D1 adaptation: close deviates from SMA20 'fair value' + directional bar."""
    close = [b['close'] for b in bars]
    ma = sma(close, 20)
    signals = []
    for i in range(25, len(bars) - hold):
        if ma[i] is None:
            continue
        if not invert:
            # LONG: close significantly below SMA20 + bullish bar
            if close[i] < ma[i] * (1 - threshold) and bars[i]['close'] > bars[i]['open']:
                signals.append(i)
        else:
            # SHORT: close above SMA20 + bearish bar
            if close[i] > ma[i] * (1 + threshold) and bars[i]['close'] < bars[i]['open']:
                signals.append(i)
    return signals

def theory_MTF(bars, rsi_thresh=35, sma_n=50, hold=5, use_stoch=False, invert=False):
    """Multi-timeframe: oversold on RSI/Stoch AND above weekly trend (SMA50 on D1)."""
    close = [b['close'] for b in bars]
    r = rsi(close)
    ma = sma(close, sma_n)
    sk = stoch(bars)
    signals = []
    for i in range(sma_n + 5, len(bars) - hold):
        if ma[i] is None:
            continue
        if not use_stoch:
            osc_signal = (r[i] is not None and r[i] < rsi_thresh)
        else:
            # Stoch cross up from <20
            osc_signal = (
                sk[i] is not None and sk[i-1] is not None and
                sk[i-1] < 20 and sk[i] > sk[i-1]
            )
        in_uptrend = close[i] > ma[i]
        if not invert:
            if osc_signal and in_uptrend:
                signals.append(i)
        else:
            osc_over = (r[i] is not None and r[i] > (100 - rsi_thresh))
            if osc_over and not in_uptrend:
                signals.append(i)
    return signals

def theory_ACG(bars, atr_mult=5.0, hold=5, invert=False):
    """Adaptive Cost Gate + BB: price at/below lower BB AND ATR is high enough vs cost."""
    close = [b['close'] for b in bars]
    _, _, lower, _ = bb_bands(close)
    at = atr(bars)
    signals = []
    for i in range(25, len(bars) - hold):
        if lower[i] is None or at[i] is None:
            continue
        atr_pct = at[i] / close[i]
        cost_gate = atr_pct > (atr_mult * COST_RT)
        if not invert:
            if close[i] <= lower[i] and cost_gate:
                signals.append(i)
        else:
            _, upper, _, _ = bb_bands(close)
            if upper[i] is not None and close[i] >= upper[i] and cost_gate:
                signals.append(i)
    return signals

def theory_RVL(bars, range_mult=1.5, close_zone='upper', hold=5, require_expansion=False):
    """Range Volume-Like: high-range bar with close in specified zone."""
    ranges = [b['high'] - b['low'] for b in bars]
    avg_range = sma(ranges, 20)
    signals = []
    for i in range(25, len(bars) - hold):
        if avg_range[i] is None or avg_range[i] == 0:
            continue
        cur_range = ranges[i]
        if cur_range < range_mult * avg_range[i]:
            continue
        if require_expansion and avg_range[i-1] is not None:
            if ranges[i-1] > 0.8 * avg_range[i]:  # previous bar was NOT low-vol
                continue
        # close position within bar
        rng = bars[i]['high'] - bars[i]['low']
        if rng == 0:
            continue
        pos = (bars[i]['close'] - bars[i]['low']) / rng  # 0=bottom, 1=top
        if close_zone == 'upper' and pos >= 0.6:  # upper 40%
            signals.append(i)
        elif close_zone == 'lower' and pos <= 0.4:  # lower 40%
            signals.append(i)
        elif close_zone == 'any':
            signals.append(i)
    return signals

def main():
    bars = load_eurusd(DATA_PATH)
    print(f"Loaded {len(bars)} bars: {bars[0]['date']} → {bars[-1]['date']}")

    results = []

    # ── VQZ ──────────────────────────────────────────────────────────────────
    for pct, rb, hold, tag in [
        (30, 2, 5, 'VQZ-1'), (25, 2, 5, 'VQZ-2'), (30, 3, 5, 'VQZ-3'),
        (35, 2, 3, 'VQZ-4'), (30, 2, 5, 'VQZ-1-INV'),
    ]:
        inv = tag.endswith('INV')
        sig = theory_VQZ(bars, pct_thresh=pct, rsi_bars=rb, hold=hold, invert=inv)
        results.append(run_backtest(sig, bars, hold, tag))

    # ── VWD ──────────────────────────────────────────────────────────────────
    for thresh, hold, tag in [
        (0.005, 5, 'VWD-1'), (0.003, 5, 'VWD-2'), (0.007, 5, 'VWD-3'),
        (0.004, 3, 'VWD-4'), (0.005, 5, 'VWD-1-INV'),
    ]:
        inv = tag.endswith('INV')
        sig = theory_VWD(bars, threshold=thresh, hold=hold, invert=inv)
        results.append(run_backtest(sig, bars, hold, tag))

    # ── MTF ──────────────────────────────────────────────────────────────────
    for rsi_th, sma_n, hold, stoch_, tag in [
        (35, 50, 5, False, 'MTF-1'), (30, 50, 5, False, 'MTF-2'),
        (35, 50, 5, True,  'MTF-3'), (40, 200, 5, False, 'MTF-4'),
        (35, 50, 5, False, 'MTF-1-INV'),
    ]:
        inv = tag.endswith('INV')
        sig = theory_MTF(bars, rsi_thresh=rsi_th, sma_n=sma_n, hold=hold,
                         use_stoch=stoch_, invert=inv)
        results.append(run_backtest(sig, bars, hold, tag))

    # ── ACG ──────────────────────────────────────────────────────────────────
    for mult, hold, tag in [
        (5.0, 5, 'ACG-1'), (7.5, 5, 'ACG-2'), (3.0, 5, 'ACG-3'),
        (5.0, 3, 'ACG-4'), (5.0, 5, 'ACG-1-INV'),
    ]:
        inv = tag.endswith('INV')
        sig = theory_ACG(bars, atr_mult=mult, hold=hold, invert=inv)
        results.append(run_backtest(sig, bars, hold, tag))

    # ── RVL ──────────────────────────────────────────────────────────────────
    for mult, zone, exp, hold, tag in [
        (1.5, 'upper', False, 5, 'RVL-1'), (2.0, 'upper', False, 5, 'RVL-2'),
        (1.5, 'lower', False, 5, 'RVL-3'), (1.5, 'upper', True,  5, 'RVL-4'),
        (1.5, 'any',   False, 5, 'RVL-5'),
    ]:
        sig = theory_RVL(bars, range_mult=mult, close_zone=zone,
                         hold=hold, require_expansion=exp)
        results.append(run_backtest(sig, bars, hold, tag))

    # ── Report ────────────────────────────────────────────────────────────────
    survivors = [r for r in results if r['survivor']]

    print("\n=== ALL RESULTS ===")
    print(f"{'Label':<18} {'n':>5} {'Win%':>6} {'AvgNet%':>9} {'P1':>8} {'P2':>8} {'P3':>8} {'Surv'}")
    for r in sorted(results, key=lambda x: -x['avg_net']):
        print(f"{r['label']:<18} {r['n']:>5} {r['win_pct']:>6.1f} {r['avg_net']:>9.4f} "
              f"{r['p1'][1]:>8.4f} {r['p2'][1]:>8.4f} {r['p3'][1]:>8.4f} "
              f"{'YES' if r['survivor'] else 'no'}")

    print(f"\n=== SURVIVORS ({len(survivors)}) ===")
    for r in survivors:
        print(f"  {r['label']}: n={r['n']}, win={r['win_pct']}%, avg={r['avg_net']:+.4f}%, "
              f"pos_periods={r['pos_periods']}/3")

    return survivors, results

if __name__ == '__main__':
    survivors, results = main()
