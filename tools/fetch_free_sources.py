#!/usr/bin/env python3
"""Keyless real-data fetchers (run on a machine with network; the hosted sandbox blocks stooq.com / finance.yahoo.com).
  python3 tools/fetch_free_sources.py stooq  SPY.US,AAPL.US d          -> data/stooq_<sym>_<i>_<stamp>.csv (+ history_<stamp>.csv rows)
  python3 tools/fetch_free_sources.py yahoo  HYPE32196-USD,SPY 1h 60d  -> data/<sym>_<interval>_<stamp>.json ([t_ms,o,h,l,c]) + seed merge
Stooq: https://stooq.com/q/d/l/?s=<sym>&i=<d|w|m>  (daily/weekly/monthly CSV; intraday needs their site, not the CSV endpoint).
Yahoo: free chart API (no key). pip install yfinance is optional; this uses the raw endpoint so nothing extra is needed.
Output is merged into data/slc_win2_ext.json (key "<SYM>|<TF>", cost class by symbol: crypto for *-USD, else stock) - never overwrites longer series."""
import sys,json,os,time,csv,urllib.request,datetime
def stamp():
    import zoneinfo;d=datetime.datetime.now(zoneinfo.ZoneInfo('America/New_York'));return d.strftime('%Y%m%d-%H%M')
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'});return urllib.request.urlopen(req,timeout=30).read().decode('utf-8')
def merge_ext(key,bars,cls,src):
    p='data/slc_win2_ext.json';ext={}
    if os.path.exists(p): ext=json.load(open(p))
    old=ext.get(key,{}).get('b',[]);m={b[0]:b for b in old}
    for b in bars: m[b[0]]=b
    ext[key]={'cls':cls,'src':src,'b':[m[t] for t in sorted(m)]};json.dump(ext,open(p,'w'));return len(ext[key]['b'])
def stooq(syms,i):
    st=stamp();rows=['source,symbol,timeframe,timestamp_ms,time_utc,open,high,low,close,dividend']
    for s in syms.split(','):
        txt=get(f'https://stooq.com/q/d/l/?s={s.lower()}&i={i}');open(f'data/stooq_{s}_{i}_{st}.csv','w').write(txt)
        bars=[]
        for r in csv.DictReader(txt.splitlines()):
            try: t=int(datetime.datetime.strptime(r['Date'],'%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp()*1000);bars.append([t,float(r['Open']),float(r['High']),float(r['Low']),float(r['Close'])])
            except Exception: pass
        tf={'d':'D1','w':'W1','m':'MN'}[i];sym=s.split('.')[0].upper()
        for b in bars: rows.append(','.join(['stooq',sym,tf,str(b[0]),datetime.datetime.utcfromtimestamp(b[0]/1000).isoformat()+'Z',*map(str,b[1:]),'']))
        n=merge_ext(f'{sym}|{tf}',bars,'stock','stooq');print(s,i,len(bars),'bars ->',n,'in seed')
    open(f'data/history_{st}.csv','w').write('\n'.join(rows))
def yahoo(syms,interval,rng):
    st=stamp();TF={'15m':'M15','30m':'M30','60m':'M60','1h':'M60','2h':'M120','4h':'H4','1d':'D1'}
    for s in syms.split(','):
        j=json.loads(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{s}?interval={interval}&range={rng}'))['chart']['result'][0]
        q=j['indicators']['quote'][0];bars=[[t*1000,q['open'][k],q['high'][k],q['low'][k],q['close'][k]] for k,t in enumerate(j['timestamp']) if q['close'][k] is not None]
        json.dump(bars,open(f'data/{s}_{interval}_{st}.json','w'));cls='crypto' if s.endswith('-USD') else 'stock'
        n=merge_ext(f"{s.split('-')[0].split('.')[0].upper()}|{TF.get(interval,interval)}",bars,cls,'yahoo');print(s,interval,len(bars),'bars ->',n,'in seed')
if __name__=='__main__':
    a=sys.argv[1:]
    if not a: print(__doc__);sys.exit(0)
    os.makedirs('data',exist_ok=True)
    if a[0]=='stooq': stooq(a[1],a[2] if len(a)>2 else 'd')
    elif a[0]=='yahoo': yahoo(a[1],a[2] if len(a)>2 else '1h',a[3] if len(a)>3 else '60d')
    else: print(__doc__)
