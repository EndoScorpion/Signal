#!/usr/bin/env python3
"""Re-price MT4 Strategy Tester reports with FXOpen ECN commission.

FXOpen ECN charges commission per standard lot per side, tiered by account balance:
  < $1,000: $3.50 | $1,000-25,000: $2.50 | $25,000-250,000: $1.80 | > $250,000: $1.50
A closed trade pays it twice (open + close): cost = lots * rate * 2.
P/L is rebuilt from raw prices (EURUSD, $100,000 per lot); the tester's own commission and swap are excluded.
Mode "balance": the tier follows the running balance (as the report shows it).
Mode "fixed:<rate>": one rate for every trade (e.g. fixed:3.5 for an account under $1,000).
Mode "points:<p>": flat round-trip commission in points (1 point = $1 per lot on EURUSD), regardless of
balance or margin. DEFAULT is points:8 (owner's rule, 11 Oct 2026: assume 8 points max).
Leverage (1:500) only affects margin, not P/L, so it does not change these numbers.

Usage: python3 fx/commission.py OUT.json report1.htm [report2.htm ...]
"""
import json, re, sys, html, os

DEFAULT = 'points:8'
TIERS = [(1000, 3.50), (25000, 2.50), (250000, 1.80), (float('inf'), 1.50)]

def tier_rate(balance):
    for top, r in TIERS:
        if balance < top:
            return r

def strip(x):
    return html.unescape(re.sub(r'<[^>]+>', '', x)).strip()

def parse(path):
    s = open(path, encoding='latin-1').read()
    head = {}
    for k in ('Initial deposit', 'Spread', 'Total net profit', 'Total trades', 'Maximal drawdown'):
        m = re.search(re.escape(k) + r'</td>\s*<td[^>]*>([^<]*)', s)
        head[k] = m.group(1).strip() if m else None
    m = re.search(r'Period</td>\s*<td[^>]*>([^<]*)', s)
    head['Period'] = m.group(1).strip() if m else None
    m = re.search(r'<b>(Strong2010b_claude_b\d+\w*|[A-Za-z0-9_]+)</b>', s)
    rows = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', s, re.S):
        c = [strip(x) for x in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(c) >= 8 and c[0].isdigit() and re.match(r'\d{4}\.\d\d\.\d\d', c[1]):
            rows.append(c)
    return head, rows

def price(path, mode):
    head, rows = parse(path)
    dep = float(head['Initial deposit'])
    side = {}
    fill = {}
    trades = []
    for c in rows:
        typ, order, size = c[2], c[3], float(c[4])
        if typ in ('buy', 'sell', 'buy limit', 'buy stop', 'sell limit', 'sell stop'):
            side.setdefault(order, typ.split()[0])
        if typ in ('buy', 'sell'):
            fill[order] = (typ, float(c[5]))
        if len(c) >= 10 and c[8] != '':
            # The MT4 tester already deducts its own commission (~8 points) from the profit column,
            # so rebuild P/L from raw open/close prices and charge commission once here.
            s0, p0 = fill.get(order, (side.get(order, '?'), None))
            raw = (float(c[5]) - p0) * (1 if s0 == 'buy' else -1) * 100000 * size if p0 is not None else float(c[8])
            trades.append(dict(t=c[1], order=order, side=side.get(order, '?'), lots=size, gross=raw, report=float(c[8])))
    bal = dep; peak = dep; mdd = 0.0
    out = {'buy': [0, 0.0, 0.0, 0], 'sell': [0, 0.0, 0.0, 0]}  # n, gross, comm, wins net
    for tr in trades:
        if mode.startswith('points:'):
            comm = tr['lots'] * float(mode.split(':')[1])  # $1 per point per lot, round trip
        else:
            rate = tier_rate(bal) if mode == 'balance' else float(mode.split(':')[1])
            comm = tr['lots'] * rate * 2
        net = tr['gross'] - comm
        bal += net; peak = max(peak, bal); mdd = max(mdd, peak - bal)
        o = out.setdefault(tr['side'], [0, 0.0, 0.0, 0])
        o[0] += 1; o[1] += tr['gross']; o[2] += comm; o[3] += net > 0
    g = sum(v[1] for v in out.values()); cm = sum(v[2] for v in out.values()); n = sum(v[0] for v in out.values())
    return dict(report=os.path.basename(path), period=head['Period'], deposit=dep, spread=head['Spread'],
                mt4_net=float(head['Total net profit']), trades=n, lots_avg=round(sum(t['lots'] for t in trades) / n, 4) if n else 0,
                gross=round(g, 2), commission=round(cm, 2), net=round(g - cm, 2), max_dd=round(mdd, 2),
                by_side={k: dict(n=v[0], gross=round(v[1], 2), commission=round(v[2], 2), net=round(v[1] - v[2], 2),
                                 win_pct=round(100 * v[3] / v[0], 1) if v[0] else 0) for k, v in out.items() if v[0]})

if __name__ == '__main__':
    res = []
    for p in sys.argv[2:]:
        r = {'default8': price(p, DEFAULT), 'balance': price(p, 'balance'), 'under1k': price(p, 'fixed:3.5')}
        res.append(r)
        b, u = r['default8'], r['under1k']
        print(f"{b['report']:34s} n={b['trades']:5d} gross={b['gross']:9.2f} comm={b['commission']:8.2f} net={b['net']:9.2f} | <1k net={u['net']:9.2f} | "
              + ' '.join(f"{k}:{v['net']:.2f}" for k, v in b['by_side'].items()))
    json.dump(res, open(sys.argv[1], 'w'), indent=1)
