#!/usr/bin/env python3
"""Merge bars into data CSVs. stdin lines: SYM date open high low close (any order of dates). Keeps one row per date, sorted."""
import sys,csv,os
d=sys.argv[1];k=sys.argv[2] if len(sys.argv)>2 else "date";os.makedirs(d,exist_ok=True);N={}
for ln in sys.stdin:
    p=ln.split()
    if len(p)==6:N.setdefault(p[0],{})[p[1]]=p[2:]
for s,rows in N.items():
    fn=f"{d}/{s}.csv";old={}
    if os.path.exists(fn):
        for r in csv.DictReader(open(fn)):old[r[k]]=[r["open"],r["high"],r["low"],r["close"]]
    old.update(rows)
    with open(fn,"w",newline="") as o:
        w=csv.writer(o);w.writerow([k,"open","high","low","close","volume"])
        for t in sorted(old):w.writerow([t,*old[t],0])
    print(s,len(old))
