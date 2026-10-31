#!/usr/bin/env python3
"""
Extended winner analysis: chaos, dynamic params, news, data integrity,
timing, institutional flows, MM patterns, CB proxy.
"""
import csv, math, sys, datetime
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

SPREAD_PIPS = 1.0
COMMISSION  = 0.00007
SLIPPAGE    = 0.00003
COST_RT     = (SPREAD_PIPS * 0.0001) + COMMISSION + SLIPPAGE

@dataclass
class Bar:
    date: str
    o: float; h: float; l: float; c: float; v: float
    dow: int = 0   # 0=Mon..4=Fri

def load_eurusd(path: str) -> List[Bar]:
    bars = []
    with open(path) as f:
        lines = f.readlines()
    for line in lines[3:]:
        parts = line.strip().split(',')
        if len(parts) < 6: continue
        try:
            date = parts[0]
            c,h,l,o = float(parts[1]),float(parts[2]),float(parts[3]),float(parts[4])
            v = float(parts[5]) if parts[5] else 0.0
            if c > 0:
                dt = datetime.date.fromisoformat(date)
                bars.append(Bar(date, o, h, l, c, v, dow=dt.weekday()))
        except:
            pass
    return bars

# ---- Indicators ----
def ema(data, n):
    r=[None]*len(data)
    if len(data)<n: return r
    r[n-1]=sum(data[:n])/n
    k=2/(n+1)
    for i in range(n,len(data)):
        r[i]=data[i]*k+r[i-1]*(1-k)
    return r

def sma(data, n):
    r=[None]*len(data)
    for i in range(n-1,len(data)):
        window=[x for x in data[i-n+1:i+1] if x is not None]
        if len(window)==n: r[i]=sum(window)/n
    return r

def stdev(data, n):
    r=[None]*len(data)
    for i in range(n-1,len(data)):
        s=data[i-n+1:i+1]; m=sum(s)/n
        r[i]=math.sqrt(sum((x-m)**2 for x in s)/n)
    return r

def atr_series(bars, n=14):
    trs=[None]
    for i in range(1,len(bars)):
        trs.append(max(bars[i].h-bars[i].l, abs(bars[i].h-bars[i-1].c), abs(bars[i].l-bars[i-1].c)))
    r=[None]*len(bars)
    if len(bars)>=n+1:
        r[n]=sum(trs[1:n+1])/n
        for i in range(n+1,len(bars)):
            r[i]=(r[i-1]*(n-1)+trs[i])/n
    return r

def rsi_series(closes, n=14):
    r=[None]*len(closes)
    if len(closes)<n+1: return r
    gains,losses=[],[]
    for i in range(1,len(closes)):
        d=closes[i]-closes[i-1]
        gains.append(max(d,0)); losses.append(max(-d,0))
    ag=sum(gains[:n])/n; al=sum(losses[:n])/n
    def rs2r(ag,al): return 100-100/(1+ag/al) if al>0 else 100
    r[n]=rs2r(ag,al)
    for i in range(n,len(gains)):
        ag=(ag*(n-1)+gains[i])/n; al=(al*(n-1)+losses[i])/n
        r[i+1]=rs2r(ag,al)
    return r

