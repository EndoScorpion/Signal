#!/usr/bin/env python3
"""
oos_check.py  --  MT4 detailed backtest HTML report OOS analyser.

Usage:
    python analysis/oos_check.py <report.htm> [--deposit N] [--commission N]

Arguments:
    report.htm       Path to MT4 Strategy Tester detailed HTML report.
    --deposit N      Starting balance used for max-DD % calculation
                     (default: 10000).
    --commission N   Commission in POINTS per trade (default: 6); deducts
                     N * 1.00 * lots dollars from every trade's profit
                     (1 point = $1 per 1.00 lot, so 6 pt at 0.01 lots = $0.06).
                     FIXED 12 Oct 2026: old formula N*0.10*lots was 10x too low.

PASS criteria: estimated PF >= 1.10  AND  max closed-trade DD <= 5 % of deposit.
Exit codes:  0 = PASS,  1 = FAIL or error.

Parse logic
-----------
Open rows  : 10 expanded cells, type exactly 'sell' or 'buy'.
Close rows : 10 expanded cells, type in {'t/p', 's/l', 'close'}.
Match by order number (column index 3).
Open-row time supplies the trade's hour and weekday.
Close-row column 8 is the raw profit.
"""

import sys
import argparse
from html.parser import HTMLParser
from collections import defaultdict
from datetime import datetime


# ---------------------------------------------------------------------------
# HTML row parser
# ---------------------------------------------------------------------------

class RowParser(HTMLParser):
    """Collect every <tr> as a list of plain-text cell strings.

    colspan > 1 is expanded into multiple empty strings so that
    all rows share the same column indices.
    """

    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell = None
        self._span = 1

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'tr':
            self._row = []
        elif tag == 'td' and self._row is not None:
            self._cell = []
            try:
                self._span = int(a.get('colspan', 1))
            except (TypeError, ValueError):
                self._span = 1

    def handle_endtag(self, tag):
        if tag == 'td' and self._cell is not None:
            self._row.append(''.join(self._cell).strip())
            for _ in range(self._span - 1):
                self._row.append('')
            self._cell = None
        elif tag == 'tr' and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _float(s):
    """Parse float, returning None on failure."""
    try:
        return float(s.replace(',', '').strip())
    except (ValueError, AttributeError):
        return None


def _parse_dt(s):
    """Parse MT4 datetime string 'YYYY.MM.DD HH:MM'."""
    try:
        return datetime.strptime(s.strip(), '%Y.%m.%d %H:%M')
    except ValueError:
        return None


DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
             'Friday', 'Saturday', 'Sunday']

WARN_SUFFIX = '  <-- WARN'

CLOSE_TYPES = frozenset(('t/p', 's/l', 'close'))
OPEN_TYPES  = frozenset(('sell', 'buy'))


# ---------------------------------------------------------------------------
# Core parser
# ---------------------------------------------------------------------------

def parse_report(filepath, commission_n):
    """Return (trades, initial_deposit).

    Each trade is a dict:
        open_time  : datetime  (from the execution / open row)
        lots       : float
        raw_profit : float     (profit as reported in the HTML)
        profit     : float     (raw_profit minus commission)
    """
    with open(filepath, encoding='utf-8', errors='replace') as fh:
        html = fh.read()

    p = RowParser()
    p.feed(html)

    # Grab initial deposit from the summary section
    initial_deposit = 10000.0
    for row in p.rows:
        if len(row) >= 2 and 'Initial deposit' in row[0]:
            v = _float(row[1])
            if v is not None:
                initial_deposit = v
            break

    opens  = {}   # order_str -> (datetime, lots)
    trades = []

    for row in p.rows:
        if len(row) < 9:
            continue

        rtype = row[2].lower().strip()
        order = row[3].strip()

        if rtype in OPEN_TYPES:
            dt   = _parse_dt(row[1])
            lots = _float(row[4])
            if dt is not None and lots is not None and order:
                opens[order] = (dt, lots)

        elif rtype in CLOSE_TYPES:
            if len(row) < 10:
                continue
            raw_profit = _float(row[8])
            lots_close = _float(row[4])
            if raw_profit is None or lots_close is None:
                continue
            if order not in opens:
                continue
            open_dt, open_lots = opens.pop(order)
            commission = commission_n * 1.00 * open_lots
            trades.append({
                'order':      order,
                'open_time':  open_dt,
                'lots':       open_lots,
                'raw_profit': raw_profit,
                'profit':     raw_profit - commission,
            })

    return trades, initial_deposit


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def max_closed_dd(trades, deposit):
    """Max drawdown from peak closed-trade balance, in $ and %."""
    peak    = deposit
    balance = deposit
    max_dd      = 0.0
    max_dd_pct  = 0.0
    for t in sorted(trades, key=lambda x: x['open_time']):
        balance += t['profit']
        if balance > peak:
            peak = balance
        dd     = peak - balance
        dd_pct = dd / peak * 100.0 if peak > 0 else 0.0
        if dd > max_dd:
            max_dd     = dd
            max_dd_pct = dd_pct
    return max_dd, max_dd_pct


