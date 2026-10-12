"""Track points, lots, balance, DD per run. Usage: python lots_tracker_v1_12Oct2026.py report.htm --balance 5000 [--commission PTS]
Commission default = FXOpen ECN tier (per side $/lot, round trip = 2x, 1 pt = $1/lot): <1k 7.0, 1k-25k 5.0, >=25k 3.6; cap 6."""
import sys, argparse, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oos_check import parse_report, max_closed_dd
def tier(b): return 7.0 if b < 1000 else (5.0 if b < 25000 else (3.6 if b < 250000 else 3.0))
ap = argparse.ArgumentParser(); ap.add_argument('report'); ap.add_argument('--balance', type=float, default=5000)
ap.add_argument('--commission', type=float, default=None); ap.add_argument('--lev', type=int, default=500); a = ap.parse_args()
c = a.commission if a.commission is not None else min(tier(a.balance), 6.0)
tr, _ = parse_report(a.report, c)
n = len(tr); lots = [t['lots'] for t in tr]
pts = sum(t['raw_profit'] / t['lots'] for t in tr if t['lots'] > 0)
comm = sum(t['raw_profit'] - t['profit'] for t in tr); net = sum(t['profit'] for t in tr)
gw = sum(t['profit'] for t in tr if t['profit'] > 0); gl = -sum(t['profit'] for t in tr if t['profit'] < 0)
dd, ddp = max_closed_dd(tr, a.balance)
w = sum(1 for t in tr if t['profit'] > 0)
bal = a.balance; peak = bal
for t in sorted(tr, key=lambda x: x['open_time']):
    bal += t['profit']; peak = max(peak, bal)
print('bal %.0f lev 1:%d comm %.1fpt | trades %d WR %.1f%% | lots avg %.2f max %.2f total %.1f | points net(raw) %.0f | comm paid $%.2f | net $%.2f -> end bal $%.2f (%.1f%%) | MAX BAL $%.2f | PF %.3f | maxDD $%.2f (%.2f%%) | %s' % (
 a.balance, a.lev, c, n, 100.0*w/max(n,1), sum(lots)/max(n,1), max(lots) if lots else 0, sum(lots), pts, comm, net, a.balance+net, 100*net/a.balance, peak, gw/gl if gl else 0, dd, ddp, 'PASS' if (gl and gw/gl >= 1.10 and ddp <= 5) else 'FAIL'))
