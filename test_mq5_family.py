import glob,csv,json
C=json.load(open("cost_model.json"));RT=C["spread_bps"]["stock"]/100+2*C["slippage_bps_per_side"]/100+C["reg_fee_bps_sell"]/100
HOLD=10
def sma(x,n):return [None if i<n-1 else sum(x[i-n+1:i+1])/n for i in range(len(x))]
def rsi(c,n):  # Wilder
    r=[None]*len(c)
    if len(c)<=n:return r
    g=sum(max(c[i]-c[i-1],0) for i in range(1,n+1))/n;l=sum(max(c[i-1]-c[i],0) for i in range(1,n+1))/n
    r[n]=100 if l==0 else 100-100/(1+g/l)
    for i in range(n+1,len(c)):
        g=(g*(n-1)+max(c[i]-c[i-1],0))/n;l=(l*(n-1)+max(c[i-1]-c[i],0))/n;r[i]=100 if l==0 else 100-100/(1+g/l)
    return r
def cci(c,n):
    m=sma(c,n);r=[None]*len(c)
    for i in range(n-1,len(c)):
        md=sum(abs(c[j]-m[i]) for j in range(i-n+1,i+1))/n;r[i]=0 if md==0 else (c[i]-m[i])/(0.015*md)
    return r
def mfi(h,l,c,v,n):
    tp=[(h[i]+l[i]+c[i])/3 for i in range(len(c))];r=[None]*len(c)
    for i in range(n,len(c)):
        p=q=0
        for j in range(i-n+1,i+1):
            f=tp[j]*v[j]
            if tp[j]>tp[j-1]:p+=f
            elif tp[j]<tp[j-1]:q+=f
        r[i]=100 if q==0 else 100-100/(1+p/q)
    return r
def stoch(h,l,c,K,D,S):
    n=len(c);raw=[None]*n
    for i in range(K-1,n):
        hh,ll=max(h[i-K+1:i+1]),min(l[i-K+1:i+1]);raw[i]=50 if hh==ll else 100*(c[i]-ll)/(hh-ll)
    def sm(x,m):return [None if i<m-1 or any(v is None for v in x[i-m+1:i+1]) else sum(x[i-m+1:i+1])/m for i in range(n)]
    return sm(sm(raw,S),D)
CONF={"Stoch47/9/13":(lambda h,l,c,v:stoch(h,l,c,47,9,13),lambda s:s<30,lambda s:s>70),
      "RSI37 <40/>60":(lambda h,l,c,v:rsi(c,37),lambda s:s<40,lambda s:s>60),
      "CCI37 <-50/>50":(lambda h,l,c,v:cci(c,37),lambda s:s<-50,lambda s:s>50),
      "MFI37 <40/>60":(lambda h,l,c,v:mfi(h,l,c,v,37),lambda s:s<40,lambda s:s>60)}
out={}
def add(k,side,d,g):out.setdefault((k,side),[]).append((d,g-RT))
for fn in glob.glob("data/history/*.csv"):
    R=list(csv.DictReader(open(fn)));d=[r["date"] for r in R];o=[float(r["open"]) for r in R];h=[float(r["high"]) for r in R];l=[float(r["low"]) for r in R];c=[float(r["close"]) for r in R];v=[float(r["volume"]) for r in R];n=len(c)
    body=[abs(o[i]-c[i]) for i in range(n)];ma5=sma(c,5)
    ind={k:f(h,l,c,v) for k,(f,_,_) in CONF.items()};st=ind["Stoch47/9/13"]
    for t in range(60,n-HOLD-1):
        i=t-1;a=sum(body[i-j] for j in range(12))/12;b1,b2,b3=i,i-1,i-2;mid3=(o[b3]+c[b3])/2;side=None
        if c[b3]-o[b3]>a and abs(c[b2]-o[b2])<a*.1 and c[b2]>c[b3] and o[b2]>o[b3] and o[b1]<c[b2] and c[b1]<c[b2]:side="sell"
        elif c[b3]-o[b3]>a and abs(c[b2]-o[b2])<a*.5 and c[b2]>c[b3] and o[b2]>o[b3] and c[b1]<mid3:side="sell"
        elif o[b3]-c[b3]>a and abs(c[b2]-o[b2])<a*.1 and c[b2]<c[b3] and o[b2]<o[b3] and o[b1]>c[b2] and c[b1]>c[b2]:side="buy"
        elif o[b3]-c[b3]>a and abs(c[b2]-o[b2])<a*.5 and c[b2]<c[b3] and o[b2]<o[b3] and c[b1]>mid3:side="buy"
        if side:
            for k,(_,bf,sf) in CONF.items():
                s=ind[k][i]
                if s is None:continue
                if (side=="buy" and bf(s)) or (side=="sell" and sf(s)):add("Star/Doji+"+k,side,d[t],(c[t+HOLD]/o[t]-1)*100*(1 if side=="buy" else -1))
        # Hammer / Hanging Man (+stoch), as in the EA
        if ma5[b2] is not None and st[i] is not None:
            mid=(h[i]+l[i])/2;top=h[i]-(h[i]-l[i])/3
            hs=None
            if mid>ma5[b2] and min(o[i],c[i])>top and c[i]>c[b2] and o[i]>o[b2]:hs="sell"
            elif mid<ma5[b2] and min(o[i],c[i])>top and c[i]<c[b2] and o[i]<o[b2]:hs="buy"
            if hs and ((hs=="buy" and st[i]<30) or (hs=="sell" and st[i]>70)):add("HangMan/Hammer+Stoch",hs,d[t],(c[t+HOLD]/o[t]-1)*100*(1 if hs=="buy" else -1))
print("hold 10d, entry next open, net of costs, 10 symbols 2022-26 (shorts ignore borrow cost)")
for (k,s),L in sorted(out.items()):
    a=[x for dd,x in L if dd<"2024"];b=[x for dd,x in L if dd>="2024"]
    f=lambda q:f"n={len(q)} avg={sum(q)/len(q):.2f}" if q else "n=0"
    print(f"{k:34s}{s:5s} n={len(L):3d} win={100*sum(x>0 for _,x in L)/len(L):4.0f}% avg={sum(x for _,x in L)/len(L):6.2f}% | 22-23 {f(a)} | 24-26 {f(b)}")
