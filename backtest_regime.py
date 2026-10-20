#!/usr/bin/env python3
"""Regime-filtered backtest: only take S1/S3 signals when SPY > 200SMA."""
import glob,os,csv,json,collections
C=json.load(open("cost_model.json"))
def cost_pct(kind,days):
    return C["spread_bps"].get(kind,4)/100+2*C["slippage_bps_per_side"]/100+2*C["comm_per_order_usd"]/C["position_usd"]*100+C["reg_fee_bps_sell"]/100+days*C["swap_pct_per_year"]/365
def sma(x,n,i):return sum(x[i-n+1:i+1])/n if i>=n-1 else None
def feats(c,h,l):
    out=[]
    for i in range(len(c)):
        f={}
        if i>=14:
            g=[max(c[j]-c[j-1],0) for j in range(i-13,i+1)];d=[max(c[j-1]-c[j],0) for j in range(i-13,i+1)]
            ag,al=sum(g)/14,sum(d)/14;f["rsi"]=100 if al==0 else 100-100/(1+ag/al)
            hh,ll=max(h[i-13:i+1]),min(l[i-13:i+1]);f["stoch"]=50 if hh==ll else 100*(c[i]-ll)/(hh-ll)
        if i>=20:
            m=sma(c,20,i);sd=(sum((x-m)**2 for x in c[i-19:i+1])/20)**.5;f["bbl"]=m-2*sd
        if i>=10:f["r3"]=c[i]/c[i-3]-1;f["r10"]=c[i]/c[i-10]-1
        if i>=50:f["up"]=c[i]>sma(c,50,i)
        out.append(f)
    return out

# Load SPY 200SMA lookup
spy_rows=list(csv.DictReader(open("data/history/SPY.csv")))
spy_c=[float(r["close"]) for r in spy_rows]
spy_d=[r["date"] for r in spy_rows]
spy200={}
for i in range(len(spy_c)):
    s=sma(spy_c,200,i)
    if s:spy200[spy_d[i]]=(spy_c[i]>s)

RULES_REGIME={
    "S1_regime RSI<30 & belowBB & SPY>200SMA":lambda f,c,bull:f.get("rsi",99)<30 and c<f.get("bbl",0) and bull,
    "S3_regime 3d-5%&10d-10%&SPY>200SMA":lambda f,c,bull:f.get("r3",0)<-.05 and f.get("r10",0)<-.10 and bull,
}
def per(d):return "2015-19" if d<"2020" else "2020-22" if d<"2023" else "2023-26"
hold=3
cc=cost_pct("stock",hold)
acc=collections.defaultdict(lambda:[0,0,0.0,0.0,0.0])
for fn in glob.glob("data/history/*.csv"):
    if "SPY" in fn:continue
    R=list(csv.DictReader(open(fn)));c=[float(r["close"]) for r in R];h=[float(r["high"]) for r in R];l=[float(r["low"]) for r in R];d=[r["date"] for r in R];F=feats(c,h,l);prev={k:False for k in RULES_REGIME}
    for i in range(len(c)-hold):
        if d[i]<"2015":continue
        bull=spy200.get(d[i],False)
        g=(c[i+hold]/c[i]-1)*100;n=g-cc;at=n*(1-C["tax_short_term_pct"]/100) if n>0 else n
        for k,fx in RULES_REGIME.items():
            on=fx(F[i],c[i],bull)
            if on and not prev[k]:
                q=acc[(k,per(d[i]))];q[0]+=1;q[1]+=n>0;q[2]+=g;q[3]+=n;q[4]+=at
            prev[k]=on

os.makedirs("results",exist_ok=True)
print(f"{'Rule':<45} {'Period':<10} {'n':>5} {'Win%':>6} {'Avg gross':>10} {'Avg net':>9} {'After-tax':>10}")
print("-"*105)
for (k,p),q in sorted(acc.items()):
    if q[0]:
        print(f"{k:<45} {p:<10} {q[0]:>5} {100*q[1]/q[0]:>6.1f} {q[2]/q[0]:>10.3f} {q[3]/q[0]:>9.3f} {q[4]/q[0]:>10.3f}")

# Save
with open("results/regime_filter_results.csv","w",newline="") as o:
    w=csv.writer(o);w.writerow(["rule","period","n","win_net_pct","avg_gross","avg_net","avg_after_tax"])
    for (k,p),q in sorted(acc.items()):
        if q[0]:w.writerow([k,p,q[0],round(100*q[1]/q[0],1),round(q[2]/q[0],3),round(q[3]/q[0],3),round(q[4]/q[0],3)])
print(f"\ncost/round trip {cc:.3f}%  (stock 3d hold)")
print("wrote results/regime_filter_results.csv")
