import sys, random
sys.path.insert(0, '/home/claude/signal/analysis')
from oos_check import parse_report
from collections import defaultdict
for f in sys.argv[1:]:
    r = parse_report(f, 2)
    trades = r[0] if isinstance(r, tuple) else r
    day = defaultdict(float)
    for t in trades: day[t['open_time'].date()] += t['profit']
    v = list(day.values()); n = len(v); random.seed(1); B = 20000
    neg = sum(1 for _ in range(B) if sum(random.choice(v) for _ in range(n)) <= 0)
    print(f.split('/')[-1], 'days', n, 'net', round(sum(v),2), 'day-block p(net<=0)', neg / B)
