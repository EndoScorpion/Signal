#!/usr/bin/env python3
"""Daily rule backtest NET of costs and tax. Each fresh signal counted once; hold N days; compared with all-days baseline."""
import glob,os,csv,json,argparse,collections
ap=argparse.ArgumentParser();ap.add_argument("--data",default="data/history");ap.add_argument("--hold",type=int,default=3);ap.add_argument("--cost",default="cost_model.json");ap.add_argument("--group",default="stock");a=ap.parse_args()
C=json.load(open(a.cost))
def cost_pct(kind,days):
    return C["spread_bps"].get(kind,4)/100+2*C["slippage_bps_per_side"]/100+2*C["comm_per_order_usd"]/C["position_usd"]*100+(2*C["crypto_fee_bps_per_side"]/100 if kind=="crypto" else C["reg_fee_bps_sell"]/100)+days*C["swap_pct_per_year"]/365
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
RULES={"S1 RSI<30 & below BB":lambda f,c:f.get("rsi",99)<30 and c<f.get("bbl",0),"S2 RSI<25":lambda f,c:f.get("rsi",99)<25,"S3 3d-5% & 10d-10%":lambda f,c:f.get("r3",0)<-.05 and f.get("r10",0)<-.10,"S4 below BB & Stoch<10 in uptrend":lambda f,c:c<f.get("bbl",0) and f.get("stoch",99)<10 and f.get("up",False)}
def per(d):return "2015-19" if d<"2020" else "2020-22" if d<"2023" else "2023-26"
acc=collections.defaultdict(lambda:[0,0,0.0,0.0,0.0,0,0.0,0.0])  # n,wins,gross,net,aftertax,ddN,ddSum,ddMax
cc=cost_pct(a.group,a.hold)
def parts(kind,days):
    return dict(spread=C["spread_bps"].get(kind,4)/100,slippage=2*C["slippage_bps_per_side"]/100,commission=2*C["comm_per_order_usd"]/C["position_usd"]*100,fees=(2*C["crypto_fee_bps_per_side"]/100 if kind=="crypto" else C["reg_fee_bps_sell"]/100),swap=days*C["swap_pct_per_year"]/365)
P=parts(a.group,a.hold)
for fn in glob.glob(a.data+"/*.csv"):
    R=list(csv.DictReader(open(fn)));c=[float(r["close"]) for r in R];h=[float(r["high"]) for r in R];l=[float(r["low"]) for r in R];d=[r["date"] for r in R];F=feats(c,h,l);prev={k:False for k in RULES};ST={}
    for i in range(len(c)-a.hold):
        if d[i]<"2015":continue
        g=(c[i+a.hold]/c[i]-1)*100;n=g-cc;at=n*(1-C["tax_short_term_pct"]/100) if n>0 else n
        def add(k):
            q=acc[k];q[0]+=1;q[1]+=n>0;q[2]+=g;q[3]+=n;q[4]+=at
            s=ST.setdefault(k,[0.0,0.0,0.0]);s[0]+=at   # eq,peak,cur
            if s[0]>=s[1]:
                if s[2]>0:q[5]+=1;q[6]+=s[2];q[7]=max(q[7],s[2]);s[2]=0
                s[1]=s[0]
            else:s[2]=s[1]-s[0]
        add(("BASE",per(d[i])))
        for k,fx in RULES.items():
            on=fx(F[i],c[i])
            if on and not prev[k]:add((k,per(d[i])))
            prev[k]=on
    for k,s in ST.items():
        if s[2]>0:
            qq=acc[k];qq[5]+=1;qq[6]+=s[2];qq[7]=max(qq[7],s[2])
os.makedirs("results",exist_ok=True)
with open("results/rules_net.csv","w",newline="") as o:
    w=csv.writer(o);w.writerow(["rule","period","n","win_net_pct","avg_gross","avg_net","avg_after_tax","avg_tax","cost_spread","cost_slippage","cost_commission","cost_fees","cost_swap","cost_total","dd_avg","dd_total","dd_max","dd_episodes"])
    for (k,p),q in sorted(acc.items()):
        if q[0]:w.writerow([k,p,q[0],round(100*q[1]/q[0],1),round(q[2]/q[0],3),round(q[3]/q[0],3),round(q[4]/q[0],3),round((q[3]-q[4])/q[0],3),round(P["spread"],3),round(P["slippage"],3),round(P["commission"],3),round(P["fees"],3),round(P["swap"],3),round(cc,3),round(q[6]/q[5],3) if q[5] else 0,round(q[6],2),round(q[7],2),q[5]])
print("wrote results/rules_net.csv  cost/round trip %.3f%%"%cc)
