#!/usr/bin/env python3
"""Commission point lookup: net result per report at 5, 8, 10, 15 points (8 = default).
Usage: python3 fx/commission_table.py OUT_PREFIX report1.htm [...]  -> OUT_PREFIX.json + OUT_PREFIX.md"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import commission as c

POINTS = [8, 5, 10, 15]  # 8 = default, shown first
table = {}
for p in sys.argv[2:]:
    row = {}
    for pt in POINTS:
        r = c.price(p, f'points:{pt}')
        s = r['by_side'].get('sell')
        row[pt] = {'all': r['net'], 'sell': s['net'] if s else None, 'trades': r['trades'], 'sell_trades': s['n'] if s else 0}
    table[os.path.basename(p)[:-4]] = row
json.dump(table, open(sys.argv[1] + '.json', 'w'), indent=1)
hdr = '| Report | Trades | ' + ' | '.join(f'All {p} pts' for p in POINTS) + ' | Sell trades | ' + ' | '.join(f'Sell {p} pts' for p in POINTS) + ' |'
L = ['# Commission point table (net USD, 0.01 lots, $10k deposit; 8 pts = default)', '', hdr, '|' + '---|' * (3 + 2 * len(POINTS))]
for k, row in table.items():
    f = lambda v: '-' if v is None else f'{v:.2f}'
    L.append(f"| {k} | {row[8]['trades']} | " + ' | '.join(f(row[p]['all']) for p in POINTS) + f" | {row[8]['sell_trades']} | " + ' | '.join(f(row[p]['sell']) for p in POINTS) + ' |')
open(sys.argv[1] + '.md', 'w').write('\n'.join(L) + '\n')
