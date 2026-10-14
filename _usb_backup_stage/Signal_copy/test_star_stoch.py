import glob,os,csv,json
C=json.load(open("cost_model.json"));RT=C["spread_bps"]["stock"]/100+2*C["slippage_bps_per_side"]/100+C["reg_fee_bps_sell"]/100
def sma(x,n):return [None if i<n-1 else sum(x[i-n+1:i+1])/n for i in range(len(x))]
def run(K,D,S,hold,avgp=12):
    res={"buy":[],"sell":[]}
    for fn in glob.glob("data/history/*.csv"):
        R=list(csv.DictReader(open(fn)));d=[r["date"] for r in R];o=[float(r["open"]) for r in R];h=[float(r["high"]) for r in R];l=[float(r["low"]) for r in R];c=[float(r["close"]) for r in R];n=len(c)
        raw=[None]*n
        for i in range(K-1,n):
            hh,ll=max(h[i-K+1:i+1]),min(l[i-K+1:i+1]);raw[i]=50 if hh==ll else 100*(c[i]-ll)/(hh-ll)
        def sm(x,m):return [None if i<m-1 or any(v is None for v in x[i-m+1:i+1]) else sum(x[i-m+1:i+1])/m for i in range(n)]
        sig=sm(sm(raw,S),D)
        body=[abs(o[i]-c[i]) for i in range(n)]
        for t in range(K+S+D+avgp+4,n-hold-1):
            i=t-1  # bar index used as "1" (last closed), 2 and 3 earlier ;  act at open of bar t
            a=sum(body[i-j] for j in range(avgp))/avgp  # AvgBody(1)
            b1,b2,b3=i,i-1,i-2
            mid3=(o[b3]+c[b3])/2
            side=None
            if c[b3]-o[b3]>a and abs(c[b2]-o[b2])<a*.1 and c[b2]>c[b3] and o[b2]>o[b3] and o[b1]<c[b2] and c[b1]<c[b2]:side="sell"
            elif c[b3]-o[b3]>a and abs(c[b2]-o[b2])<a*.5 and c[b2]>c[b3] and o[b2]>o[b3] and c[b1]<mid3:side="sell"
            elif o[b3]-c[b3]>a and abs(c[b2]-o[b2])<a*.1 and c[b2]<c[b3] and o[b2]<o[b3] and o[b1]>c[b2] and c[b1]>c[b2]:side="buy"
            elif o[b3]-c[b3]>a and abs(c[b2]-o[b2])<a*.5 and c[b2]<c[b3] and o[b2]<o[b3] and c[b1]>mid3:side="buy"
            if side is None or sig[i] is None:continue
            if side=="buy" and not sig[i]<30:continue
            if side=="sell" and not sig[i]>70:continue
            g=(c[t+hold]/o[t]-1)*100*(1 if side=="buy" else -1)  # enter next open, exit close after hold bars
            res[side].append((d[t],g-RT))
    return res
def rep(tag,L):
    if not L:print(tag,"n=0");return
    pe=lambda x:"A" if x<"2024" else "B"
    s=f"{tag} n={len(L)} win={100*sum(v>0 for _,v in L)/len(L):.1f} avgnet={sum(v for _,v in L)/len(L):.3f}"
    for p in "AB":
        q=[v for d,v in L if pe(d)==p];s+=f" | {'2022-23' if p=='A' else '2024-26'} n={len(q)} avg={sum(q)/len(q) if q else 0:.3f}"
    print(s)
for (K,D,S) in [(47,9,13),(14,3,3)]:
    r=run(K,D,S,10);print(f"stoch {K}/{D}/{S} hold 10");rep(" morning BUY ",r["buy"]);rep(" evening SELL",r["sell"])