def hurst(series, min_lag=2, max_lag=20):
    """R/S Hurst exponent estimate, returns None if insufficient data"""
    n=len(series)
    if n<max_lag*2: return None
    lags=range(min_lag,min(max_lag,n//2))
    rs_list=[]
    for lag in lags:
        chunks=[series[i:i+lag] for i in range(0,n-lag,lag)]
        if not chunks: continue
        rs_vals=[]
        for chunk in chunks:
            m=sum(chunk)/len(chunk)
            dev=[x-m for x in chunk]
            cumdev=[sum(dev[:i+1]) for i in range(len(dev))]
            R=max(cumdev)-min(cumdev)
            S=math.sqrt(sum((x-m)**2 for x in chunk)/len(chunk))
            if S>0: rs_vals.append(R/S)
        if rs_vals: rs_list.append((math.log(lag), math.log(sum(rs_vals)/len(rs_vals))))
    if len(rs_list)<3: return None
    xs=[x for x,y in rs_list]; ys=[y for x,y in rs_list]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den=sum((x-mx)**2 for x in xs)
    return num/den if den>0 else None

# ==================== PHASE 1: DATA INTEGRITY ====================
def check_integrity(bars):
    issues=[]
    prev_dates=set()
    for i,b in enumerate(bars):
        if b.date in prev_dates:
            issues.append(f"DUPLICATE {b.date}")
        prev_dates.add(b.date)
        if b.h<b.l:
            issues.append(f"OHLC_VIOLATION {b.date} H={b.h}<L={b.l}")
        if b.c>b.h or b.c<b.l:
            issues.append(f"CLOSE_OUTSIDE {b.date}")
        if b.o>b.h or b.o<b.l:
            issues.append(f"OPEN_OUTSIDE {b.date}")
        if b.c<=0 or b.o<=0 or b.h<=0 or b.l<=0:
            issues.append(f"ZERO_BAR {b.date}")
    at=atr_series(bars,14)
    spike_dates=set()
    for i in range(15,len(bars)):
        if at[i] and at[i]>0:
            rng=bars[i].h-bars[i].l
            if rng>10*at[i]:
                issues.append(f"SPIKE {bars[i].date} range={rng:.5f} atr={at[i]:.5f}")
                spike_dates.add(bars[i].date)
            if i>0:
                gap=abs(bars[i].o-bars[i-1].c)
                if gap>5*at[i]:
                    issues.append(f"ABN_GAP {bars[i].date} gap={gap:.5f}")
    return issues, spike_dates

# ==================== PHASE 2: CHAOS PROFILES ====================
def chaos_profile(bars, signals, hold, label):
    """For each signal trade compute chaos metrics at entry; split winners vs losers"""
    closes=[b.c for b in bars]
    at=atr_series(bars,14)
    win_chaos=[]; loss_chaos=[]
    win_range=[]; loss_range=[]
    win_hurst=[]; loss_hurst=[]
    win_atr_reg=[]; loss_atr_reg=[]

    for idx,direction,entry in signals:
        if idx<30 or at[idx] is None: continue
        exit_idx=min(idx+hold,len(bars)-1)
        exit_p=bars[exit_idx].c
        net=(exit_p-entry)*direction - COST_RT
        is_win = net>0

        # LYA chaos: rolling vol of rets over 20 bars
        window=closes[idx-20:idx]
        rets=[(window[j]-window[j-1])/window[j-1] for j in range(1,len(window))]
        chaos=math.sqrt(sum(r*r for r in rets)/len(rets)) if rets else 0

        # ATR regime: current ATR vs 50-bar avg ATR
        at_window=[at[k] for k in range(max(0,idx-50),idx) if at[k]]
        atr_reg=at[idx]/( sum(at_window)/len(at_window) ) if at_window and at[idx] else 1.0

        # Hurst
        h=hurst(window)

        # Bar range at entry
        entry_range=(bars[idx].h-bars[idx].l)/(at[idx] if at[idx] else 1)

        bucket = win_chaos if is_win else loss_chaos
        bucket.append(chaos)
        (win_range if is_win else loss_range).append(entry_range)
        if h: (win_hurst if is_win else loss_hurst).append(h)
        (win_atr_reg if is_win else loss_atr_reg).append(atr_reg)

    def s(lst): return f"{sum(lst)/len(lst):.4f}" if lst else "n/a"
    return {
        'label': label,
        'win_chaos_avg': s(win_chaos), 'loss_chaos_avg': s(loss_chaos),
        'win_range_avg': s(win_range), 'loss_range_avg': s(loss_range),
        'win_hurst': s(win_hurst), 'loss_hurst': s(loss_hurst),
        'win_atr_reg': s(win_atr_reg), 'loss_atr_reg': s(loss_atr_reg),
        'nw': len(win_chaos), 'nl': len(loss_chaos)
    }

# ==================== PHASE 3: DYNAMIC PARAMS ====================
def run_backtest_pnl(signals, bars, hold):
    trades=[]
    for idx,direction,entry in signals:
        exit_idx=min(idx+hold,len(bars)-1)
        net=(bars[exit_idx].c-entry)*direction - COST_RT
        trades.append(net/entry*100)
    if not trades: return {'n':0,'win_pct':0,'avg':0}
    return {'n':len(trades),'win_pct':sum(1 for t in trades if t>0)/len(trades)*100,'avg':sum(trades)/len(trades)}

def dynamic_PAV(bars, base_rsi=40, base_hold=5):
    """ATR-regime adaptive: RSI tightens in high-ATR, hold extends with Hurst persistence"""
    closes=[b.c for b in bars]
    at=atr_series(bars,14)
    at50=sma(at,50)
    rs=rsi_series(closes,14)
    signals=[]
    for i in range(52,len(bars)-1):
        if rs[i] is None or at[i] is None or at50[i] is None or at50[i]==0: continue
        atr_regime=at[i]/at50[i]
        # tighten RSI threshold in high-ATR (volatile), loosen in low-ATR (quiet)
        if atr_regime>1.3:   rsi_t=base_rsi-8   # tight: 32
        elif atr_regime<0.7: rsi_t=base_rsi+8   # loose: 48
        else:                rsi_t=base_rsi       # 40
        # Hurst-adaptive hold
        window=closes[max(0,i-30):i]
        h=hurst(window)
        if h and h>0.55:   hold=base_hold+2    # persistent: longer
        elif h and h<0.45: hold=max(2,base_hold-1)  # anti-persistent: shorter
        else:              hold=base_hold
        # swing low check
        if (bars[i-1].l<bars[i-2].l and bars[i-1].l<bars[i].l and rs[i]<rsi_t):
            swing_h=bars[i].h-bars[i-1].l
            atr_ratio=swing_h/at[i] if at[i] else 0
            if 1.0<=atr_ratio<=4.0:
                signals.append((i,1,bars[i].c,hold))
    # run with variable hold
    trades=[]
    for idx,direction,entry,hold in signals:
        exit_idx=min(idx+hold,len(bars)-1)
        net=(bars[exit_idx].c-entry)*direction - COST_RT
        trades.append(net/entry*100)
    if not trades: return {'n':0,'win_pct':0,'avg':0,'label':'PAV_DYNAMIC'}
    return {'n':len(trades),'win_pct':sum(1 for t in trades if t>0)/len(trades)*100,
            'avg':sum(trades)/len(trades),'label':'PAV_DYNAMIC'}

def dynamic_GAP(bars, base_thresh=0.003, base_hold=3):
    """High-ATR: tighten gap threshold, low-ATR: loosen"""
    at=atr_series(bars,14)
    at50=sma(at,50)
    signals=[]
    for i in range(52,len(bars)):
        if at[i] is None or at50[i] is None or at50[i]==0: continue
        atr_regime=at[i]/at50[i]
        thresh = base_thresh*1.5 if atr_regime>1.3 else (base_thresh*0.7 if atr_regime<0.7 else base_thresh)
        hold   = base_hold+1 if atr_regime>1.3 else base_hold
        gap=(bars[i].o-bars[i-1].c)/bars[i-1].c
        if gap>=thresh and bars[i].c<bars[i].o:
            signals.append((i,-1,bars[i].c,hold))
    trades=[]
    for idx,direction,entry,hold in signals:
        exit_idx=min(idx+hold,len(bars)-1)
        net=(bars[exit_idx].c-entry)*direction - COST_RT
        trades.append(net/entry*100)
    if not trades: return {'n':0,'win_pct':0,'avg':0,'label':'GAP_DYNAMIC'}
    return {'n':len(trades),'win_pct':sum(1 for t in trades if t>0)/len(trades)*100,
            'avg':sum(trades)/len(trades),'label':'GAP_DYNAMIC'}

# ==================== PHASE 4: NEWS INFLUENCE ====================
def news_bars(bars, n=20, mult=3.0):
    ranges=[b.h-b.l for b in bars]
    avg_range=sma(ranges,n)
    news_set=set()
    for i in range(n,len(bars)):
        if avg_range[i] and ranges[i]>mult*avg_range[i]:
            news_set.add(i)
    return news_set

def news_filter_backtest(bars, signals, hold, label, mode):
    """mode: 'avoid1'=skip entry within 1 bar of news, 'after2'=enter 2 bars after news, 'bias'=news dir bias"""
    nb=news_bars(bars)
    filtered=[]
    for idx,direction,entry in signals:
        near_news=any(abs(idx-n)<=1 for n in nb)
        if mode=='avoid1':
            if not near_news: filtered.append((idx,direction,entry))
        elif mode=='after2':
            # enter only if there was a news bar 2-3 bars ago and direction matches
            news_near=[n for n in nb if 2<=idx-n<=3]
            if news_near:
                n_idx=news_near[-1]
                news_dir=1 if bars[n_idx].c>bars[n_idx].o else -1
                filtered.append((idx,news_dir,entry))
        elif mode=='bias':
            # add news direction bias for next 5 bars after news
            recent_news=[n for n in nb if 0<idx-n<=5]
            if recent_news:
                n_idx=recent_news[-1]
                bias=1 if bars[n_idx].c>bars[n_idx].o else -1
                # only take signal if it aligns with news bias
                if direction==bias: filtered.append((idx,direction,entry))
            else:
                filtered.append((idx,direction,entry))

    r=run_backtest_pnl(filtered,bars,hold)
    r['label']=label+f'_news_{mode}'
    return r

# ==================== PHASE 5: MARKET TIMING ====================
def dow_breakdown(bars, signals, hold, label):
    """Day-of-week win rates"""
    dow_trades={0:[],1:[],2:[],3:[],4:[]}
    dow_names={0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri'}
    for idx,direction,entry in signals:
        exit_idx=min(idx+hold,len(bars)-1)
        net=(bars[exit_idx].c-entry)*direction - COST_RT
        net_pct=net/entry*100
        d=bars[idx].dow
        if d in dow_trades: dow_trades[d].append(net_pct)
    rows=[]
    for d in range(5):
        ts=dow_trades[d]
        if ts:
            rows.append(f"{dow_names[d]}: n={len(ts)} win={sum(1 for t in ts if t>0)/len(ts)*100:.1f}% avg={sum(ts)/len(ts):.4f}%")
    return rows

# ==================== PHASE 6: INSTITUTIONAL FLOWS ====================
def round_number_proximity(price, pip_size=0.0001):
    """Returns min distance to round level (x.x000 or x.x500) in pips"""
    p=round(price/pip_size)
    nearest_00=round(p/1000)*1000
    nearest_50=round((p-500)/1000)*1000+500
    return min(abs(p-nearest_00), abs(p-nearest_50))

def prior_day_levels(bars):
    """Return dict of bar_idx -> (pd_high, pd_low, pd_close)"""
    levels={}
    for i in range(1,len(bars)):
        levels[i]=(bars[i-1].h, bars[i-1].l, bars[i-1].c)
    return levels

def institutional_analysis(bars, signals, hold, label):
    pd_lev=prior_day_levels(bars)
    ranges=[b.h-b.l for b in bars]
    avg_r=sma(ranges,20)

    near_round_wins=0; near_round_losses=0
    near_pd_wins=0;    near_pd_losses=0
    compress_wins=0;   compress_losses=0
    expand_wins=0;     expand_losses=0

    for idx,direction,entry in signals:
        if idx<21 or idx not in pd_lev: continue
        exit_idx=min(idx+hold,len(bars)-1)
        net=(bars[exit_idx].c-entry)*direction - COST_RT
        is_win=net>0

        # Round number: within 10 pips
        dist_round=round_number_proximity(entry)
        near_round = dist_round<=10

        # Prior day level: within 10 pips of pdH, pdL, or pdC
        pdh,pdl,pdc=pd_lev[idx]
        dist_pd=min(abs(entry-pdh),abs(entry-pdl),abs(entry-pdc))/0.0001
        near_pd = dist_pd<=10

        # Range compression/expansion vs 20-bar avg
        if avg_r[idx] and avg_r[idx]>0:
            range_ratio=ranges[idx]/avg_r[idx]
            compress = range_ratio<0.7
            expand   = range_ratio>1.5
        else:
            compress=expand=False

        if is_win:
            if near_round: near_round_wins+=1
            if near_pd: near_pd_wins+=1
            if compress: compress_wins+=1
            if expand: expand_wins+=1
        else:
            if near_round: near_round_losses+=1
            if near_pd: near_pd_losses+=1
            if compress: compress_losses+=1
            if expand: expand_losses+=1

    def pct(a,b): return f"{a/(a+b)*100:.1f}%" if a+b>0 else "n/a"
    return {
        'label': label,
        'round_num_win_rate': pct(near_round_wins, near_round_losses),
        'round_num_n': near_round_wins+near_round_losses,
        'pd_level_win_rate': pct(near_pd_wins, near_pd_losses),
        'pd_level_n': near_pd_wins+near_pd_losses,
        'compress_win_rate': pct(compress_wins, compress_losses),
        'compress_n': compress_wins+compress_losses,
        'expand_win_rate': pct(expand_wins, expand_losses),
        'expand_n': expand_wins+expand_losses,
    }

# ==================== PHASE 7: MM STOP HUNT ====================
def mm_bars(bars, pip_lookback=20, wick_ratio=0.6):
    """Detect stop-hunt bars: spike beyond recent swing then reverses, wick_ratio > threshold"""
    mm_set=set()
    for i in range(pip_lookback+1,len(bars)):
        total_range=bars[i].h-bars[i].l
        if total_range<=0: continue
        body=abs(bars[i].c-bars[i].o)
        wick=total_range-body
        if wick/total_range<wick_ratio: continue
        # upper wick spike above recent high
        recent_h=max(bars[j].h for j in range(i-pip_lookback,i))
        recent_l=min(bars[j].l for j in range(i-pip_lookback,i))
        if bars[i].h>recent_h and bars[i].c<recent_h:
            mm_set.add(i)
        elif bars[i].l<recent_l and bars[i].c>recent_l:
            mm_set.add(i)
    return mm_set

def mm_analysis(bars, signals, hold, label):
    """Check if winners follow MM bars (within 1-3 bars after)"""
    mm=mm_bars(bars)
    after_mm_wins=0; after_mm_losses=0
    other_wins=0; other_losses=0

    for idx,direction,entry in signals:
        exit_idx=min(idx+hold,len(bars)-1)
        net=(bars[exit_idx].c-entry)*direction - COST_RT
        is_win=net>0
        follows_mm=any(0<idx-m<=3 for m in mm)
        if follows_mm:
            if is_win: after_mm_wins+=1
            else: after_mm_losses+=1
        else:
            if is_win: other_wins+=1
            else: other_losses+=1

    def pct(a,b): return f"{a/(a+b)*100:.1f}%" if a+b>0 else "n/a"
    return {
        'label': label,
        'after_mm_win': pct(after_mm_wins,after_mm_losses),
        'after_mm_n': after_mm_wins+after_mm_losses,
        'other_win': pct(other_wins,other_losses),
        'other_n': other_wins+other_losses,
    }

# ==================== PHASE 8: CB/GOV REVERSION ====================
def cb_reversion_analysis(bars, signals, hold, label):
    """Winners that enter 1-5 bars AFTER a major outlier bar (CB/news)"""
    nb=news_bars(bars, mult=3.0)
    post_cb_wins=0; post_cb_losses=0
    other_wins=0; other_losses=0

    for idx,direction,entry in signals:
        exit_idx=min(idx+hold,len(bars)-1)
        net=(bars[exit_idx].c-entry)*direction - COST_RT
        is_win=net>0
        post_cb=any(1<=idx-n<=5 for n in nb)
        if post_cb:
            if is_win: post_cb_wins+=1
            else: post_cb_losses+=1
        else:
            if is_win: other_wins+=1
            else: other_losses+=1

    def pct(a,b): return f"{a/(a+b)*100:.1f}%" if a+b>0 else "n/a"
    return {
        'label': label,
        'post_cb_win': pct(post_cb_wins,post_cb_losses),
        'post_cb_n': post_cb_wins+post_cb_losses,
        'other_win': pct(other_wins,other_losses),
        'other_n': other_wins+other_losses
    }

# ==================== SURVIVOR SIGNAL REGEN ====================
def gen_survivor_signals(bars):
    closes=[b.c for b in bars]
    at=atr_series(bars,14)
    rs=rsi_series(closes,14)
    ma20=sma(closes,20); sd20=stdev(closes,20)
    em21=ema(closes,21)

    survivors={}

    # PAV_r40a10-40h5
    sig=[]
    for i in range(16,len(bars)-1):
        if rs[i] is None or at[i] is None or at[i]==0: continue
        if bars[i-1].l<bars[i-2].l and bars[i-1].l<bars[i].l and rs[i]<40:
            atr_ratio=(bars[i].h-bars[i-1].l)/at[i]
            if 1.0<=atr_ratio<=4.0: sig.append((i,1,bars[i].c))
    survivors['PAV_r40_h5']=(sig,5)

    # PAV_r35a5-30h4
    sig2=[]
    for i in range(16,len(bars)-1):
        if rs[i] is None or at[i] is None or at[i]==0: continue
        if bars[i-1].l<bars[i-2].l and bars[i-1].l<bars[i].l and rs[i]<35:
            atr_ratio=(bars[i].h-bars[i-1].l)/at[i]
            if 0.5<=atr_ratio<=3.0: sig2.append((i,1,bars[i].c))
    survivors['PAV_r35_h4']=(sig2,4)

    # PAV_r45a15-50h6
    sig3=[]
    for i in range(16,len(bars)-1):
        if rs[i] is None or at[i] is None or at[i]==0: continue
        if bars[i-1].l<bars[i-2].l and bars[i-1].l<bars[i].l and rs[i]<45:
            atr_ratio=(bars[i].h-bars[i-1].l)/at[i]
            if 1.5<=atr_ratio<=5.0: sig3.append((i,1,bars[i].c))
    survivors['PAV_r45_h6']=(sig3,6)

    # CRB_n20k20h5
    sig4=[]
    for i in range(22,len(bars)):
        if ma20[i] is None or sd20[i] is None: continue
        lb=ma20[i]-2.0*sd20[i]; lb1=ma20[i-1]-2.0*(sd20[i-1] or 0); lb2=ma20[i-2]-2.0*(sd20[i-2] or 0)
        if bars[i-2].c<lb2 and bars[i-1].c<lb1 and bars[i].c>lb and bars[i].c>bars[i].o:
            sig4.append((i,1,bars[i].c))
    survivors['CRB_n20k20_h5']=(sig4,5)

    # CRB_n20k15h3
    sig5=[]
    for i in range(22,len(bars)):
        if ma20[i] is None or sd20[i] is None: continue
        lb=ma20[i]-1.5*sd20[i]; lb1=ma20[i-1]-1.5*(sd20[i-1] or 0); lb2=ma20[i-2]-1.5*(sd20[i-2] or 0)
        if bars[i-2].c<lb2 and bars[i-1].c<lb1 and bars[i].c>lb and bars[i].c>bars[i].o:
            sig5.append((i,1,bars[i].c))
    survivors['CRB_n20k15_h3']=(sig5,3)

    # CRB_INV n14k20h4
    ma14=sma(closes,14); sd14=stdev(closes,14)
    sig6=[]
    for i in range(16,len(bars)):
        if ma14[i] is None or sd14[i] is None: continue
        lb=ma14[i]-2.0*sd14[i]; lb1=ma14[i-1]-2.0*(sd14[i-1] or 0); lb2=ma14[i-2]-2.0*(sd14[i-2] or 0)
        if bars[i-2].c<lb2 and bars[i-1].c<lb1 and bars[i].c>lb and bars[i].c>bars[i].o:
            sig6.append((i,-1,bars[i].c))
    survivors['CRB_INV_n14_h4']=(sig6,4)

    # GAP_t3h3
    sig7=[(i,-1,bars[i].c) for i in range(1,len(bars))
          if (bars[i].o-bars[i-1].c)/bars[i-1].c>=0.003 and bars[i].c<bars[i].o]
    survivors['GAP_t3_h3']=(sig7,3)

    # GAP_MICRO_t1h3
    sig8=[(i,-1,bars[i].c) for i in range(1,len(bars))
          if (bars[i].o-bars[i-1].c)/bars[i-1].c>=0.001 and bars[i].c<bars[i].o]
    survivors['GAP_MICRO_h3']=(sig8,3)

    # GAP_t5h5
    sig9=[(i,-1,bars[i].c) for i in range(1,len(bars))
          if (bars[i].o-bars[i-1].c)/bars[i-1].c>=0.005 and bars[i].c<bars[i].o]
    survivors['GAP_t5_h5']=(sig9,5)

    return survivors

# ==================== MAIN ====================
def main():
    bars=load_eurusd('/home/user/Signal/data/history/EURUSD.csv')
    print(f"Loaded {len(bars)} bars")

    out=['# Extended Winner Analysis — EURUSD D1\n']

    # ---- DATA INTEGRITY ----
    issues, spike_dates=check_integrity(bars)
    out.append('## Data Integrity\n')
    if issues:
        out.append(f"Found {len(issues)} issues:\n")
        for iss in issues[:20]: out.append(f"  {iss}\n")
        if len(issues)>20: out.append(f"  ... and {len(issues)-20} more\n")
    else:
        out.append("  No integrity issues found.\n")
    out.append(f"  Spike/outlier bar dates: {sorted(spike_dates)[:10]}\n\n")

    survivors=gen_survivor_signals(bars)

    # ---- CHAOS PROFILES ----
    out.append('## Chaos Profile: Winners vs Losers\n')
    out.append('| Strategy | nW | nL | Win chaos | Loss chaos | Win Hurst | Loss Hurst | Win ATR-reg | Loss ATR-reg | Win Range | Loss Range |\n')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|\n')
    for name,(sig,hold) in survivors.items():
        cp=chaos_profile(bars,sig,hold,name)
        out.append(f"| {cp['label']} | {cp['nw']} | {cp['nl']} | {cp['win_chaos_avg']} | {cp['loss_chaos_avg']} | {cp['win_hurst']} | {cp['loss_hurst']} | {cp['win_atr_reg']} | {cp['loss_atr_reg']} | {cp['win_range_avg']} | {cp['loss_range_avg']} |\n")
    out.append('\n')

    # ---- DYNAMIC PARAMS ----
    out.append('## Dynamic Parameter Variants\n')
    fixed_pav=run_backtest_pnl(survivors['PAV_r40_h5'][0], bars, 5)
    dyn_pav=dynamic_PAV(bars)
    fixed_gap=run_backtest_pnl(survivors['GAP_t3_h3'][0], bars, 3)
    dyn_gap=dynamic_GAP(bars)
    out.append(f"PAV fixed:   n={fixed_pav['n']} win={fixed_pav['win_pct']:.1f}% avg={fixed_pav['avg']:.4f}%\n")
    out.append(f"PAV dynamic: n={dyn_pav['n']} win={dyn_pav['win_pct']:.1f}% avg={dyn_pav['avg']:.4f}%\n")
    out.append(f"GAP fixed:   n={fixed_gap['n']} win={fixed_gap['win_pct']:.1f}% avg={fixed_gap['avg']:.4f}%\n")
    out.append(f"GAP dynamic: n={dyn_gap['n']} win={dyn_gap['win_pct']:.1f}% avg={dyn_gap['avg']:.4f}%\n\n")

    # ---- NEWS INFLUENCE ----
    out.append('## News Influence (range > 3× 20-bar avg = news bar)\n')
    nb=news_bars(bars)
    out.append(f"  News bars detected: {len(nb)}\n")
    for name,(sig,hold) in [('PAV_r40_h5',survivors['PAV_r40_h5']),
                              ('CRB_n20k20_h5',survivors['CRB_n20k20_h5']),
                              ('GAP_t3_h3',survivors['GAP_t3_h3'])]:
        base=run_backtest_pnl(sig,bars,hold)
        out.append(f"\n  {name} BASE: n={base['n']} win={base['win_pct']:.1f}% avg={base['avg']:.4f}%\n")
        for mode in ['avoid1','after2','bias']:
            r=news_filter_backtest(bars,sig,hold,name,mode)
            out.append(f"    [{mode}] n={r['n']} win={r['win_pct']:.1f}% avg={r['avg']:.4f}%\n")
    out.append('\n')

    # ---- MARKET TIMING ----
    out.append('## Market Timing (Day of Week)\n')
    for name,(sig,hold) in list(survivors.items())[:4]:
        rows=dow_breakdown(bars,sig,hold,name)
        out.append(f"\n  {name}:\n")
        for row in rows: out.append(f"    {row}\n")
    out.append('\n')

    # ---- INSTITUTIONAL FLOWS ----
    out.append('## Institutional Flows & Liquidity\n')
    out.append('| Strategy | Round# WR | n | PD-level WR | n | Compress WR | n | Expand WR | n |\n')
    out.append('|---|---|---|---|---|---|---|---|---|\n')
    for name,(sig,hold) in survivors.items():
        ia=institutional_analysis(bars,sig,hold,name)
        out.append(f"| {ia['label']} | {ia['round_num_win_rate']} | {ia['round_num_n']} | {ia['pd_level_win_rate']} | {ia['pd_level_n']} | {ia['compress_win_rate']} | {ia['compress_n']} | {ia['expand_win_rate']} | {ia['expand_n']} |\n")
    out.append('\n')

    # ---- MM STOP HUNT ----
    out.append('## Market Maker Stop-Hunt Analysis\n')
    mm=mm_bars(bars)
    out.append(f"  MM stop-hunt bars detected: {len(mm)}\n")
    out.append('| Strategy | After-MM WR | n | Other WR | n |\n')
    out.append('|---|---|---|---|---|\n')
    for name,(sig,hold) in list(survivors.items())[:5]:
        r=mm_analysis(bars,sig,hold,name)
        out.append(f"| {r['label']} | {r['after_mm_win']} | {r['after_mm_n']} | {r['other_win']} | {r['other_n']} |\n")
    out.append('\n')

    # ---- CB REVERSION ----
    out.append('## CB/Gov Action Reversion (1-5 bars after >3× ATR outlier)\n')
    out.append('| Strategy | Post-CB WR | n | Other WR | n |\n')
    out.append('|---|---|---|---|---|\n')
    for name,(sig,hold) in list(survivors.items())[:5]:
        r=cb_reversion_analysis(bars,sig,hold,name)
        out.append(f"| {r['label']} | {r['post_cb_win']} | {r['post_cb_n']} | {r['other_win']} | {r['other_n']} |\n")
    out.append('\n')

    out.append('---\n_Past results are not advice. Chaos = realized vol proxy. Hurst>0.5=persistent, <0.5=mean-reverting._\n')

    result=''.join(out)
    print(result)

    with open('/mnt/project-files/extended_analysis.md','w') as f:
        f.write(result)

if __name__=='__main__':
    main()
