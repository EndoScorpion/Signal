#!/usr/bin/env python3
"""Resumable daily-history fetcher with automatic fallback: Yahoo -> Stooq -> AlphaVantage. Safe chunks, no orders."""
import sys,os,time,json,csv,argparse,urllib.request,datetime
ap=argparse.ArgumentParser();ap.add_argument("symbols",nargs="*");ap.add_argument("--universe");ap.add_argument("--out",default="data/history");ap.add_argument("--range",default="10y")
a=ap.parse_args();os.makedirs(a.out,exist_ok=True)
S=list(a.symbols)
if a.universe:S+=[x for x in open(a.universe).read().split() if x]
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=20).read().decode()
def yahoo(s):
    j=json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range={a.range}&interval=1d"))["chart"]["result"][0];q=j["indicators"]["quote"][0]
    return [(datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"),q["open"][i],q["high"][i],q["low"][i],q["close"][i],q["volume"][i] or 0) for i,t in enumerate(j["timestamp"]) if q["close"][i] is not None]
def stooq(s):
    L=get(f"https://stooq.com/q/d/l/?s={s.lower()}.us&i=d").strip().splitlines()
    if len(L)<3:raise Exception("no data")
    return [tuple([r[0]]+[float(x) for x in r[1:6]]) for r in (l.split(",") for l in L[1:]) if len(r)>=5]
def yf(s):
    import yfinance as Y  # pip install yfinance (free, no key)
    d=Y.download(s,period=a.range,interval="1d",auto_adjust=False,progress=False)
    if d.empty:raise Exception("no data")
    d.columns=[c[0] if isinstance(c,tuple) else c for c in d.columns]
    return [(i.strftime("%Y-%m-%d"),r["Open"],r["High"],r["Low"],r["Close"],r["Volume"]) for i,r in d.iterrows()]
def av(s):
    k=os.environ.get("ALPHAVANTAGE_KEY");assert k,"no ALPHAVANTAGE_KEY"
    T=json.loads(get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol={s}&apikey={k}"))["Time Series (Daily)"]
    return [(d,float(T[d]["1. open"]),float(T[d]["2. high"]),float(T[d]["3. low"]),float(T[d]["4. close"]),float(T[d]["5. volume"])) for d in sorted(T)]
log=open("results_fetch_log.txt","a")
for i,s in enumerate(S):
    f=f"{a.out}/{s}.csv"
    if os.path.exists(f):continue
    for n,fn in (("yahoo",yahoo),("yfinance",yf),("stooq",stooq),("alphavantage",av)):
        try:
            r=fn(s)
            with open(f,"w",newline="") as o:
                w=csv.writer(o);w.writerow(["date","open","high","low","close","volume"]);w.writerows(r)
            print(s,n,len(r));log.write(f"{s} {n} {len(r)}\n");break
        except Exception as e:
            log.write(f"{s} {n} FAIL {e}\n")
    else:print(s,"ALL SOURCES FAILED")
    time.sleep(0.12)
    if (i+1)%3==0:time.sleep(0.45)
