import csv,glob,itertools,json,collections,sys
import numpy as np
f=glob.glob('/root/.claude/uploads/872f8bbd-13b0-5e26-a092-57124dc9b3f6/*H1_all*')[0]
RAW=collections.defaultdict(list)
for r in csv.DictReader(open(f)):RAW[r['symbol']].append((r['time_utc'],float(r['open']),float(r['high']),float(r['low']),float(r['close'])))
def sma(x,n):
    c=np.cumsum(np.insert(x,0,0));o=np.full(len(x),np.nan);o[n-1:]=(c[n:]-c[:-n])/n;return o
def rstd(x,n):
    m=sma(x,n);m2=sma(x*x,n);return np.sqrt(np.maximum(m2-m*m,0))
def rmax(x,n):return np.array([x[max(0,i-n+1):i+1].max() for i in range(len(x))])
def rmin(x,n):return np.array([x[max(0,i-n+1):i+1].min() for i in range(len(x))])
def rsi(c,n=14):
    d=np.diff(c,prepend=c[0]);u=np.where(d>0,d,0);dn=np.where(d<0,-d,0);au=np.zeros(len(c));ad=np.zeros(len(c))
    au[n]=u[1:n+1].mean();ad[n]=dn[1:n+1].mean()
    for i in range(n+1,len(c)):au[i]=(au[i-1]*(n-1)+u[i])/n;ad[i]=(ad[i-1]*(n-1)+dn[i])/n
    r=100-100/(1+au/np.maximum(ad,1e-12));r[:n]=np.nan;return r
S={}
for s,a in RAW.items():
    if len(a)<1500 or s in('EURUSD','MATIC'):continue
    t=[x[0] for x in a];o,h,l,c=[np.array([x[k] for x in a]) for k in(1,2,3,4)];n=len(c)
    F={};F['rsi']=rsi(c);lo=rmin(l,14);hi=rmax(h,14);F['stoch']=100*(c-lo)/np.maximum(hi-lo,1e-12)
    m=sma(c,20);sd=rstd(c,20);F['bbp']=100*(c-(m-2*sd))/np.maximum(4*sd,1e-12);F['ext']=100*(c/m-1)/np.maximum(100*sd/m,1e-9)  # z-score of price vs sma20
    F['ret3']=100*(c/np.roll(c,3)-1);F['ret12']=100*(c/np.roll(c,12)-1);tr=np.maximum(h-l,np.abs(h-np.roll(c,1)));F['atrp']=100*sma(tr,14)/c
    ma=sma(c,24);F['trend']=100*(ma/np.roll(ma,12)-1)/np.maximum(F['atrp'],1e-9)
    F['hr']=np.array([int(x[11:13]) for x in t]).astype(float)
    F['dow']=np.array([__import__('datetime').datetime.fromisoformat(x).weekday() for x in t]).astype(float)
    fr=np.full(n,np.nan);fr[:-4]=100*(c[4:]/c[:-4]-1)
    S[s]=dict(F=F,fr=fr,n=n)
TUNE=['ETH','ADA','AVAX','DOT','LINK','LTC']  # 7000 bar majors
HOLD=[s for s in S if s not in TUNE]
print('tune',TUNE,'holdout',HOLD,{s:S[s]['n'] for s in S})
def episodes(mask,fr,side,cost,lo,hi):
    out=[];i=lo
    idx=np.where(mask[lo:hi])[0]+lo;last=-99
    for i in idx:
        if i-last<4 or np.isnan(fr[i]):continue
        out.append(side*fr[i]-cost);last=i
    return out
def evalrule(rule,side,syms,a,b,cost=0.04):
    r=[]
    for s in syms:
        d=S[s];n=d['n'];lo=int(n*a);hi=int(n*b);mask=np.ones(n,bool)
        for k,op,v in rule:
            x=d['F'][k];mask&=(x>v) if op=='>' else (x<v)&~np.isnan(x)
            mask&=~np.isnan(x)
        r+=episodes(mask,d['fr'],side,cost,lo,hi)
    return np.array(r)
def stat(r):
    if len(r)<3:return (len(r),0,0,0)
    return (len(r),100*(r>0).mean(),r.mean(),r.mean()/(r.std()/np.sqrt(len(r))+1e-9))
GRID={'rsi':[('<',20),('<',25),('<',30),('<',35),('>',65),('>',70),('>',75),('>',80)],
'stoch':[('<',10),('<',20),('<',30),('>',70),('>',80),('>',90)],
'bbp':[('<',5),('<',15),('<',25),('>',75),('>',85),('>',95)],
'ext':[('<',-2),('<',-1.5),('<',-1),('>',1),('>',1.5),('>',2)],
'ret3':[('<',-1.5),('<',-1),('<',-.5),('>',.5),('>',1),('>',1.5)],
'ret12':[('<',-3),('<',-2),('<',-1),('>',1),('>',2),('>',3)],
'trend':[('<',-1),('<',0),('>',0),('>',1)],
'atrp':[('<',.3),('<',.5),('>',.5),('>',.8)],
'hr':[('<',8),('>',15),('<',12),('>',11)],}
atoms=[(k,op,v) for k,L in GRID.items() for op,v in L]
rules=[(a,) for a in atoms]+[(a,b) for a,b in itertools.combinations(atoms,2) if a[0]!=b[0]]
print('rules',len(rules)*2)
res=[]
for rl in rules:
    for side in(1,-1):
        t=evalrule(rl,side,TUNE,0,.6)
        if len(t)<40:continue
        n,w,m,tt=stat(t)
        if tt<2.5 or m<=0.08:continue
        v=evalrule(rl,side,TUNE,.6,.8);sv=stat(v)
        if sv[0]<10 or sv[2]<=0:continue
        res.append((rl,side,stat(t),sv))
print('survive train+val',len(res))
out=[]
for rl,side,st,sv in res:
    te=stat(evalrule(rl,side,TUNE,.8,1.0));ho=stat(evalrule(rl,side,HOLD,0,1.0));hs=stat(evalrule(rl,side,HOLD,0,1.0,cost=0.12))
    out.append(dict(rule=[list(x) for x in rl],side='BUY' if side==1 else 'SELL',train=st,val=sv,test=te,holdout=ho,holdout_cost12=hs))
json.dump(out,open('res.json','w'),default=float)
good=[o for o in out if o['test'][2]>0 and o['holdout'][2]>0.05 and o['holdout'][0]>=30]
good.sort(key=lambda o:-o['holdout'][3])
print('pass test+holdout',len(good))
for o in good[:25]:
    print(o['side'],' & '.join(f"{k}{op}{v}" for k,op,v in o['rule']),'| tr n/w/avg',[round(x,2) for x in o['train'][:3]],'val',[round(x,2) for x in o['val'][:3]],'test',[round(x,2) for x in o['test'][:3]],'HOLD',[round(x,2) for x in o['holdout']],'@0.12',[round(x,2) for x in o['holdout_cost12'][1:3]])
