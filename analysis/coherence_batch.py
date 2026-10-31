#!/usr/bin/env python3
"""
Multi-TF Coherence + MA Proximity + MMR Mean Reversion Batch Test
Base signal: T92 M30 (HURR + FPCS>1.0 + mid-month + quarter-end skip)
"""
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

DATA = '/mnt/project-files'
COST_PIPS = 1.1  # round-trip FXOpen ECN
PIP = 0.0001
HOLD_BARS_M30 = 3
TP_PIPS = 20
SL_PIPS = 15

PERIODS = {
    '2010-14': ('2010-01-01', '2014-12-31'),
    '2015-19': ('2015-01-01', '2019-12-31'),
    '2020-22': ('2020-01-01', '2022-12-31'),
    '2023-24': ('2023-01-01', '2024-12-31'),
}

def load_csv(path, nrows=None):
    df = pd.read_csv(path, nrows=nrows)
    df.columns = [c.strip().lower() for c in df.columns]
    # detect date col
    for c in ['date','time','datetime','timestamp']:
        if c in df.columns:
            df['dt'] = pd.to_datetime(df[c], infer_datetime_format=True)
            break
    if 'dt' not in df.columns:
        df['dt'] = pd.to_datetime(df.iloc[:,0], infer_datetime_format=True)
    df = df.sort_values('dt').reset_index(drop=True)
    for col in ['open','high','low','close']:
        if col not in df.columns:
            # try first numeric cols
            nums = df.select_dtypes(include=np.number).columns
            if len(nums) >= 4:
                df[['open','high','low','close']] = df[nums[:4]].values
            break
    return df

def load_multipart(prefix, max_parts=4):
    parts = sorted(glob.glob(f'{DATA}/{prefix}_part*.csv'))[:max_parts]
    if not parts:
        f = f'{DATA}/{prefix}.csv'
        if os.path.exists(f):
            return load_csv(f)
        return None
    frames = [load_csv(p) for p in parts]
    df = pd.concat(frames).sort_values('dt').drop_duplicates('dt').reset_index(drop=True)
    return df

