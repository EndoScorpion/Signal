#!/usr/bin/env python3
"""Paper-trading bot: LOCAL simulated broker only. No Webull order calls. Live is not implemented.
Replays rules over data/history, enters at next open, exits after HOLD days, charges cost_model.json costs.
Limits: MAX_POS open positions, MAX_NEW per day, DAILY_LOSS_STOP pct, kill file results/KILL."""
import glob,os,csv,json,argparse
ap=argparse.ArgumentParser();ap.add_argument("--data",default="data/history");ap.add_argument("--cost",default="cost_model.json")
ap.add_argument("--rule",default="S1");ap.add_argument("--hold",type=int,default=3);ap.add_argument("--from",dest="frm",default="2024-01-01")
ap.add_argument("--equity",type=float,default=10000);ap.add_argument("--pos",type=float,default=1000)
ap.add_argument("--max-pos",type=int,default=5);ap.add_argument("--max-new",type=int,default=3);ap.add_argument("--daily-loss-stop",type=float,default=2.0)
a=ap.parse_args();C=json.load(open(a.cost))
RT=(C["spread_bps"]["stock"]/100+2*C["slippage_bps_per_side"]/100+C["reg_fee_bps_sell"]/100)  # round-trip cost %
def sma(x,n,i):return sum(x[i-n+1:i+1])/n
def feat(c,h,l,i):
    f={}
    if i>=14:
        g=[max(c[j]-c[j-1],0) for j in range(i-13,i+1)];d=[max(c[j-1]-c[j],0) for j in range(i-13,i+1)]
        ag,al=sum(g)/14,sum(d)/14;f["rsi"]=100 if al==0 else 100-100/(1+ag/al)
    if i>=20:
        m=sma(c,20,i);sd=(sum((x-m)**2 for x in c[i-19:i+1])/20)**.5;f["bbl"]=m-2*sd
    return f
RULES={"S1":lambda f,p:f.get("rsi",99)<30 and p<f.get("bbl",0),"S2":lambda f,p:f.get("rsi",99)<25}
rule=RULES[a.rule]
D={}
for fn in glob.glob(a.data+"/*.csv"):
    R=list(csv.DictReader(open(fn)));D[os.path.basename(fn)[:-4]]=[(r["date"],float(r["open"]),float(r["high"]),float(r["low"]),float(r["close"])) for r in R]
dates=sorted({r[0] for v in D.values() for r in v if r[0]>=a.frm})
cash=a.equity;open_=[];ledger=[];prev_eq=a.equity
idx={s:{r[0]:i for i,r in enumerate(v)} for s,v in D.items()}
def px(s,d,k):i=idx[s].get(d);return None if i is None else D[s][i][k]
for di,d in enumerate(dates):
    if os.path.exists("results/KILL"):print("KILL file: stop");break
    for p in list(open_):  # exits at today's open after hold days
        if p["due"]<=d and px(p["s"],d,1):
            x=px(p["s"],d,1);gross=(x/p["e"]-1)*100;net=gross-RT;cash+=p["usd"]*(1+net/100)
            ledger.append((p["s"],p["d0"],d,round(p["e"],2),round(x,2),round(gross,3),round(net,3)));open_.remove(p)
    eq=cash+sum(p["usd"] for p in open_)
    if (prev_eq-eq)/prev_eq*100>=a.daily_loss_stop:prev_eq=eq;continue  # daily loss stop: skip entries
    prev_eq=eq;new=0
    if di==0:continue
    yd=dates[di-1]
    for s in sorted(D):
        if len(open_)>=a.max_pos or new>=a.max_new or cash<a.pos:break
        i=idx[s].get(yd);o=px(s,d,1)
        if i is None or o is None or any(p["s"]==s for p in open_):continue
        c=[r[4] for r in D[s]];h=[r[2] for r in D[s]];l=[r[3] for r in D[s]]
        if rule(feat(c,h,l,i),c[i]):
            cash-=a.pos;new+=1;due=dates[min(di+a.hold,len(dates)-1)];open_.append(dict(s=s,d0=d,e=o,usd=a.pos,due=due))
os.makedirs("results",exist_ok=True)
with open("results/paper_ledger.csv","w",newline="") as o:
    w=csv.writer(o);w.writerow(["sym","entry","exit","in","out","gross%","net%"]);w.writerows(ledger)
n=len(ledger);nets=[r[6] for r in ledger]
print(f"rule {a.rule} hold {a.hold} from {a.frm}: trades {n} win% {100*sum(x>0 for x in nets)/max(n,1):.1f} avg net {sum(nets)/max(n,1):.3f}% end equity {cash+sum(p['usd'] for p in open_):.0f} (start {a.equity:.0f}) open {len(open_)}")