def bucket_stats(trades, key_fn):
    """Group trades by key_fn(trade) and return dict of bucket stats."""
    buckets = {}
    for t in trades:
        k = key_fn(t)
        if k not in buckets:
            buckets[k] = {'n': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}
        b = buckets[k]
        b['n']   += 1
        b['pnl'] += t['profit']
        if t['profit'] > 0:
            b['wins']   += 1
        else:
            b['losses'] += 1
    return buckets


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description='Analyse an MT4 detailed backtest HTML report.')
    ap.add_argument('report',
                    help='Path to MT4 Strategy Tester HTML report')
    ap.add_argument('--deposit', type=float, default=10000.0,
                    help='Starting deposit in $ for DD%% calculation (default: 10000)')
    ap.add_argument('--commission', type=float, default=6.0,
                    help='Commission in points N; deducts N*1.00*lots dollars per trade (default: 6)')
    args = ap.parse_args()

    trades, detected_deposit = parse_report(args.report, args.commission)
    deposit = args.deposit

    if not trades:
        print('ERROR: no completed trades found.')
        sys.exit(1)

    # -- Summary stats -------------------------------------------------------
    total    = len(trades)
    wins_tr  = [t for t in trades if t['profit'] > 0]
    loss_tr  = [t for t in trades if t['profit'] <= 0]
    n_wins   = len(wins_tr)
    n_losses = len(loss_tr)
    win_pct  = n_wins / total * 100.0 if total else 0.0

    gross_profit = sum(t['profit'] for t in wins_tr)
    gross_loss   = sum(t['profit'] for t in loss_tr)
    net_pnl      = gross_profit + gross_loss

    avg_win  = gross_profit / n_wins   if n_wins   else 0.0
    avg_loss = abs(gross_loss) / n_losses if n_losses else 0.0
    pf_est   = (n_wins * avg_win) / (n_losses * avg_loss) \
               if (n_losses > 0 and avg_loss > 0) else float('inf')

    max_dd_usd, max_dd_pct = max_closed_dd(trades, deposit)

    comm_ex = args.commission * 1.00 * 0.01   # example at 0.01 lots

    print('=' * 62)
    print('SUMMARY STATS')
    print('=' * 62)
    print('  Total trades      : %d' % total)
    print('  Win rate          : %.1f%%  (%dW / %dL)' % (win_pct, n_wins, n_losses))
    print('  Gross profit      : $%10.2f' % gross_profit)
    print('  Gross loss        : $%10.2f' % gross_loss)
    print('  Net PnL           : $%10.2f' % net_pnl)
    print('  PF estimate       : %.3f' % pf_est)
    print('  Avg win           : $%8.2f' % avg_win)
    print('  Avg loss          : $%8.2f' % avg_loss)
    print('  Max closed-DD     : $%8.2f  (%.2f%% of $%.0f deposit)' % (
          max_dd_usd, max_dd_pct, deposit))
    print('  Commission/trade  : $%.4f  (at 0.01 lots, N=%.0f)' % (
          comm_ex, args.commission))

    # -- Hourly breakdown ----------------------------------------------------
    hour_data = bucket_stats(trades, lambda t: t['open_time'].hour)
    print()
    print('=' * 62)
    print('HOURLY BREAKDOWN')
    print('=' * 62)
    print('  %4s  %6s  %5s  %6s  %6s  %9s' % (
          'Hour', 'Trades', 'Wins', 'Losses', 'WR%', 'Net PnL'))
    print('  ' + '-' * 44)
    for h in range(24):
        b = hour_data.get(h)
        if b is None:
            continue
        wr   = b['wins'] / b['n'] * 100.0 if b['n'] else 0.0
        flag = b['n'] > 0 and (wr < 50.0 or b['pnl'] < 0.0)
        line = '  %4d  %6d  %5d  %6d  %5.1f%%  %+9.2f' % (
               h, b['n'], b['wins'], b['losses'], wr, b['pnl'])
        if flag:
            line += WARN_SUFFIX
        print(line)

    # -- Daily breakdown -----------------------------------------------------
    day_data = bucket_stats(trades, lambda t: t['open_time'].weekday())
    print()
    print('=' * 62)
    print('DAILY BREAKDOWN')
    print('=' * 62)
    print('  %-11s  %6s  %5s  %6s  %6s  %9s' % (
          'Day', 'Trades', 'Wins', 'Losses', 'WR%', 'Net PnL'))
    print('  ' + '-' * 47)
    for d in range(7):
        b = day_data.get(d)
        if b is None:
            continue
        wr   = b['wins'] / b['n'] * 100.0 if b['n'] else 0.0
        flag = b['n'] > 0 and (wr < 50.0 or b['pnl'] < 0.0)
        line = '  %-11s  %6d  %5d  %6d  %5.1f%%  %+9.2f' % (
               DAY_NAMES[d], b['n'], b['wins'], b['losses'], wr, b['pnl'])
        if flag:
            line += WARN_SUFFIX
        print(line)

    # -- Verdict -------------------------------------------------------------
    pf_ok = pf_est >= 1.10
    dd_ok = max_dd_pct <= 5.0

    print()
    print('=' * 62)
    print('VERDICT')
    print('=' * 62)
    print('  PF >= 1.10   : %.3f  [%s]' % (pf_est,   'OK' if pf_ok else 'FAIL'))
    print('  Max DD <= 5%% : %.2f%%  [%s]' % (max_dd_pct, 'OK' if dd_ok else 'FAIL'))
    print()
    if pf_ok and dd_ok:
        print('  *** PASS ***')
        sys.exit(0)
    else:
        print('  *** FAIL ***')
        sys.exit(1)


if __name__ == '__main__':
    main()
