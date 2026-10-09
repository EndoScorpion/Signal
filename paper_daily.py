#!/usr/bin/env python3
"""Daily PAPER bot (forward-only). Never places orders: no broker calls at all, it only reads CSV bars.
Rules: S2 daily RSI<25 (hold 3d); S4 daily below BB & Stoch<10 & close>SMA50 (hold 3d);
C1 crypto H1 dip-rebound: RSI<30 & 12-bar return < -2% (hold 4 bars, stop -1.5%).
Signal on a closed bar -> entry next bar open -> exit at open after hold (or stop). Costs from cost_model.json.
Ledger results/paper_ledger.csv keyed by rule+sym+signal_time, so reruns never duplicate.
Usage: python3 paper_daily.py --start 2026-10-10   |   python3 paper_daily.py --report"""
import csv,glob,json,os,argparse,collections
ap=argparse.ArgumentParser();ap.add_argument("--daily",default="data/history");ap.add_argument("--h1",default="data/crypto_h1")
ap.add_argument("--cost",default="cost_model.json");ap.add_argument("--ledger",default="results/paper_ledger.csv")
ap.add_argument("--start",default="2026-10-10",help="only signals on/after this date (forward test)");ap.add_argument("--report",action="store_true")
a=ap.parse_args();C=json.load(open(a.cost))
TAX=C["tax_short_term_pct"]/100
RT_STOCK=(C["spread_bps"]["stock"]+2*C["slippage_bps_per_side"]+C["reg_fee_bps_sell"])/100   # % round trip
RT_CRYPTO=(C["spread_bps"]["crypto"]+2*C["slippage_bps_per_side"]+2*C["crypto_fee_bps_per_side"])/100
COLS=["rule","sym","signal_time","entry_time","entry","exit_time","exit","gross_pct","net_pct","after_tax_pct","status"]
def load(fn):
    R=list(csv.DictReader(open(fn)));k="date" if "date" in R[0] else "time_utc"
    return [(r[k],float(r["open"]),float(r["high"]),float(r["low"]),float(r["close"])) for r in R]
def sma(x,n,i):return sum(x[i-n+1:i+1])/n
def feat(c,h,l,i):
    f={}
    if i>=14:
        g=[max(c[j]-c[j-1],0) for j in range(i-13,i+1)];d=[max(c[j-1]-c[j],0) for j in range(i-13,i+1)]
        ag,al=sum(g)/14,sum(d)/14;f["rsi"]=100 if al==0 else 100-100/(1+ag/al)
        hh,ll=max(h[i-13:i+1]),min(l[i-13:i+1]);f["stoch"]=50 if hh==ll else 100*(c[i]-ll)/(hh-ll)
    if i>=12:f["r12"]=100*(c[i]/c[i-12]-1)
    if i>=20:m=sma(c,20,i);sd=(sum((x-m)**2 for x in c[i-19:i+1])/20)**.5;f["bbl"]=m-2*sd
    if i>=50:f["up"]=c[i]>sma(c,50,i)
    return f
RULES={"S2":(lambda f,p:f.get("rsi",99)<25,3,None,RT_STOCK),
       "S4":(lambda f,p:p<f.get("bbl",0) and f.get("stoch",50)<10 and f.get("up",False),3,None,RT_STOCK),
       "C1":(lambda f,p:f.get("rsi",99)<30 and f.get("r12",0)<-2,4,1.5,RT_CRYPTO)}
L={}
if os.path.exists(a.ledger):
    for r in csv.DictReader(open(a.ledger)):
        if "rule" in r and r.get("signal_time"):L[(r["rule"],r["sym"],r["signal_time"])]=r
def net(g,rt):n=g-rt;return n,(n*(1-TAX) if n>0 else n)
def run(rule,files):
    fn_,hold,stop,rt=RULES[rule]
    for fn in files:
        s=os.path.basename(fn)[:-4];B=load(fn);t=[b[0] for b in B];c=[b[4] for b in B];h=[b[2] for b in B];l=[b[3] for b in B]
        for i in range(len(B)-1):   # last bar may still be forming? signal bars must have a next bar
            if t[i][:10]<a.start:continue
            k=(rule,s,t[i])
            if k in L and L[k]["status"]=="closed":continue
            if k not in L and not fn_(feat(c,h,l,i),c[i]):continue
            e=B[i+1][1];r=dict(rule=rule,sym=s,signal_time=t[i],entry_time=t[i+1],entry=round(e,6),exit_time="",exit="",gross_pct="",net_pct="",after_tax_pct="",status="open")
            x=xt=None
            for j in range(i+1,min(i+1+hold,len(B))):
                if stop and B[j][3]<=e*(1-stop/100):x,xt=e*(1-stop/100),t[j];break
            if x is None and i+1+hold<len(B):x,xt=B[i+1+hold][1],t[i+1+hold]
            if x is not None:
                g=(x/e-1)*100;n,at=net(g,rt);r.update(exit_time=xt,exit=round(x,6),gross_pct=round(g,3),net_pct=round(n,3),after_tax_pct=round(at,3),status="closed")
            L[k]=r
def report():
    M=collections.defaultdict(list)
    for r in L.values():
        if r["status"]=="closed":M[(r["exit_time"][:7],r["rule"])].append((float(r["net_pct"]),float(r["after_tax_pct"])))
    out=["| month | rule | n | win% net | avg net % | avg after tax % |","|--|--|--|--|--|--|"]
    for (m,ru),v in sorted(M.items()):
        n=len(v);out.append(f"| {m} | {ru} | {n} | {100*sum(x>0 for x,_ in v)/n:.1f} | {sum(x for x,_ in v)/n:.3f} | {sum(y for _,y in v)/n:.3f} |")
    op=sum(r["status"]=="open" for r in L.values())
    txt="# Paper bot monthly report (forward test, net of cost_model.json, not advice)\n\n"+"\n".join(out)+f"\n\nOpen paper positions: {op}. Rules with n<30 are not conclusive (CLAUDE.md).\n"
    open("results/PAPER_REPORT.md","w").write(txt);print(txt)
if not a.report:
    run("S2",glob.glob(a.daily+"/*.csv"));run("S4",glob.glob(a.daily+"/*.csv"));run("C1",glob.glob(a.h1+"/*.csv"))
    os.makedirs(os.path.dirname(a.ledger),exist_ok=True)
    with open(a.ledger,"w",newline="") as o:
        w=csv.DictWriter(o,COLS);w.writeheader();[w.writerow(r) for r in sorted(L.values(),key=lambda r:r["signal_time"])]
    print("ledger rows",len(L),"open",sum(r["status"]=="open" for r in L.values()))
report()
