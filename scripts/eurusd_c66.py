"""
EURUSD C66: RSI(14) threshold scan + C61c (fresh EMA30 cross) combo + monthly exclusion
Baseline v2.3: EMA120<0, ADX<30, ATR14_pct<75%, ATR14>=0.0005, Wed/Thu, asia_net>=0.25*ATR14
Stop=Entry+0.80*ATR14, Exit=21:00 UTC, Cost=0.00008/trade
"""
import pandas as pd
import numpy as np

DATA = "/mnt/project-files/data/eurusd_fxopen_h1.csv"
COST = 0.00008

df = pd.read_csv(DATA)
df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True).dt.tz_convert('UTC').dt.tz_localize(None)
df['date'] = df['datetime'].dt.date
df['hour'] = df['datetime'].dt.hour
df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['dow'] = df['datetime'].dt.dayofweek  # 0=Mon

df = df.sort_values('datetime').reset_index(drop=True)

# ── Indicators ──────────────────────────────────────────────────────────────

# EMA(120) slope
df['ema120'] = df['close'].ewm(span=120, adjust=False).mean()
df['ema120_slope'] = df['ema120'].diff()

# ADX(14)
high = df['high']; low = df['low']; close = df['close']
prev_close = close.shift(1)
tr = pd.concat([high-low, (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
df['atr14'] = tr.ewm(span=14, adjust=False).mean()
up_move = high.diff(); down_move = -low.diff()
plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
plus_di = 100 * pd.Series(plus_dm).ewm(span=14, adjust=False).mean() / df['atr14'].clip(lower=1e-9)
minus_di = 100 * pd.Series(minus_dm).ewm(span=14, adjust=False).mean() / df['atr14'].clip(lower=1e-9)
dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).clip(lower=1e-9)
df['adx14'] = dx.ewm(span=14, adjust=False).mean()

# ATR% of close
df['atr14_pct'] = df['atr14'] / df['close'].clip(lower=1e-9)
atr_75pct = df['atr14_pct'].quantile(0.75)

# RSI(5) H1
delta5 = df['close'].diff()
df['rsi5'] = 100 - (100 / (1 + delta5.clip(lower=0).ewm(span=5, adjust=False).mean() /
                              (-delta5.clip(upper=0)).ewm(span=5, adjust=False).mean().clip(lower=1e-9)))

# RSI(14) H1
delta14 = df['close'].diff()
df['rsi14'] = 100 - (100 / (1 + delta14.clip(lower=0).ewm(span=14, adjust=False).mean() /
                               (-delta14.clip(upper=0)).ewm(span=14, adjust=False).mean().clip(lower=1e-9)))

# EMA(30) for EMA30 neg filter and fresh-cross detection
df['ema30'] = df['close'].ewm(span=30, adjust=False).mean()
df['ema30_neg'] = (df['ema30'].diff() < 0).astype(int)
# Fresh cross: close crossed below EMA30 within last N bars
# Signal = 1 on the bar where close < ema30 AND prev close >= ema30
df['ema30_cross_dn'] = ((df['close'] < df['ema30']) & (df['close'].shift(1) >= df['ema30'].shift(1))).astype(int)
# Bars since last downward cross (max out at 999 if no cross found)
bars_since = []
cnt = 999
for v in df['ema30_cross_dn']:
    if v == 1:
        cnt = 0
    bars_since.append(cnt)
    cnt = min(cnt + 1, 999)
df['bars_since_ema30_cross'] = bars_since

# D1 slope from prior day close
daily_oc = df.groupby('date').agg(open_d1=('open','first'), close_d1=('close','last'),
                                   high_d=('high','max')).reset_index()
daily_oc['d1_slope'] = daily_oc['close_d1'] - daily_oc['open_d1']
daily_oc['prev_close'] = daily_oc['close_d1'].shift(1)
daily_oc['prior_day_slope'] = daily_oc['d1_slope'].shift(1)

# ── Build entry table (07:00 bars, Wed/Thu) ─────────────────────────────────
bar06 = df[df['hour'] == 6][['date','close']].rename(columns={'close':'close06'})
bar07 = df[df['hour'] == 7].copy()
bar07['date_key'] = pd.to_datetime(bar07['date']).dt.date

# Lookup helpers
bar22 = df[df['hour'] == 22][['date','close']].copy()
bar22['date'] = pd.to_datetime(bar22['date']).dt.date
bar22_dict = dict(zip(bar22['date'], bar22['close']))

bar21 = df[df['hour'] == 21][['date','open']].copy()
bar21['date'] = pd.to_datetime(bar21['date']).dt.date
bar21_dict = dict(zip(bar21['date'], bar21['open']))

intra = df[(df['hour'] >= 8) & (df['hour'] <= 20)][['date','hour','high','open']].copy()
intra['date'] = pd.to_datetime(intra['date']).dt.date
intra_dict = {}
for row in intra.itertuples(index=False):
    intra_dict.setdefault(row.date, []).append((row.hour, row.high, row.open))

bar07 = bar07.merge(bar06, on='date', how='left')
bar07 = bar07.merge(daily_oc[['date','d1_slope','prev_close','prior_day_slope']].rename(
    columns={'date':'date_obj'}), left_on='date', right_on='date_obj', how='left')

entry = bar07.rename(columns={'open':'open07','atr14_pct':'atr14_pct','atr14':'atr14',
                               'adx14':'adx14','ema120_slope':'ema120_slope'}).copy()
entry['date_key'] = pd.to_datetime(entry['date']).dt.date
entry['year'] = entry['datetime'].dt.year
entry['month'] = entry['datetime'].dt.month
entry['dow'] = entry['datetime'].dt.dayofweek

# Asia net move (prev close22 -> open07)
import bisect as _bisect
_all_bar22_dates = sorted(bar22_dict.keys())
def _prev_close22(d):
    i = _bisect.bisect_left(_all_bar22_dates, d)
    return bar22_dict[_all_bar22_dates[i-1]] if i > 0 else np.nan
entry['close22_prev'] = entry['date_key'].apply(_prev_close22)
entry['asia_net'] = entry['open07'] - entry['close22_prev']

# Gap filter: no gap up from 06:00 close to 07:00 open (C64 definition)
entry['overnight_gap'] = entry['open07'] - entry['close06']
entry['no_gap'] = (entry['overnight_gap'] <= 0).astype(int)

# RSI5 and RSI14 at bar07
entry['rsi5_07'] = entry['rsi5']
entry['rsi14_07'] = entry['rsi14']

# EMA30 slope and fresh cross at bar07
entry['ema30_neg_07'] = entry['ema30_neg']
entry['bars_since_cross_07'] = entry['bars_since_ema30_cross']

# ── Simulation ───────────────────────────────────────────────────────────────
def sim(ep, atr, date):
    stop_px = ep + 0.80 * atr
    for hour, high, open_px in sorted(intra_dict.get(date, [])):
        if high >= stop_px:
            return stop_px, True
    return bar21_dict.get(date, ep), False

def run_on_mask(mask, label=""):
    rows = entry[mask]
    if len(rows) == 0:
        return {'label': label, 'n': 0, 'pf': 0, 'avg': 0, 'win': 0, 'by_year': {}}
    results = []
    for _, row in rows.iterrows():
        ep = row['open07']; atr = row['atr14']; date = row['date_key']
        exit_px, stopped = sim(ep, atr, date)
        pnl = (ep - exit_px) / ep - COST
        results.append({'year': row['year'], 'month': row['month'], 'pnl': pnl})
    r = pd.DataFrame(results)
    w = r[r['pnl'] > 0]['pnl'].sum()
    l = abs(r[r['pnl'] < 0]['pnl'].sum())
    pf = w / l if l > 0 else float('inf')
    by_yr = {}
    for yr, g in r.groupby('year'):
        gw = g[g['pnl'] > 0]['pnl'].sum()
        gl = abs(g[g['pnl'] < 0]['pnl'].sum())
        by_yr[yr] = round(gw / max(gl, 1e-10), 2)
    return {'label': label, 'n': len(r), 'pf': round(pf, 2),
            'avg': round(r['pnl'].mean() * 100, 3),
            'win': round((r['pnl'] > 0).mean() * 100, 1), 'by_year': by_yr}

def fmt(res):
    yr = res['by_year']
    yr_str = ' | '.join([f"{y}:{v}" for y, v in sorted(yr.items())])
    return (f"  {res['label']:<55} n={res['n']:>3}  PF={res['pf']:>6.2f}  "
            f"avg={res['avg']:>+6.3f}%  win={res['win']:>4.1f}%  [{yr_str}]")

# ── Baseline ─────────────────────────────────────────────────────────────────
base = ((entry['ema120_slope'] < 0) & (entry['adx14'] < 30) &
        (entry['atr14_pct'] < 0.75) & (entry['atr14'] >= 0.0005) &
        (entry['dow'].isin([2, 3])) & (entry['asia_net'] >= 0.25 * entry['atr14']))

b0 = run_on_mask(base, "Baseline v2.3")
print("=== C66: RSI14 threshold scan + C61c combo + monthly exclusion ===\n")
print("BASELINE")
print(fmt(b0))
print()

# ── A: RSI14 threshold scan ─────────────────────────────────────────────────
print("A: RSI14 threshold scan")
for thresh in [45, 48, 50, 52, 55, 58, 60, 65]:
    m = base & (entry['rsi14_07'] < thresh)
    r = run_on_mask(m, f"RSI14 < {thresh}")
    print(fmt(r))
print()

# Compare RSI14<55 vs RSI5<60 head-to-head
m_r14 = base & (entry['rsi14_07'] < 55)
m_r5  = base & (entry['rsi5_07'] < 60)
m_both = base & (entry['rsi14_07'] < 55) & (entry['rsi5_07'] < 60)
m_r14_only = base & (entry['rsi14_07'] < 55) & (entry['rsi5_07'] >= 60)
m_r5_only  = base & (entry['rsi14_07'] >= 55) & (entry['rsi5_07'] < 60)
print("RSI14<55 vs RSI5<60 overlap analysis")
print(fmt(run_on_mask(m_r14, "RSI14<55")))
print(fmt(run_on_mask(m_r5,  "RSI5<60")))
print(fmt(run_on_mask(m_both,"RSI14<55 AND RSI5<60")))
print(fmt(run_on_mask(m_r14_only, "RSI14<55 only (RSI5>=60)")))
print(fmt(run_on_mask(m_r5_only,  "RSI5<60 only (RSI14>=55)")))
print()

# ── B: C61c (fresh EMA30 cross <=15 bars) + RSI5<60 ─────────────────────────
print("B: Fresh EMA30 cross + RSI5<60 combinations")
for n_bars in [5, 10, 15, 20]:
    m = base & (entry['bars_since_cross_07'] <= n_bars)
    r = run_on_mask(m, f"Fresh EMA30 cross (<=  {n_bars} bars)")
    print(fmt(r))

m_fresh15 = base & (entry['bars_since_cross_07'] <= 15)
m_fresh15_r5 = m_fresh15 & (entry['rsi5_07'] < 60)
print(fmt(run_on_mask(m_fresh15_r5, "Fresh EMA30 (<=15) + RSI5<60")))

m_ema30neg = base & (entry['ema30_neg_07'] == 1)
m_ema30neg_r5 = m_ema30neg & (entry['rsi5_07'] < 60)
m_ema30neg_r5_nogap = m_ema30neg_r5 & (entry['no_gap'] == 1)
print(fmt(run_on_mask(m_ema30neg, "EMA30 slope neg")))
print(fmt(run_on_mask(m_ema30neg_r5, "EMA30 slope neg + RSI5<60")))
print(fmt(run_on_mask(m_ema30neg_r5_nogap, "EMA30 slope neg + RSI5<60 + no gap  [C64b repro]")))
print()

# ── C: Monthly exclusion scan ────────────────────────────────────────────────
print("C: Per-month breakdown (base + RSI5<60)")
m_rsi5 = base & (entry['rsi5_07'] < 60)
r_all = run_on_mask(m_rsi5, "RSI5<60 all months")
print(fmt(r_all))
print()
month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
               7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
monthly = []
for mo in range(1, 13):
    m_mo = m_rsi5 & (entry['month'] == mo)
    r_mo = run_on_mask(m_mo, f"  Month {month_names[mo]} ({mo:02d})")
    monthly.append((mo, r_mo))
    print(fmt(r_mo))
print()

# Which months are drag? Exclude each one individually
print("C2: Exclude each month from RSI5<60 set")
for mo, r_mo in monthly:
    if r_mo['n'] < 2:
        continue
    m_excl = m_rsi5 & (entry['month'] != mo)
    r_excl = run_on_mask(m_excl, f"Excl {month_names[mo]}")
    print(fmt(r_excl))
print()

# Q2 exclusion (Apr/May/Jun) with RSI5<60
m_noq2 = m_rsi5 & (~entry['month'].isin([4, 5, 6]))
print(fmt(run_on_mask(m_noq2, "RSI5<60 excl Q2 (Apr-Jun)")))

# Best 3-filter combo with seasonal tweak
m_best3 = m_ema30neg_r5_nogap
m_best3_noq2 = m_best3 & (~entry['month'].isin([4, 5, 6]))
print(fmt(run_on_mask(m_best3, "C64b: EMA30neg+RSI5<60+no gap")))
print(fmt(run_on_mask(m_best3_noq2, "C64b excl Q2")))
print()

# ── D: Optimal threshold combo scan ─────────────────────────────────────────
print("D: RSI14 threshold with best base combos")
for thresh in [50, 52, 55]:
    m14 = base & (entry['rsi14_07'] < thresh) & (entry['no_gap'] == 1)
    print(fmt(run_on_mask(m14, f"RSI14<{thresh} + no gap")))
    m14_ema = m14 & (entry['ema30_neg_07'] == 1)
    print(fmt(run_on_mask(m14_ema, f"RSI14<{thresh} + no gap + EMA30neg")))
print()

print("=== END C66 ===")
