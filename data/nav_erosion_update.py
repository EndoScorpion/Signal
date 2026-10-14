# NAV erosion tracker + dividend-capture event study. Research only. Run: python -E -P nav_erosion_update.py [--study]
# Source: Yahoo chart API (unofficial, split-adjusted OHLC, dividends = ex-dates). Append-only CSV tracker.
import urllib.request,json,time,csv,os,sys,datetime as dt,statistics as S
HERE=os.path.dirname(os.path.abspath(__file__))
TRACK=os.path.join(HERE,"nav_erosion_tracker.csv")
WEEKLY="COYY MAAY IOYY HOYY MST SMYY RGYY MTYY QBY MARO RTYY TSYY WNTR CRCO HMYY SEMY HIYY MSTY ULTI RBLY RDYY MSTW PLYY SMCY CONY BBYY COIW HOOY CVNY DRAY FIAT AMYY XBTY NUGY AIYY NVYY HOOW YBTY ULTY SLTY TSII ARMW TSLY YETH XYZY CRSH TSLW LFGY AMDY BABO GDXY GMEY YBIT YBST AVGW BABW PLTY GDXW DIPS NFLY PYPY PLTW SNOY NFLW FBYY YMAX YBTC CWY AZYY OARK MUYY UBEW CRY NVII TQQY AMDW NVDY TSMY USOY AMZY TOPW NVDW GOOY BLOX FBY YMAG GOLI CEPI QLDY RDTY RDTE QDTE BCCC CHPY AMZW MRNY GOOW YSPY METW IWMY XDTE".split()
OTHER="JEPI JEPQ QYLD XYLD RYLD SPYI QQQI DIVO SDIV SCHD VYM HDV DVY O MAIN STAG ARCC OBDC PSEC BXMT AGNC NLY ET EPD VZ T MO PFE KO XOM CVX PM ABBV IBM KMI MPW LTC GOOD BHP RIO NVO TM HSBC BTI PBR VALE EWA DIA SPY JPM WMT".split()
def get(s):
    for _ in range(2):
        try:
            r=urllib.request.Request("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=2y&interval=1d&events=div"%s,headers={"User-Agent":"Mozilla/5.0"})
            res=json.load(urllib.request.urlopen(r,timeout=20))["chart"]["result"][0]
            q=res["indicators"]["quote"][0]
            d=[dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d") for t in res["timestamp"]]
            divs={dt.datetime.utcfromtimestamp(v["date"]).strftime("%Y-%m-%d"):v["amount"] for v in res.get("events",{}).get("dividends",{}).values()}
            rows=[(a,b,c) for a,b,c in zip(d,q["open"],q["close"])]
            rows=[r for r in rows if r[1] and r[2]]
            return rows,divs
        except Exception: time.sleep(2)
    return None,None
def freq(divs):
    ks=sorted(divs)
    if len(ks)<3: return "irregular"
    g=S.median((dt.date.fromisoformat(b)-dt.date.fromisoformat(a)).days for a,b in zip(ks,ks[1:]))
    return "weekly" if g<=9 else "monthly" if g<=40 else "quarterly" if g<=110 else "semiannual/annual"
def tracker(sym,rows,divs,today):
    last=rows[-1][0];cut=(dt.date.fromisoformat(last)-dt.timedelta(days=365)).isoformat()
    w=[r for r in rows if r[0]>=cut]
    if len(w)<100: return None
    p0=w[0][2];p1=w[-1][2];dv=sorted((k,v) for k,v in divs.items() if k>=w[0][0])
    ds=sum(v for _,v in dv);h=len(dv)//2
    tr="n/a" if h<1 else "%.1f%%"%((S.mean(v for _,v in dv[h:])/S.mean(v for _,v in dv[:h])-1)*100)
    pc=(p1/p0-1)*100;dp=ds/p0*100
    note="PRICE FELL MORE THAN DISTRIBUTIONS PAID" if pc+dp<0 else ""
    return [today,sym,freq(divs),"%.4f"%p0,"%.4f"%p1,"%.1f"%pc,"%.1f"%dp,"%.1f"%(pc+dp),tr,"window %s..%s n_dist=%d; %s"%(w[0][0],last,len(dv),note)]
def study(rows,divs):
    d=[r[0] for r in rows];o=[r[1] for r in rows];c=[r[2] for r in rows]
    ev=[];
    for ex,dv in sorted(divs.items()):
        if ex not in d: continue
        i=d.index(ex)
        if i<1 or i+4>=len(d): continue
        pc=c[i-1];s=[o[i],c[i]]+[c[i+k] for k in range(1,5)]
        ev.append((ex,dv/pc*1e4,(pc-c[i])/pc*1e4,[(x-pc+dv)/pc*1e4 for x in s]))
    return ev
EX=["ex_open","ex_close","+1d","+2d","+3d","+4d"]
if __name__=="__main__":
    today=dt.date.today().isoformat();new=not os.path.exists(TRACK)
    syms=[(s,"w") for s in WEEKLY]+[(s,"o") for s in OTHER]
    out=[];trk=[]
    for s,_ in syms:
        rows,divs=get(s);time.sleep(0.3)
        if not rows or not divs: print("skip",s);continue
        t=tracker(s,rows,divs,today)
        if t: trk.append(t)
        if "--study" in sys.argv:
            ev=study(rows,divs)
            if len(ev)<8: continue
            r={"symbol":s,"freq":freq(divs),"n":len(ev),"div_bps":S.mean(e[1] for e in ev),"drop_bps":S.mean(e[2] for e in ev)}
            hi=len(ev)//2
            for k,nm in enumerate(EX):
                g=[e[3][k] for e in ev]
                for cst in (4,20):
                    n=[x-cst for x in g]
                    r["%s_net%d"%(nm,cst)]=S.mean(n)
                    if cst==20: r[nm+"_win20"]=100*sum(x>0 for x in n)/len(n);r[nm+"_worst20"]=min(n);r[nm+"_h1_20"]=S.mean(n[:hi]);r[nm+"_h2_20"]=S.mean(n[hi:])
            out.append(r)
    with open(TRACK,"a",newline="") as f:
        w=csv.writer(f)
        if new: w.writerow("date_checked,symbol,payer_frequency,price_start,price_now,price_change_pct,distributions_sum_pct_of_start,total_return_proxy_pct,distribution_per_share_trend,notes".split(","))
        w.writerows(trk)
    print("tracker rows appended:",len(trk))
    if out:
        p=os.environ.get("STUDY_OUT","study_results.json");json.dump(out,open(p,"w"));print("study",len(out),"->",p)
