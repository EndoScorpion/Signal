"""EUR/USD FXOpen ECN improvement cycle 2 (2026-10-20). LOCAL ONLY - win logic, do not commit.
Engine = clone_gen13 style (indicators/run/stats copied), Stack v2 = G11-3@22 + Mon17x22 + T82@21.
Data: mt4_tester2 EURUSD60.hst (aligned v2, FXOpen server clock UTC+2/+3 US-DST) -> converted to UTC.
Split: IS FXOpen 2024-26, OOS FXOpen 2020-23 (TwelveData file not on this PC), EXT FXOpen 2011-19 (extra unseen).
COST 0.00008 (8 pts) per trade. Research only; no orders, no MT4.
"""
import struct, sys, numpy as np, pandas as pd, warnings
from dateutil.easter import easter
from pandas.tseries.holiday import USFederalHolidayCalendar
warnings.filterwarnings('ignore')

COST = 0.00008
P = 0.00001
HST = r'C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server\EURUSD60.hst'

def load_hst(path):
    b = open(path, 'rb').read()
    dt = np.dtype([('t','<i8'),('o','<f8'),('h','<f8'),('l','<f8'),('c','<f8'),('v','<i8'),('s','<i4'),('rv','<i8')])
    a = np.frombuffer(b[148:148+(len(b)-148)//60*60], dtype=dt)
    srv = pd.to_datetime(a['t'], unit='s')
    utc = srv - pd.Timedelta(hours=2)
    ny = utc.tz_localize('UTC').tz_convert('America/New_York')
    dst = np.array([x.dst().total_seconds() > 0 for x in ny])
    utc = utc - pd.to_timedelta(dst.astype(int), unit='h')
    df = pd.DataFrame({'open':a['o'],'high':a['h'],'low':a['l'],'close':a['c']}, index=utc).sort_index()
    df = df[~df.index.duplicated()]
    df['hour']=df.index.hour; df['dow']=df.index.dayofweek; df['date']=df.index.date; df['year']=df.index.year
    return df

def add_indicators(df):
    p = P
    tr = np.maximum(df.high-df.low, np.maximum((df.high-df.close.shift()).abs(), (df.low-df.close.shift()).abs()))
    df['atr'] = tr.rolling(14).mean()
    df['atr_pct'] = df.atr.rolling(252).rank(pct=True)
    df['atr_med'] = df.atr.rolling(24*250, min_periods=500).median()
    df['ema120'] = df.close.ewm(span=120, adjust=False).mean()
    df['slope120'] = df.ema120.diff(5)
    cd = df.close.diff()/p
    mx = cd.rolling(12).max(); mn = cd.rolling(12).min()
    df['mmr'] = np.where(mx > 0, mn/mx, -9.0)
    C,H,L_ = df.close, df.high, df.low
    slp=[]; st=[]; ac=[]
    for S in (1,4,24):
        lo=L_.rolling(14*S).min(); hi=H.rolling(14*S).max()
        K=(100*(C-lo)/(hi-lo)).rolling(3).mean()
        for pdd in (2,5,10):
            ma=C.rolling(pdd*S).mean(); s0=(ma-ma.shift(S))/p
            for sh in (0,1):
                s=s0.shift(sh*S); a=s-s.shift(S)
                slp.append(s); st.append(K.shift(sh*S)); ac.append(a)
    SL=np.column_stack([x.values for x in slp]); ST=np.column_stack([x.values for x in st]); AC=np.column_stack([x.values for x in ac])
    with np.errstate(divide='ignore', invalid='ignore'):
        SSR=np.column_stack([np.where(SL[:,k]!=0, SL[:,0]/SL[:,k], 0) for k in (1,6,8,10,12,14,16)])
    df['minssr']=np.nanmin(SSR,axis=1)
    df['maxslp3']=np.nanmax(SL[:,12:18],axis=1); df['maxac3']=np.nanmax(AC[:,12:18],axis=1)
    df['npc']=(SL>0).sum(axis=1).astype(float)
    df['st0']=ST[:,0]
    df['lossyl']=((df.st0<20)&((df.maxslp3>0)|(df.maxac3>0))&(df.npc>0)).astype(float)
    df['rng']=df.high-df.low
    for c in ['atr','atr_pct','atr_med','ema120','slope120','mmr','minssr','maxslp3','maxac3','npc','st0','lossyl','rng']:
        df[c]=df[c].shift(1)
    prev_close=df.groupby('date').close.last().shift(1)
    df['prev_close']=df.date.map(prev_close)
    return df

# ---------- calendars (approximate, from memory - verify before live use) ----------
FOMC = """2011-01-26 2011-03-15 2011-04-27 2011-06-22 2011-08-09 2011-09-21 2011-11-02 2011-12-13
2012-01-25 2012-03-13 2012-04-25 2012-06-20 2012-08-01 2012-09-13 2012-10-24 2012-12-12
2013-01-30 2013-03-20 2013-05-01 2013-06-19 2013-07-31 2013-09-18 2013-10-30 2013-12-18
2014-01-29 2014-03-19 2014-04-30 2014-06-18 2014-07-30 2014-09-17 2014-10-29 2014-12-17
2015-01-28 2015-03-18 2015-04-29 2015-06-17 2015-07-29 2015-09-17 2015-10-28 2015-12-16
2016-01-27 2016-03-16 2016-04-27 2016-06-15 2016-07-27 2016-09-21 2016-11-02 2016-12-14
2017-02-01 2017-03-15 2017-05-03 2017-06-14 2017-07-26 2017-09-20 2017-11-01 2017-12-13
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08 2018-12-19
2019-01-30 2019-03-20 2019-05-01 2019-06-19 2019-07-31 2019-09-18 2019-10-30 2019-12-11
2020-01-29 2020-03-03 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14
2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18
2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16""".split()
CPI_FRI = """2015-01-16 2015-04-17 2015-05-22 2015-07-17 2016-02-19 2016-07-15 2016-09-16 2017-04-14 2017-05-12
2017-07-14 2017-08-11 2017-10-13 2018-01-12 2018-08-10 2019-01-11 2019-05-10 2020-04-10 2020-09-11 2021-12-10
2022-06-10 2025-10-24""".split()
fomc_fri = set()
for d in pd.to_datetime(FOMC):
    fomc_fri.add((d + pd.Timedelta(days=(4-d.dayofweek) % 7)).date())
cpi_fri = set(pd.to_datetime(CPI_FRI).date)
hol = set(USFederalHolidayCalendar().holidays('2009-01-01','2026-12-31').date)
for y in range(2009,2027):
    e = pd.Timestamp(easter(y)); hol |= {(e-pd.Timedelta(days=2)).date(), (e+pd.Timedelta(days=1)).date()}
def hol_adj(d):
    d = pd.Timestamp(d)
    if (d.month==12 and d.day>=24) or (d.month==1 and d.day<=2): return True
    return any((d+pd.Timedelta(days=k)).date() in hol for k in (-3,-1,0,1,3))

# ---------- trade engine ----------
def run(df, mask, dr, exit_hour, split=None, be=None, cat=None):
    O=df.open.values; H=df.high.values; L=df.low.values; C=df.close.values
    HR=df.hour.values; A=df.atr.values; idx=df.index; N=len(df)
    exits = sorted(split) if split else [exit_hour]
    rows=[]; last_exit=-1
    for i in np.where(mask)[0]:
        if i<=last_exit or i+1>=N: continue
        ep=O[i]; atr=A[i]; armed=False; legs=[]; j=i; stopped=None
        catp = ep-dr*cat*atr if cat else None
        while len(legs)<len(exits):
            j+=1
            if j>=N or j-i>=24: break
            if catp is not None and ((dr>0 and L[j]<=catp) or (dr<0 and H[j]>=catp)): stopped=catp; break
            if armed and ((dr>0 and L[j]<=ep) or (dr<0 and H[j]>=ep)): stopped=ep; break
            if HR[j] in exits: legs.append(C[j])
            if be and ((dr>0 and H[j]-ep>=be*atr) or (dr<0 and ep-L[j]>=be*atr)): armed=True
        if stopped is not None: legs += [stopped]*(len(exits)-len(legs))
        if len(legs)<len(exits): continue
        last_exit=j
        pnl=np.mean([(x-ep)*dr for x in legs])-COST
        rows.append((idx[i],dr,pnl,idx[i].year,atr,df.atr_pct.values[i],df.atr_med.values[i]))
    return pd.DataFrame(rows, columns=['t','dir','pnl','year','atr','atr_pct','atr_med'])

def ok(df):
    return ~np.isnan(df.atr_pct.values)&~np.isnan(df.prev_close.values)&~np.isnan(df.mmr.values)&~np.isnan(df.minssr.values)
def first_fri(df): return np.array([t.day<=7 for t in df.index])

def m_g11(df, thr=0.3):
    m=ok(df)&(df.hour.values==14)&(df.dow.values==4)&((df.open.values-df.prev_close.values)>thr*df.atr.values)
    return m&~first_fri(df)&(df.mmr.values>=-1.0)&(df.slope120.values>=-0.1*df.atr.values)
def m_mon17(df):
    return ok(df)&(df.hour.values==17)&(df.dow.values==0)&((df.open.values-df.prev_close.values)<-0.3*df.atr.values)&(df.slope120.values<=0.1*df.atr.values)
def m_t82(df):
    m=ok(df)&np.isin(df.hour.values,[15,16])&(df.dow.values==0)&(df.lossyl.values>0)&(df.minssr.values>-2)
    # first hit per day
    s=pd.Series(m,index=df.index); first=s&~s.groupby(df.date.values).cumsum().shift(fill_value=0).astype(bool)
    return first.values & m

def news_skip(df, mask, kind):
    d=df.date.values
    if kind in ('cpi','news'): mask=mask&~np.isin(d,list(cpi_fri))
    if kind in ('fomc','news'): mask=mask&~np.isin(d,list(fomc_fri))
    if kind in ('hol','news'): mask=mask&~np.array([hol_adj(x) for x in d])
    return mask
def bigbar_skip(df, mask, k=1.5): return mask&~(df.rng.values>k*df.atr.values)

def stack(df, g11_thr=0.3, g11_exit=22, split=None, be=None, cat=None, skip=None, bigbar=False):
    legs=[]
    for name,m,dr,ex in [('G11-3',m_g11(df,g11_thr),-1,g11_exit),('Mon17',m_mon17(df),1,22),('T82',m_t82(df),1,21)]:
        if skip: m=news_skip(df,m,skip)
        if bigbar: m=bigbar_skip(df,m)
        t=run(df,m,dr,ex,split=split,be=be,cat=cat); t['leg']=name; legs.append(t)
    return pd.concat(legs).sort_values('t').reset_index(drop=True)

def stats(tr, w=None):
    if len(tr)==0: return dict(n=0,wr=0,pf=0,avg=0,net=0,dd=0,yr={})
    p=tr.pnl.values/P*(w if w is not None else 1)
    g=p[p>0].sum(); l=-p[p<0].sum(); eq=np.cumsum(p); dd=(np.maximum.accumulate(np.r_[0,eq])[1:]-eq).max()
    yr={}
    for y in sorted(tr.year.unique()):
        q=p[tr.year.values==y]; yr[y]=round(q[q>0].sum()/-q[q<0].sum(),2) if (q<0).any() else 99.0
    return dict(n=len(p),wr=round(100*(p>0).mean(),1),pf=round(g/l,2) if l>0 else 99.0,avg=round(p.mean(),1),net=round(p.sum()),dd=round(dd),yr=yr)

if __name__=='__main__':
    df=add_indicators(load_hst(HST))
    SEG={'IS':(2024,2026),'OOS':(2020,2023),'EXT':(2011,2019)}
    def seg(tr,s): a,b=SEG[s]; return tr[(tr.year>=a)&(tr.year<=b)]
    out=[]
    def report(label, tr, w=None, legs=False):
        r={'label':label}
        for s in SEG:
            x=seg(tr,s); ww=None if w is None else w[x.index]
            r[s]=stats(x,ww)
        oy=r['OOS']['yr']; r['verdict']='REJECT' if (r['OOS']['n']<30 or any(v<1.0 for v in oy.values())) else 'ok'
        out.append(r)
        o,i,e=r['OOS'],r['IS'],r['EXT']
        print(f"{label:34s} OOS n={o['n']} WR={o['wr']} PF={o['pf']} avg={o['avg']} net={o['net']} DD={o['dd']} yr={'/'.join(str(v) for v in o['yr'].values())} | IS n={i['n']} PF={i['pf']} avg={i['avg']} DD={i['dd']} | EXT n={e['n']} PF={e['pf']} | {r['verdict']}")
        if legs:
            for lg in ['G11-3','Mon17','T82']:
                x=tr[tr.leg==lg]; print(f"     leg {lg:6s} OOS {stats(seg(x,'OOS'))} | IS n={stats(seg(x,'IS'))['n']} PF={stats(seg(x,'IS'))['pf']} | EXT n={stats(seg(x,'EXT'))['n']} {stats(seg(x,'EXT'))['pf']}")
        return r
    base=stack(df); report('BASE Stack v2',base,legs=True)
    print('-- 1 split exit'); report('SPLIT 21/22 all legs',stack(df,split=[21,22]))
    print('-- 2 loss prevention')
    report('BE after +0.5ATR',stack(df,be=0.5))
    report('CAT stop 2.5ATR',stack(df,cat=2.5))
    report('BE0.5 + CAT2.5',stack(df,be=0.5,cat=2.5))
    report('skip prev-bar range>1.5ATR',stack(df,bigbar=True))
    report('skip CPI Fri',stack(df,skip='cpi'))
    report('skip FOMC-week Fri',stack(df,skip='fomc'))
    report('skip holiday-adjacent',stack(df,skip='hol'))
    report('skip CPI+FOMC+holiday',stack(df,skip='news'))
    print('-- 3 G11 threshold @22')
    for th in (0.25,0.3,0.35,0.4): report(f'G11 thr {th}',stack(df,g11_thr=th),legs=False)
    for th in (0.25,0.3,0.35,0.4):
        x=stack(df,g11_thr=th); x=x[x.leg=='G11-3']; print(f"     G11-only thr {th}: OOS {stats(seg(x,'OOS'))} IS {stats(seg(x,'IS'))} EXT {stats(seg(x,'EXT'))['pf']}")
    print('-- 4 vol-scaled size (weights mean-normalised per segment)')
    W={'tier pct<.33=1.25 >.67=0.75':np.where(base.atr_pct<0.33,1.25,np.where(base.atr_pct>0.67,0.75,1.0)),
       'cut pct>0.8 -> 0.5':np.where(base.atr_pct>0.8,0.5,1.0),
       'inverse ATR clip .5-1.5':np.clip(base.atr_med/base.atr,0.5,1.5)}
    for k,w in W.items():
        w=pd.Series(w,index=base.index).fillna(1.0)
        for s in SEG:
            ix=seg(base,s).index; w[ix]=w[ix]/w[ix].mean()
        report('SIZE '+k,base,w=w)
    print('-- 5 rolling 12m PF (base, all years 2011-2026, monthly steps)')
    b=base.set_index('t'); months=pd.date_range('2011-12-31','2026-10-31',freq='ME'); rows=[]
    for m in months:
        x=b[(b.index>m-pd.DateOffset(months=12))&(b.index<=m)].pnl.values
        if len(x)>=10: rows.append((m.strftime('%Y-%m'),len(x),round(x[x>0].sum()/-x[x<0].sum(),2) if (x<0).any() else 99.0))
    R=pd.DataFrame(rows,columns=['end','n','pf'])
    print(f"windows={len(R)} min={R.pf.min()} ({R.end[R.pf.idxmin()]}) median={R.pf.median()} share<1.0={round((R.pf<1).mean()*100,1)}% share<1.3={round((R.pf<1.3).mean()*100,1)}%")
    print(R[R.end.str.endswith(('-03','-06','-09','-12'))|(R.end>='2025-10')].to_string(index=False))
    R.to_csv(r'C:\Users\endos\Signal\data\eurusd_cycle2_rolling12m.csv',index=False)