def sma(s, n): return s.rolling(n).mean()
def atr(df, n=14):
    tr = pd.concat([df['high']-df['low'],
                    (df['high']-df['close'].shift()).abs(),
                    (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def slope_pips(df, n=5):
    s = sma(df['close'], n)
    return (s - s.shift(n)) / PIP

def fpcs(df):
    # FPCS = fractal dist * psych dist proxy
    # fractal: distance from local 5-bar low
    frac_low = df['low'].rolling(5).min()
    frac_dist = (df['close'] - frac_low) / PIP
    # psych: distance to nearest round 100-pip level
    price = df['close']
    nearest = (price / 0.01).round() * 0.01
    psych_dist = (price - nearest).abs() / PIP + 0.001
    return (frac_dist / 10) * (psych_dist / 10)

def weather_state(slope):
    a = slope.abs()
    state = pd.Series('CALM', index=slope.index)
    state[a.between(1, 5)] = 'BREEZE'
    state[a.between(5, 15)] = 'WIND'
    state[a.between(15, 25)] = 'STORM'
    state[a > 25] = 'HURR'
    return state

def adx(df, n=14):
    up = df['high'].diff()
    dn = -df['low'].diff()
    pdm = np.where((up > dn) & (up > 0), up, 0)
    ndm = np.where((dn > up) & (dn > 0), dn, 0)
    tr_ = pd.concat([df['high']-df['low'],
                     (df['high']-df['close'].shift()).abs(),
                     (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
    atr_ = tr_.ewm(span=n, adjust=False).mean()
    pdi = 100 * pd.Series(pdm, index=df.index).ewm(span=n, adjust=False).mean() / atr_
    ndi = 100 * pd.Series(ndm, index=df.index).ewm(span=n, adjust=False).mean() / atr_
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi + 1e-9)
    return dx.ewm(span=n, adjust=False).mean()

def bb_width(df, n=20):
    m = sma(df['close'], n)
    s = df['close'].rolling(n).std()
    return (4 * s) / (m + 1e-9)

def volume_surge(df, n=20):
    if 'volume' not in df.columns:
        return pd.Series(1.0, index=df.index)
    avg = df['volume'].rolling(n).mean()
    return df['volume'] / (avg + 1e-9)

def is_mid_month(dt_series):
    day = dt_series.dt.day
    total = dt_series.dt.days_in_month
    return day <= (total - 4)

def is_quarter_end_skip(dt_series):
    month = dt_series.dt.month
    day = dt_series.dt.day
    total = dt_series.dt.days_in_month
    qe_month = month.isin([3, 6, 9, 12])
    last_week = day >= (total - 6)
    return qe_month & last_week

def subperiod(dt_series):
    y = dt_series.dt.year
    bins = [('2010-14', 2010, 2014), ('2015-19', 2015, 2019),
            ('2020-22', 2020, 2022), ('2023-24', 2023, 2024)]
    result = pd.Series('other', index=dt_series.index)
    for name, y0, y1 in bins:
        result[(y >= y0) & (y <= y1)] = name
    return result

def simulate_trades(df, entry_mask, direction='BUY', hold=3, tp=TP_PIPS, sl=SL_PIPS):
    results = []
    idxs = df.index[entry_mask].tolist()
    for i in idxs:
        if i + hold >= len(df):
            continue
        entry = df.at[i, 'close']
        sub = df.iloc[i+1:i+hold+1]
        if direction == 'BUY':
            tp_price = entry + tp * PIP
            sl_price = entry - sl * PIP
            hit_tp = sub['high'] >= tp_price
            hit_sl = sub['low'] <= sl_price
        else:
            tp_price = entry - tp * PIP
            sl_price = entry + sl * PIP
            hit_tp = sub['low'] <= tp_price
            hit_sl = sub['high'] >= sl_price

        exit_price = df.at[i+hold, 'close']
        won = False
        if hit_tp.any() and hit_sl.any():
            tp_bar = hit_tp.idxmax()
            sl_bar = hit_sl.idxmax()
            if tp_bar <= sl_bar:
                exit_price = tp_price; won = True
            else:
                exit_price = sl_price
        elif hit_tp.any():
            exit_price = tp_price; won = True
        elif hit_sl.any():
            exit_price = sl_price

        if direction == 'BUY':
            gross_pips = (exit_price - entry) / PIP
        else:
            gross_pips = (entry - exit_price) / PIP
        net_pips = gross_pips - COST_PIPS
        results.append({
            'dt': df.at[i, 'dt'],
            'won': won,
            'net_pips': net_pips,
            'gross_pips': gross_pips,
        })
    return pd.DataFrame(results) if results else pd.DataFrame(columns=['dt','won','net_pips','gross_pips'])

def pf_stats(trades):
    if len(trades) == 0:
        return {'n': 0, 'wr': 0, 'pf': 0, 'avg_net': 0}
    wins = trades[trades['won']]
    losses = trades[~trades['won']]
    gross_win = wins['net_pips'].sum()
    gross_loss = losses['net_pips'].abs().sum()
    pf = gross_win / gross_loss if gross_loss > 0 else 99.0
    wr = len(wins) / len(trades) * 100
    return {'n': len(trades), 'wr': round(wr,1), 'pf': round(pf,2), 'avg_net': round(trades['net_pips'].mean(),2)}

def subperiod_breakdown(trades):
    if len(trades) == 0:
        return {}
    trades = trades.copy()
    trades['period'] = subperiod(trades['dt'])
    out = {}
    for p in ['2010-14','2015-19','2020-22','2023-24']:
        sub = trades[trades['period']==p]
        s = pf_stats(sub)
        out[p] = f"n={s['n']} WR={s['wr']}% PF={s['pf']}"
    return out

def flag(pf_val):
    if pf_val >= 2.33: return '★★★'
    if pf_val >= 2.0: return '★★'
    if pf_val >= 1.5: return '★'
    return ''

# ─────────────────────────────────────────────
print("Loading M30 data...")
m30 = load_multipart('EURUSD_M30_FXOpen')
if m30 is None:
    m30 = load_csv(f'{DATA}/EURUSD_M30_FXOpen.csv')
print(f"  M30: {len(m30)} bars, {m30['dt'].min()} - {m30['dt'].max()}")

print("Loading M15 data...")
m15 = load_csv(f'{DATA}/EURUSD_M15_FXOpen.csv')
print(f"  M15: {len(m15)} bars")

print("Loading H1 data...")
h1 = load_csv(f'{DATA}/EURUSD_H1_FXOpen.csv')
print(f"  H1: {len(h1)} bars")

print("Loading H4 data...")
h4 = load_csv(f'{DATA}/EURUSD_H4_FXOpen.csv')
print(f"  H4: {len(h4)} bars")

print("Loading M5 (part1 only for coherence)...")
m5 = load_csv(f'{DATA}/EURUSD_M5_FXOpen_part1.csv')
print(f"  M5 part1: {len(m5)} bars")

print("Loading M1 (part1 only for coherence)...")
m1 = load_csv(f'{DATA}/EURUSD_M1_FXOpen_part1.csv')
print(f"  M1 part1: {len(m1)} bars")

# ─────────────────────────────────────────────
# Build indicators on M30
print("\nBuilding M30 indicators...")
m30['slope5'] = slope_pips(m30, 5)
m30['state'] = weather_state(m30['slope5'])
m30['fpcs_val'] = fpcs(m30)
m30['atr14'] = atr(m30)
m30['adx14'] = adx(m30)
m30['bb_w'] = bb_width(m30)
m30['vol_surge'] = volume_surge(m30)
m30['mid_month'] = is_mid_month(m30['dt'])
m30['qe_skip'] = is_quarter_end_skip(m30['dt'])
m30['sma5'] = sma(m30['close'], 5)
m30['sma10'] = sma(m30['close'], 10)
m30['sma20'] = sma(m30['close'], 20)
m30['price_dist_sma5'] = (m30['close'] - m30['sma5']) / PIP
m30['price_dist_sma10'] = (m30['close'] - m30['sma10']) / PIP

# T92 base mask
t92_base = (
    (m30['state'] == 'HURR') &
    (m30['fpcs_val'] > 1.0) &
    m30['mid_month'] &
    ~m30['qe_skip']
)

results = []

def record(name, trades, notes=''):
    s = pf_stats(trades)
    sub = subperiod_breakdown(trades)
    f = flag(s['pf'])
    row = {'signal': name, **s, 'flag': f,
           '2010-14': sub.get('2010-14',''), '2015-19': sub.get('2015-19',''),
           '2020-22': sub.get('2020-22',''), '2023-24': sub.get('2023-24',''),
           'notes': notes}
    results.append(row)
    if s['pf'] >= 2.33 and s['n'] >= 15:
        print(f"  🔥 IMMEDIATE FLAG: {name} n={s['n']} WR={s['wr']}% PF={s['pf']} {f}")
    else:
        print(f"  {name}: n={s['n']} WR={s['wr']}% PF={s['pf']} {f}")
    return trades

# ─────────────────────────────────────────────
print("\n=== T92 BASELINE ===")
t92_trades = simulate_trades(m30, t92_base)
record('T92_M30_baseline', t92_trades)

# ─────────────────────────────────────────────
print("\n=== MA PROXIMITY GATE (T108 family) ===")
# Theory: closer to MA = stronger buy when slopes positive
# Bucket: within X pips of SMA5

for thresh in [5, 10, 15, 20]:
    close_to_sma5 = m30['price_dist_sma5'].abs() <= thresh
    mask = t92_base & close_to_sma5
    t = simulate_trades(m30, mask)
    record(f'T108a_MA_prox_sma5_{thresh}p', t, f'price within {thresh}p of SMA5')

for thresh in [10, 20, 30]:
    close_to_sma10 = m30['price_dist_sma10'].abs() <= thresh
    mask = t92_base & close_to_sma10
    t = simulate_trades(m30, mask)
    record(f'T108b_MA_prox_sma10_{thresh}p', t, f'price within {thresh}p of SMA10')

# ─────────────────────────────────────────────
print("\n=== MMR MEAN REVERSION (T109 family) ===")
# WIND/BREEZE state, price stretched far from MA, snap-back expected

m30['slope5_prev'] = m30['slope5'].shift(1)
m30['slope_flatten'] = (m30['slope5'].abs() < m30['slope5_prev'].abs())

wind_breeze = m30['state'].isin(['WIND', 'BREEZE'])

# MMR BUY: price below SMA10 by X pips, slope still positive
for stretch in [10, 20, 30]:
    mmr_buy = (
        wind_breeze &
        (m30['price_dist_sma10'] < -stretch) &
        (m30['slope5'] > 0)
    )
    t = simulate_trades(m30, mmr_buy, direction='BUY', tp=15, sl=10, hold=5)
    record(f'T109_MMR_BUY_stretch_{stretch}p', t, 'dip below SMA10, slope positive')

# MMR SELL: price above SMA10 by X pips, slope flattening
for stretch in [10, 20, 30]:
    mmr_sell = (
        wind_breeze &
        (m30['price_dist_sma10'] > stretch) &
        m30['slope_flatten']
    )
    t = simulate_trades(m30, mmr_sell, direction='SELL', tp=15, sl=10, hold=5)
    record(f'T109_MMR_SELL_stretch_{stretch}p', t, 'spike above SMA10, slope flattening')

# ─────────────────────────────────────────────
print("\n=== NEW ADAPTIVE GATES on T92 (T110-T113) ===")
# T110: ATR regime — skip if ATR14 > 2× rolling avg (too wild)
atr_avg = m30['atr14'].rolling(50).mean()
atr_calm = m30['atr14'] <= 2.0 * atr_avg

t = simulate_trades(m30, t92_base & atr_calm)
record('T110_T92_ATR_calm', t, 'skip if ATR > 2x rolling avg')

atr_hot = m30['atr14'] > 1.5 * atr_avg
t = simulate_trades(m30, t92_base & atr_hot)
record('T110b_T92_ATR_hot', t, 'entry only if ATR > 1.5x avg (active regime)')

# T111: ADX threshold — enter only if ADX > 25 (trend confirmed)
t = simulate_trades(m30, t92_base & (m30['adx14'] > 25))
record('T111a_T92_ADX25', t, 'ADX>25')
t = simulate_trades(m30, t92_base & (m30['adx14'] > 30))
record('T111b_T92_ADX30', t, 'ADX>30')
t = simulate_trades(m30, t92_base & (m30['adx14'] > 20))
record('T111c_T92_ADX20', t, 'ADX>20')

# T112: Volume surge — enter only if volume 1.5× above avg
vsurge = m30['vol_surge'] > 1.5
t = simulate_trades(m30, t92_base & vsurge)
record('T112a_T92_volsurge_1.5x', t, 'volume > 1.5x avg')
vsurge2 = m30['vol_surge'] > 2.0
t = simulate_trades(m30, t92_base & vsurge2)
record('T112b_T92_volsurge_2x', t, 'volume > 2x avg')

# T113: BB width — skip if BB too narrow (compression) or too wide (blow-off)
bb_mid_lo = m30['bb_w'].rolling(50).quantile(0.25)
bb_mid_hi = m30['bb_w'].rolling(50).quantile(0.75)
bb_normal = (m30['bb_w'] >= bb_mid_lo) & (m30['bb_w'] <= bb_mid_hi)
t = simulate_trades(m30, t92_base & bb_normal)
record('T113_T92_BB_normal_width', t, 'BB width in 25-75th pct')

bb_wide = m30['bb_w'] >= bb_mid_hi
t = simulate_trades(m30, t92_base & bb_wide)
record('T113b_T92_BB_wide', t, 'BB width >75th pct (expanded)')

# ─────────────────────────────────────────────
print("\n=== LARGE TF CONTEXT GATES (H1/H4 directional confirmation) ===")
# Merge H1 slope as a filter — if H1 slope positive, confirm BUY on M30

h1['slope5'] = slope_pips(h1, 5)
h1['state'] = weather_state(h1['slope5'])
h1_hurr_wind = h1['state'].isin(['HURR', 'WIND', 'STORM'])
h1_pos_slope = h1['slope5'] > 0

h4['slope5'] = slope_pips(h4, 5)
h4_pos_slope = h4['slope5'] > 0

# Align H1 to M30 timestamps
m30_dt = m30['dt'].values
h1_dt = h1['dt'].values

# Create a boolean array: for each M30 bar, was H1 slope positive at that time?
h1_pos_idx = pd.Series(h1_pos_slope.values, index=h1['dt'])
h1_hurr_idx = pd.Series(h1_hurr_wind.values, index=h1['dt'])

def align_tf(m30_df, src_series):
    """For each M30 bar, find most recent src value"""
    src = src_series.sort_index()
    result = pd.Series(False, index=m30_df.index)
    for i, row_dt in enumerate(m30_df['dt']):
        past = src[src.index <= row_dt]
        if len(past):
            result.iloc[i] = bool(past.iloc[-1])
    return result

print("  Aligning H1 -> M30 (this may take a moment)...")
# Use merge_asof for efficiency
m30_tmp = m30[['dt']].copy()
h1_tmp = h1[['dt','slope5']].copy()
h1_tmp.columns = ['dt','h1_slope5']
merged = pd.merge_asof(m30_tmp.sort_values('dt'), h1_tmp.sort_values('dt'),
                       on='dt', direction='backward')
merged.index = m30_tmp.index
m30['h1_slope5'] = merged['h1_slope5'].values

h4_tmp = h4[['dt','slope5']].copy()
h4_tmp.columns = ['dt','h4_slope5']
merged4 = pd.merge_asof(m30_tmp.sort_values('dt'), h4_tmp.sort_values('dt'),
                        on='dt', direction='backward')
merged4.index = m30_tmp.index
m30['h4_slope5'] = merged4['h4_slope5'].values

h1_confirm = m30['h1_slope5'] > 0
h4_confirm = m30['h4_slope5'] > 0

t = simulate_trades(m30, t92_base & h1_confirm)
record('T114a_T92_H1_confirm', t, 'H1 slope positive at entry')

t = simulate_trades(m30, t92_base & h4_confirm)
record('T114b_T92_H4_confirm', t, 'H4 slope positive at entry')

t = simulate_trades(m30, t92_base & h1_confirm & h4_confirm)
record('T114c_T92_H1_H4_both', t, 'both H1 and H4 slope positive')

t = simulate_trades(m30, t92_base & ~h1_confirm)
record('T114d_T92_H1_negative', t, 'H1 slope negative (counter)')

# ─────────────────────────────────────────────
print("\n=== MULTI-TF COHERENCE MATRIX (M15 coherence on T92 M30 entries) ===")
# Build M15 slope indicators at various periods and shifts
# then check if M15 agrees (positive slope = BUY signal) at entry time

m15['atr14'] = atr(m15)
m15_tmp = m15[['dt']].copy()

coherence_scores = pd.DataFrame(index=m30.index)
coherence_scores['dt'] = m30['dt'].values
vote_cols = []

for period in [2, 5, 10]:
    for shift in range(0, 6):
        m15[f'slope_p{period}_s{shift}'] = slope_pips(m15, period).shift(shift)
        col = f'coh_m15_p{period}_s{shift}'
        src = m15[['dt', f'slope_p{period}_s{shift}']].copy()
        src.columns = ['dt', 'val']
        merged_coh = pd.merge_asof(
            m30_tmp.sort_values('dt'), src.sort_values('dt'),
            on='dt', direction='backward'
        )
        merged_coh.index = m30_tmp.index
        coherence_scores[col] = (merged_coh['val'].values > 0).astype(int)
        vote_cols.append(col)

# Score = sum of votes
coherence_scores['total_votes'] = coherence_scores[vote_cols].sum(axis=1)
total_possible = len(vote_cols)

m30['coh_score'] = coherence_scores['total_votes'].values

# Test various thresholds
print(f"  Total coherence combos: {total_possible}")
for min_votes in [10, 14, 18]:
    pct = round(min_votes/total_possible*100)
    mask = t92_base & (m30['coh_score'] >= min_votes)
    t = simulate_trades(m30, mask)
    record(f'T115_T92_coh_M15_{min_votes}of{total_possible}({pct}%)', t,
           f'M15 coherence: {min_votes}/{total_possible} combos agree')

# ─────────────────────────────────────────────
print("\n=== COMBO CLONES (T116 best combinations) ===")
t = simulate_trades(m30, t92_base & h1_confirm & (m30['adx14'] > 25))
record('T116a_T92_H1_ADX25', t, 'H1 confirm + ADX>25')

t = simulate_trades(m30, t92_base & h1_confirm & h4_confirm & (m30['adx14'] > 20))
record('T116b_T92_H1_H4_ADX20', t, 'H1+H4 confirm + ADX>20')

# MA proximity + H1
close_to_sma5_10 = m30['price_dist_sma5'].abs() <= 10
t = simulate_trades(m30, t92_base & close_to_sma5_10 & h1_confirm)
record('T116c_T92_prox10p_H1', t, 'within 10p SMA5 + H1 confirm')

# ATR calm + H1
t = simulate_trades(m30, t92_base & atr_calm & h1_confirm)
record('T116d_T92_ATR_calm_H1', t, 'ATR calm + H1 confirm')

# Coherence + H1
high_coh = m30['coh_score'] >= 14
t = simulate_trades(m30, t92_base & high_coh & h1_confirm)
record('T116e_T92_coh14_H1', t, 'coherence>=14 + H1 confirm')

# ─────────────────────────────────────────────
print("\n=== SAVING RESULTS ===")
out = pd.DataFrame(results)
out_path = '/mnt/project-files/backups/COHERENCE_BATCH_20261031.txt'
with open(out_path, 'w') as f:
    f.write("MULTI-TF COHERENCE + MA PROXIMITY + MMR MEAN REVERSION BATCH\n")
    f.write(f"Run: {datetime.utcnow().strftime('%Y-%m-%d %H:%MZ')}\n")
    f.write(f"Data: FXOpen ECN EURUSD 2010-2024, Cost: {COST_PIPS}pip RT\n")
    f.write(f"TP={TP_PIPS}p SL={SL_PIPS}p Hold={HOLD_BARS_M30} bars (M30)\n\n")

    sections = {
        'T92 BASELINE': [r for r in results if 'baseline' in r['signal']],
        'T108 MA PROXIMITY': [r for r in results if 'T108' in r['signal']],
        'T109 MMR MEAN REVERSION': [r for r in results if 'T109' in r['signal']],
        'T110-T113 ADAPTIVE GATES': [r for r in results if any(x in r['signal'] for x in ['T110','T111','T112','T113'])],
        'T114 LARGE TF CONTEXT': [r for r in results if 'T114' in r['signal']],
        'T115 MULTI-TF COHERENCE': [r for r in results if 'T115' in r['signal']],
        'T116 COMBO CLONES': [r for r in results if 'T116' in r['signal']],
    }

    for sec_name, sec_rows in sections.items():
        f.write(f"\n{'='*60}\n{sec_name}\n{'='*60}\n")
        for r in sec_rows:
            flag_str = r.get('flag','')
            f.write(f"\n{r['signal']} {flag_str}\n")
            f.write(f"  n={r['n']} WR={r['wr']}% PF={r['pf']} avg_net={r['avg_net']}p  [{r['notes']}]\n")
            for p in ['2010-14','2015-19','2020-22','2023-24']:
                if r.get(p):
                    f.write(f"  {p}: {r[p]}\n")

    f.write(f"\n\n{'='*60}\nSURVIVORS (PF>=2.0, n>=15)\n{'='*60}\n")
    survivors = [r for r in results if r['pf'] >= 2.0 and r['n'] >= 15]
    survivors.sort(key=lambda x: -x['pf'])
    for r in survivors:
        f.write(f"{r['signal']}: n={r['n']} WR={r['wr']}% PF={r['pf']} {r['flag']}\n")
        for p in ['2010-14','2015-19','2020-22','2023-24']:
            if r.get(p):
                f.write(f"  {p}: {r[p]}\n")

print(f"\nSaved: {out_path}")
print(f"\nSURVIVORS (PF>=2.0, n>=15):")
for r in sorted([r for r in results if r['pf'] >= 2.0 and r['n'] >= 15], key=lambda x: -x['pf']):
    print(f"  {r['signal']}: n={r['n']} WR={r['wr']}% PF={r['pf']} {r['flag']}")
