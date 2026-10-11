#!/usr/bin/env python3
"""Head & Shoulders (top = SELL/short) and Inverse H&S (bottom = BUY) on daily bars. No orders, research only.
READING   : swing pivots (k bars each side, confirmed k bars late = no lookahead), LS-T1-HEAD-T2-RS, sloped neckline.
ANTICIPATE: right shoulder forming (price turning down from RS candidate, still above neckline) -> 'forming' alert with trigger price.
SIGNAL    : first close through the neckline.  ENTRY: next open.
TRADE     : stop = right-shoulder extreme, target = neckline -/+ pattern height, time exit MAXH bars, round-trip costs charged.
Usage: python3 hs_pattern.py [--data data/history] [--k 5] [--maxh 20] [--read]"""
import glob,os,csv,json,argparse
ap=argparse.ArgumentParser();ap.add_argument("--data",default="data/history");ap.add_argument("--k",type=int,default=5)
ap.add_argument("--maxh",type=int,default=20);ap.add_argument("--read",action="store_true");a=ap.parse_args()
C=json.load(open("cost_model.json"));RT=C["spread_bps"]["stock"]/100+2*C["slippage_bps_per_side"]/100+C["reg_fee_bps_sell"]/100
def top_state(H,L,Cl,t,k):
    """Top H&S state at bar t using data <= t. returns None | dict(kind='forming'|'signal', ...)"""
    n=t+1;piv=[]  # confirmed pivots (idx,type,price), alternating
    for i in range(k,n-k):
        if H[i]==max(H[i-k:i+k+1]):typ,p="H",H[i]
        elif L[i]==min(L[i-k:i+k+1]):typ,p="L",L[i]
        else:continue
        if piv and piv[-1][1]==typ:
            if (typ=="H" and p>piv[-1][2]) or (typ=="L" and p<piv[-1][2]):piv[-1]=(i,typ,p)
        else:piv.append((i,typ,p))
    if len(piv)<4:return None
    (iLS,_,LS),(i1,_,T1),(iH,_,HD),(i2,_,T2)=piv[-4:]
    if piv[-4][1]!="H" or piv[-1][1]!="L":return None
    if i2>=t:return None
    j=max(range(i2+1,t+1),key=lambda x:H[x]);RS=H[j]   # right-shoulder candidate (running high since T2)
    slope=(T2-T1)/(i2-i1);nl=lambda x:T1+slope*(x-i1)
    ht=HD-nl(iH)
    if not(0.03*abs(HD)<=ht<=0.4*abs(HD)) or HD<=LS or HD<=RS:return None
    if abs(LS-RS)>0.5*ht or RS<nl(j)+0.3*ht or j-iLS>120 or j-i2<2:return None
    st=dict(ls=LS,head=HD,rs=RS,neck=nl(t),height=ht,rs_idx=j,key=(iH,j))
    if Cl[t]<nl(t):
        if t-1>=0 and Cl[t-1]>=nl(t-1):st["kind"]="signal";return st
        return None
    if Cl[t]<RS*0.995 and Cl[t]>nl(t):st["kind"]="forming";return st
    return None
def run(path):
    R=list(csv.DictReader(open(path)));d=[r["date"] for r in R];o=[float(r["open"]) for r in R];h=[float(r["high"]) for r in R];l=[float(r["low"]) for r in R];c=[float(r["close"]) for r in R];n=len(c)
    sides={"sell":(h,l,c,1),"buy":([-x for x in l],[-x for x in h],[-x for x in c],-1)}  # inverse H&S = top on negated prices
    trades=[];reads=[];seen=set()
    for side,(H,L,Cl,sg) in sides.items():
        for t in range(40,n-1):
            s=top_state(H,L,Cl,t,a.k)
            if not s or s["kind"]!="signal" or (side,s["key"]) in seen:continue
            seen.add((side,s["key"]))
            e=t+1;ent=o[e];stop=s["rs"];tgt=s["neck"]-s["height"]  # in transformed space
            ent_t=sg*ent  # transformed entry price (negated for buy)
            ex=None
            for m in range(e,min(e+a.maxh,n-1)+1):
                Hh,Ll=H[m],L[m]
                if Hh>=stop:ex=max(stop,sg*o[m]);break  # gap through stop exits at the open
                if Ll<=tgt:ex=tgt;break
            if ex is None:m=min(e+a.maxh,n-1);ex=Cl[m]
            g=(ent_t-ex)/abs(ent_t)*100  # profit in transformed space (short on transformed = original direction)
            trades.append((side,d[t],round(g-RT,3)))
    # reading of latest bar
    for side,(H,L,Cl,sg) in sides.items():
        s=top_state(H,L,Cl,n-1,a.k)
        if s:
            nk=sg*s["neck"];reads.append((side,s["kind"],round(nk,2),round(sg*s["rs"],2),round(sg*(s["neck"]-s["height"]),2)))
    return trades,reads
allt=[];
for fn in sorted(glob.glob(a.data+"/*.csv")):
    sym=os.path.basename(fn)[:-4];tr,rd=run(fn);allt+=[(sym,)+x for x in tr]
    if a.read:
        print(sym,"->",("; ".join(f"{'TOP H&S (sell)' if s=='sell' else 'INVERSE H&S (buy)'} {k}: neckline {nk}, shoulder {rs}, target {tg}" for s,k,nk,rs,tg in rd) or "no pattern"))
print(f"\nH&S trades (k={a.k}, max hold {a.maxh}d, net of costs; shorts ignore borrow):")
for side in("buy","sell"):
    L=[x for x in allt if x[1]==side]
    if not L:print(side,"n=0");continue
    w=sum(x[3]>0 for x in L)
    p=lambda q:f"n={len(q)} avg={sum(x[3] for x in q)/len(q):.2f}" if q else "n=0"
    print(f" {'inverse H&S BUY ' if side=='buy' else 'top H&S SELL    '} n={len(L)} win={100*w/len(L):.0f}% avg={sum(x[3] for x in L)/len(L):.2f}% | 22-23 {p([x for x in L if x[2]<'2024'])} | 24-26 {p([x for x in L if x[2]>='2024'])}")
