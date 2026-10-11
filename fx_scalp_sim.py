#!/usr/bin/env python3
"""EURUSD M1 buy-scalp simulator for the NH EA family. Research only, no orders.
Input: MT4 History Center M1 CSV (date,time,open,high,low,close,volume), Bid prices, 5-digit (point=0.00001).
Entry (core of the EAs): M1 SMA(2) slope >= 2 pts, M15 Stoch(10,3,3) at shift 2 <= 80, spread <= --maxspread, not Fri >= FriHour, not >= SwapHour.
Buy at Ask=open(next)+spread, exits at Bid. Same-bar TP+SL => SL assumed first. Costs: commission pts round trip, swap pts per rollover crossed.
Exits compared: fixed TP/SL, trailing stop, TP raise. --synthetic runs a zero-edge random walk as a tool check (NOT a result)."""
import csv,sys,random,argparse,itertools
ap=argparse.ArgumentParser();ap.add_argument("csv",nargs="?");ap.add_argument("--synthetic",action="store_true")
ap.add_argument("--spread",type=float,default=3);ap.add_argument("--maxspread",type=float,default=8);ap.add_argument("--comm",type=float,default=6)
ap.add_argument("--swap",type=float,default=0,help="pts charged per rollover crossed");ap.add_argument("--swaphour",type=int,default=22);ap.add_argument("--frihour",type=int,default=19)
ap.add_argument("--rollhour",type=int,default=23,help="server hour of rollover");ap.add_argument("--maxhold",type=int,default=1440,help="bars");ap.add_argument("--cooldown",type=int,default=5)
a=ap.parse_args();P=1e-5
def load():
    if a.synthetic:
        random.seed(1);x=1.1;out=[];import datetime;t=datetime.datetime(2023,1,2)
        while len(out)<150000:
            if t.weekday()<5:
                o=x;hi=lo=x
                for _ in range(4):x+=random.gauss(0,2.5)*P;hi=max(hi,x);lo=min(lo,x)
                out.append((t,o,hi,lo,x))
            t+=datetime.timedelta(minutes=1)
        return out
    import datetime;out=[]
    for r in csv.reader(open(a.csv)):
        try:out.append((datetime.datetime.strptime(r[0]+" "+r[1],"%Y.%m.%d %H:%M"),float(r[2]),float(r[3]),float(r[4]),float(r[5])))
        except:pass
    return out
B=load();n=len(B);o=[b[1] for b in B];h=[b[2] for b in B];l=[b[3] for b in B];c=[b[4] for b in B]
sma2=[None]+[(c[i]+c[i-1])/2 for i in range(1,n)]
# M15 stoch(10,3,3): built on non-overlapping 15-bar blocks keyed by block index (approximation of M15 series)
blk=[(max(h[i:i+15]),min(l[i:i+15]),c[min(i+14,n-1)]) for i in range(0,n,15)]
raw=[None if k<9 else (lambda hh,ll,cc:50 if hh==ll else 100*(cc-ll)/(hh-ll))(max(b[0] for b in blk[k-9:k+1]),min(b[1] for b in blk[k-9:k+1]),blk[k][2]) for k in range(len(blk))]
def sm(x,m):return [None if i<m-1 or any(v is None for v in x[i-m+1:i+1]) else sum(x[i-m+1:i+1])/m for i in range(len(x))]
st=sm(sm(raw,3),3)
def signals():
    s=[];last=-10**9
    for i in range(20,n-2):
        t=B[i][0]
        if sma2[i] is None or (sma2[i]-sma2[i-1])/P<2:continue
        k=i//15-2
        if k<0 or st[k] is None or st[k]>80:continue
        if t.weekday()==4 and t.hour>=a.frihour:continue
        if t.hour>=a.swaphour:continue
        if i-last<a.cooldown:continue
        s.append(i);last=i
    return s
SIG=signals()
def sim(tp,sl,trig=None,trail=None,flat_roll=False):
    res=[];busy=-1
    for i in SIG:
        if i<=busy:continue
        e=i+1;ent=o[e]+a.spread*P;stop=ent-sl*P;tgt=ent+tp*P;best=ent;exitp=None;rolls=0;m=e
        while m<n:
            t=B[m][0]
            if m>e:
                # stop/target tested on this bar with levels set from previous bars
                if l[m]<=stop:exitp=stop if o[m]>stop else o[m];break
                if tgt is not None and h[m]>=tgt:exitp=tgt;break
            if m>e and t.hour==a.rollhour and B[m-1][0].hour!=a.rollhour:
                if flat_roll:exitp=o[m];break
                rolls+=1
            best=max(best,h[m])
            if trail is not None and (best-ent)/P>=trig:stop=max(stop,best-trail*P)
            if m-e>=a.maxhold:exitp=c[m];break
            m+=1
        if exitp is None:exitp=c[n-1]
        pnl=(exitp-ent)/P-a.comm-a.swap*rolls;res.append(pnl);busy=m
    return res
def rep(name,r):
    if not r:print(f"{name:42s} n=0");return
    w=sum(x>0 for x in r);print(f"{name:42s} n={len(r):5d} win={100*w/len(r):5.1f}% avg={sum(r)/len(r):7.2f}pts total={sum(r):9.0f} worst={min(r):7.0f}")
print(f"bars={n} signals={len(SIG)} spread={a.spread} comm={a.comm} swap={a.swap}/roll"+("  [SYNTHETIC ZERO-EDGE: tool check only]" if a.synthetic else ""))
rep("fixed TP8 / SL290 (current EAs)",sim(8,290))
rep("fixed TP8 / SL50",sim(8,50))
rep("fixed TP20 / SL40",sim(20,40))
rep("fixed TP40 / SL40",sim(40,40))
rep("no TP, trail 20 after +20, SL40",sim(10**6,40,20,20))
rep("no TP, trail 12 after +12, SL30",sim(10**6,30,12,12))
rep("no TP, trail 30 after +30, SL60",sim(10**6,60,30,30))
rep("TP60 + trail 15 after +15, SL40",sim(60,40,15,15))
rep("TP20/SL40 flat before rollover",sim(20,40,flat_roll=True))
rep("no TP trail 20/20 SL40 flat at rollover",sim(10**6,40,20,20,flat_roll=True))
