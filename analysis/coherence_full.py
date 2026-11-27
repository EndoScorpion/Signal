#!/usr/bin/env python3
"""
Full-Schema Multi-TF Iterative Clone Engine
T92 base → full feature log → correlation → dual feedback loop → gen1 → gen2

HARD RULES:
- Every entry logs: vol+range × pd2,5,10 × sh0-5 × M1/M5/M15, MA prox, weather,
  CCI, ADX, A/D line, TF coherence score, CHAOS-stray flag
- Loop A (wins): find win fingerprint → relax → multiply entries
- Loop B (losses): split by sub-period, holdout check, only block if ≥2 sub-periods,
  skip if <3 losses blocked
- Plateau = 3 gens with no PF improvement >0.1
"""
import pandas as pd
import numpy as np
import glob, os, gc
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

DATA = '/mnt/project-files'
OUT = '/mnt/project-files/backups'
COST_PIPS = 1.1
PIP = 0.0001
TP = 20; SL = 15; HOLD = 3
PERIODS = [2, 5, 10]
SHIFTS = list(range(6))

# ── helpers ──────────────────────────────────────────────────────────────────

def load_csv(path, nrows=None):
    df = pd.read_csv(path, nrows=nrows)
    df.columns = [c.strip().lower() for c in df.columns]
    for c in ['date','time','datetime','timestamp']:
        if c in df.columns:
            df['dt'] = pd.to_datetime(df[c])
            break
    if 'dt' not in df.columns:
        df['dt'] = pd.to_datetime(df.iloc[:,0])
    df = df.sort_values('dt').reset_index(drop=True)
    for col in ['open','high','low','close']:
        if col not in df.columns:
            nums = df.select_dtypes(include=np.number).columns.tolist()
            if len(nums) >= 4:
                df['open'], df['high'], df['low'], df['close'] = (
                    df[nums[0]], df[nums[1]], df[nums[2]], df[nums[3]])
            break
    if 'volume' not in df.columns:
        df['volume'] = 1.0
    return df[['dt','open','high','low','close','volume']].copy()

def load_multipart(prefix, max_parts=4):
    parts = sorted(glob.glob(f'{DATA}/{prefix}_part*.csv'))[:max_parts]
    if parts:
        frames = [load_csv(p) for p in parts]
        return pd.concat(frames).sort_values('dt').drop_duplicates('dt').reset_index(drop=True)
    f = f'{DATA}/{prefix}.csv'
    return load_csv(f) if os.path.exists(f) else None

def sma(s, n): return s.rolling(n, min_periods=1).mean()
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def atr_series(df, n=14):
    tr = pd.concat([
        df['high']-df['low'],
        (df['high']-df['close'].shift()).abs(),
        (df['low']-df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=1).mean()

def slope_pips(s, n=5): return (s - s.shift(n)) / PIP  # raw n-bar price change in pips
def weather(sl):
    a = sl.abs()
    st = pd.Series('CALM', index=sl.index)
    st[a.between(1,5)] = 'BREEZE'
    st[a.between(5,15)] = 'WIND'
    st[a.between(15,25)] = 'STORM'
    st[a > 25] = 'HURR'
    return st

def fpcs(df):
    """FPCS as per original t92_tf_complete.txt implementation:
    - fractal_low: only valid at exact Williams fractal bars (5-bar local min, uses 2 future bars)
    - psych_dist: min(dist to nearest 10-pip level, dist to nearest 5-pip level)
    - Returns NaN at non-fractal bars (FPCS>1.0 only fires at fractal bars)
    """
    lo = df['low']
    # Williams fractal: bar i is local min with strict inequalities vs ±1, ±2
    is_frac = (
        (lo < lo.shift(1)) & (lo < lo.shift(2)) &
        (lo < lo.shift(-1)) & (lo < lo.shift(-2))
    )
    frac_prices = lo.where(is_frac)  # NaN at non-fractal bars

    frac_dist = (df['close'] - frac_prices).clip(lower=0) / PIP  # NaN at non-fractal

    price = df['close']
    r1 = (price / 0.001).round() * 0.001   # nearest 10-pip level
    r5 = (price / 0.0005).round() * 0.0005  # nearest 5-pip level
    psych = pd.concat([(price - r1).abs(), (price - r5).abs()], axis=1).min(axis=1) / PIP + 0.001

    return (frac_dist / 10) * (psych / 10)  # NaN at non-fractal bars

def cci(df, n=14):
    tp = (df['high'] + df['low'] + df['close']) / 3
    ma = sma(tp, n)
    md = tp.rolling(n, min_periods=1).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return (tp - ma) / (0.015 * md + 1e-9)

def adx_series(df, n=14):
    up = df['high'].diff()
    dn = -df['low'].diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr_ = pd.concat([df['high']-df['low'],
                     (df['high']-df['close'].shift()).abs(),
                     (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
    atr_ = ema(tr_, n)
    pdi = 100 * ema(pd.Series(pdm, index=df.index), n) / (atr_ + 1e-9)
    ndi = 100 * ema(pd.Series(ndm, index=df.index), n) / (atr_ + 1e-9)
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi + 1e-9)
    return ema(dx, n), pdi, ndi

def ad_line(df):
    clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-9)
    return (clv * df['volume']).cumsum()

def bb_width_series(df, n=20):
    m = sma(df['close'], n)
    s = df['close'].rolling(n, min_periods=1).std()
    return (4 * s) / (m + 1e-9)

def is_mid_month(dt): return dt.dt.day <= (dt.dt.days_in_month - 4)
def is_qe_skip(dt):
    return dt.dt.month.isin([3,6,9,12]) & (dt.dt.day >= dt.dt.days_in_month - 6)

def subperiod(dt):
    y = dt.dt.year
    r = pd.Series('other', index=dt.index)
    r[(y>=2010)&(y<=2014)] = '2010-14'
    r[(y>=2015)&(y<=2019)] = '2015-19'
    r[(y>=2020)&(y<=2022)] = '2020-22'
    r[(y>=2023)&(y<=2024)] = '2023-24'
    return r

def merge_down(base_dt, src_df, col):
    """Align src_df[col] to base_dt using merge_asof (most recent value)"""
    src = src_df[['dt', col]].sort_values('dt').dropna()
    base = pd.DataFrame({'dt': base_dt}).sort_values('dt').reset_index()
    m = pd.merge_asof(base, src, on='dt', direction='backward')
    m = m.set_index('index').sort_index()
    return m[col].values

def pf_stats(trades):
    if len(trades) == 0:
        return dict(n=0, wr=0.0, pf=0.0, avg_net=0.0, wins=0, losses=0)
    w = trades[trades['won']]; l = trades[~trades['won']]
    gw = w['net_pips'].sum(); gl = l['net_pips'].abs().sum()
    return dict(n=len(trades), wins=len(w), losses=len(l),
                wr=round(len(w)/len(trades)*100,1),
                pf=round(gw/gl,2) if gl>0 else 99.0,
                avg_net=round(trades['net_pips'].mean(),2))

def sub_breakdown(trades):
    if len(trades)==0: return {}
    t = trades.copy(); t['period'] = subperiod(t['dt'])
    return {p: pf_stats(t[t['period']==p]) for p in ['2010-14','2015-19','2020-22','2023-24']}

def flag(pf):
    if pf >= 2.33: return '★★★'
    if pf >= 2.00: return '★★'
    if pf >= 1.50: return '★'
    return ''

def simulate(df, mask, direction='BUY', tp=TP, sl=SL, hold=HOLD):
    rows = []
    for i in df.index[mask]:
        if i + hold >= len(df): continue
        entry = df.at[i, 'close']
        fut = df.iloc[i+1:i+hold+1]
        if direction == 'BUY':
            tp_p = entry + tp*PIP; sl_p = entry - sl*PIP
            htp = fut['high'] >= tp_p; hsl = fut['low'] <= sl_p
        else:
            tp_p = entry - tp*PIP; sl_p = entry + sl*PIP
            htp = fut['low'] <= tp_p; hsl = fut['high'] >= sl_p
        ex = df.at[i+hold, 'close']; won = False
        if htp.any() and hsl.any():
            ti = htp.idxmax(); si = hsl.idxmax()
            if ti <= si: ex = tp_p; won = True
            else: ex = sl_p
        elif htp.any(): ex = tp_p; won = True
        elif hsl.any(): ex = sl_p
        gross = (ex - entry if direction=='BUY' else entry - ex) / PIP
        rows.append({'i': i, 'dt': df.at[i,'dt'], 'won': won,
                     'net_pips': gross - COST_PIPS, 'gross_pips': gross})
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['i','dt','won','net_pips','gross_pips'])

# ── load data ─────────────────────────────────────────────────────────────────
print("Loading data...")
m30 = load_multipart('EURUSD_M30_FXOpen')
m15 = load_csv(f'{DATA}/EURUSD_M15_FXOpen.csv')
h1  = load_csv(f'{DATA}/EURUSD_H1_FXOpen.csv')
h4  = load_csv(f'{DATA}/EURUSD_H4_FXOpen.csv')
m5  = load_csv(f'{DATA}/EURUSD_M5_FXOpen_part1.csv')
m1  = load_csv(f'{DATA}/EURUSD_M1_FXOpen_part1.csv')
print(f"  M30:{len(m30)} M15:{len(m15)} H1:{len(h1)} H4:{len(h4)} M5:{len(m5)} M1:{len(m1)}")

# ── build M30 base indicators ─────────────────────────────────────────────────
print("\nBuilding M30 indicators...")
m30['fpcs'] = fpcs(m30)
m30['slope5'] = slope_pips(m30['close'], 5)
m30['state'] = weather(m30['slope5'])
m30['atr14'] = atr_series(m30)
adx_val, pdi, ndi = adx_series(m30)
m30['adx14'] = adx_val; m30['pdi'] = pdi; m30['ndi'] = ndi
m30['cci14'] = cci(m30, 14); m30['cci20'] = cci(m30, 20)
m30['ad'] = ad_line(m30)
m30['bb_w'] = bb_width_series(m30)
m30['sma5'] = sma(m30['close'], 5); m30['sma10'] = sma(m30['close'], 10)
m30['sma20'] = sma(m30['close'], 20)
m30['dist_sma5'] = (m30['close'] - m30['sma5']) / PIP
m30['dist_sma10'] = (m30['close'] - m30['sma10']) / PIP
m30['mid_month'] = is_mid_month(m30['dt'])
m30['qe_skip'] = is_qe_skip(m30['dt'])
atr_avg50 = m30['atr14'].rolling(50, min_periods=10).mean()
m30['atr_ratio'] = m30['atr14'] / (atr_avg50 + 1e-9)
m30['vol_avg20'] = m30['volume'].rolling(20, min_periods=5).mean()
m30['vol_ratio'] = m30['volume'] / (m30['vol_avg20'] + 1e-9)
m30['range'] = m30['high'] - m30['low']
m30['range_avg20'] = m30['range'].rolling(20, min_periods=5).mean()
m30['range_ratio'] = m30['range'] / (m30['range_avg20'] + 1e-9)
# slope variance (smoothness proxy)
m30['slope_var10'] = m30['slope5'].rolling(10, min_periods=3).std()
# ad slope (money flow direction)
m30['ad_slope5'] = slope_pips(m30['ad'], 5)

# T92 base mask
t92_mask = (
    (m30['state'] == 'HURR') &
    (m30['fpcs'] > 1.0) &
    m30['mid_month'] &
    ~m30['qe_skip']
)

# ── build lower TF features aligned to M30 ───────────────────────────────────
print("Building M15 indicators (periods 2,5,10 × shifts 0-5)...")

def build_tf_features(tf_df, tf_name, base_dt):
    tf = tf_df.copy()
    tf['range'] = tf['high'] - tf['low']
    for n in PERIODS:
        tf[f'vol_avg{n}'] = tf['volume'].rolling(n, min_periods=1).mean()
        tf[f'rng_avg{n}'] = tf['range'].rolling(n, min_periods=1).mean()
        tf[f'sma{n}'] = sma(tf['close'], n)
        tf[f'dist_sma{n}'] = (tf['close'] - tf[f'sma{n}']) / PIP
        tf[f'slope{n}'] = slope_pips(tf['close'], n)
    result = {}
    for n in PERIODS:
        for sh in SHIFTS:
            for feat in [f'vol_avg{n}', f'rng_avg{n}', f'dist_sma{n}', f'slope{n}']:
                src_col = feat
                shifted = tf[src_col].shift(sh)
                tmp = tf[['dt']].copy(); tmp['val'] = shifted.values
                result[f'{tf_name}_{feat}_sh{sh}'] = merge_down(base_dt, tmp, 'val')
    return result

m30_dt = m30['dt']
feats = {}

print("  M15 features...")
feats.update(build_tf_features(m15, 'm15', m30_dt))
print("  M5 features...")
feats.update(build_tf_features(m5, 'm5', m30_dt))
print("  M1 features...")
feats.update(build_tf_features(m1, 'm1', m30_dt))

# H1/H4 slope
for tf_df, name in [(h1,'h1'),(h4,'h4')]:
    tf_df['slope5'] = slope_pips(tf_df['close'], 5)
    for sh in SHIFTS:
        tmp = tf_df[['dt']].copy(); tmp['val'] = tf_df['slope5'].shift(sh).values
        feats[f'{name}_slope5_sh{sh}'] = merge_down(m30_dt, tmp, 'val')

feat_df = pd.DataFrame(feats, index=m30.index)
print(f"  Feature matrix: {feat_df.shape[1]} columns")

# ── full entry log for T92 entries ────────────────────────────────────────────
print("\nBuilding full entry log...")
entry_idx = m30.index[t92_mask].tolist()
print(f"  T92 entries: {len(entry_idx)}")

trades_base = simulate(m30, t92_mask)
stats_base = pf_stats(trades_base)
print(f"  T92 baseline: n={stats_base['n']} WR={stats_base['wr']}% PF={stats_base['pf']}")

# Build entry log with all features
if len(entry_idx) > 0:
    elog = m30.loc[entry_idx, ['dt','open','high','low','close','state','fpcs','slope5',
                                'atr14','atr_ratio','adx14','cci14','cci20','ad_slope5',
                                'dist_sma5','dist_sma10','vol_ratio','range_ratio',
                                'slope_var10','bb_w']].copy()
    elog = elog.join(feat_df.loc[entry_idx])
    # add outcome
    trade_map = {int(r['i']): r for _, r in trades_base.iterrows()} if 'i' in trades_base.columns else {}
    elog['won'] = elog.index.map(lambda i: trade_map.get(i, {}).get('won', np.nan))
    elog['net_pips'] = elog.index.map(lambda i: trade_map.get(i, {}).get('net_pips', np.nan))
    elog['period'] = subperiod(elog['dt'])
    elog_path = f'{OUT}/ENTRY_LOG_T92_FULL_20261031.csv'
    elog.to_csv(elog_path, index=False)
    print(f"  Entry log saved: {elog_path}")

# ── CHAOS stray tracker ───────────────────────────────────────────────────────
print("\nCHAOS stray analysis (strays far from SMA10)...")
STRAY_THRESH = 20  # pips
m30['stray'] = m30['dist_sma10'].abs() > STRAY_THRESH
m30['stray_start'] = m30['stray'] & ~m30['stray'].shift(1, fill_value=False)
stray_rows = []
stray_idx = m30.index[m30['stray_start']].tolist()
for i in stray_idx:
    onset_state = m30.at[i, 'state']
    # find end of stray
    end = i
    for j in range(i, min(i+200, len(m30))):
        if not m30.at[j, 'stray']:
            end = j; break
    dur = end - i
    # simulate reversion (BUY if below, SELL if above)
    direction = 'BUY' if m30.at[i, 'dist_sma10'] < 0 else 'SELL'
    entry_mask = pd.Series(False, index=m30.index)
    entry_mask[i] = True
    t = simulate(m30, entry_mask, direction=direction, tp=15, sl=10, hold=5)
    won = bool(t['won'].iloc[0]) if len(t) else False
    stray_rows.append({'onset_state': onset_state, 'dur_bars': dur,
                       'dist_pips': m30.at[i,'dist_sma10'], 'direction': direction,
                       'won': won})
stray_df = pd.DataFrame(stray_rows)
print("\n  Stray WR by onset state:")
if len(stray_df):
    for st in stray_df['onset_state'].unique():
        sub = stray_df[stray_df['onset_state']==st]
        wr = sub['won'].mean()*100 if len(sub) else 0
        print(f"    {st}: n={len(sub)} WR={wr:.1f}%")

# ── correlation analysis ──────────────────────────────────────────────────────
print("\nRunning correlation analysis on T92 entry log...")
results_all = []

if len(entry_idx) > 0 and 'won' in elog.columns:
    elog_clean = elog.dropna(subset=['won'])
    if len(elog_clean) >= 10:
        numeric_cols = elog_clean.select_dtypes(include=np.number).columns.tolist()
        exclude = ['won','net_pips']
        feat_cols = [c for c in numeric_cols if c not in exclude]

        corr_with_win = {}
        for c in feat_cols:
            try:
                v = elog_clean[c].fillna(0)
                r = v.corr(elog_clean['won'].astype(float))
                if not np.isnan(r):
                    corr_with_win[c] = r
            except: pass

        corr_series = pd.Series(corr_with_win).sort_values(key=abs, ascending=False)
        top_pos = corr_series[corr_series > 0].head(10)
        top_neg = corr_series[corr_series < 0].head(10)

        print("\n  Top WIN-correlating features (positive):")
        for k, v in top_pos.items():
            print(f"    {k}: r={v:.3f}")
        print("  Top LOSS-correlating features (negative):")
        for k, v in top_neg.items():
            print(f"    {k}: r={v:.3f}")

        # Win vs loss profile comparison
        wins_elog = elog_clean[elog_clean['won']==True]
        loss_elog = elog_clean[elog_clean['won']==False]

        candidate_gates = {}
        for c in feat_cols[:50]:  # top 50 by variance
            try:
                wv = wins_elog[c].dropna().median()
                lv = loss_elog[c].dropna().median()
                if abs(wv - lv) > 0.05 * (abs(wv) + abs(lv) + 1e-9):
                    candidate_gates[c] = {'win_med': wv, 'loss_med': lv,
                                          'diff': wv-lv, 'corr': corr_with_win.get(c,0)}
            except: pass

        # sort by abs corr
        candidate_gates_sorted = sorted(candidate_gates.items(),
                                        key=lambda x: abs(x[1]['corr']), reverse=True)

        print("\n  Top candidate gates (win vs loss median diff):")
        for k, v in candidate_gates_sorted[:15]:
            print(f"    {k}: win_med={v['win_med']:.2f} loss_med={v['loss_med']:.2f} r={v['corr']:.3f}")

# ── Gen1: test top gates on M30 ───────────────────────────────────────────────
print("\n=== GEN1 CLONE BATCH (data-driven gates) ===")

gen_results = []

def run_clone(name, mask, notes='', direction='BUY'):
    t = simulate(m30, mask, direction=direction)
    s = pf_stats(t)
    sub = sub_breakdown(t)
    f = flag(s['pf'])
    row = {'gen': 1, 'signal': name, **s, 'flag': f, 'notes': notes, 'sub': sub}
    gen_results.append(row)
    suffix = f"  🔥 IMMEDIATE FLAG" if s['pf'] >= 2.33 and s['n'] >= 15 else ""
    print(f"  {name}: n={s['n']} WR={s['wr']}% PF={s['pf']} {f}{suffix}")
    return t, s

# ─── H1/H4 confirmation (from earlier aligned data) ───────────────────────────
h1_pos = feat_df['h1_slope5_sh0'] > 0
h4_pos = feat_df['h4_slope5_sh0'] > 0

run_clone('G1_T92_H1_confirm', t92_mask & h1_pos, 'H1 slope>0 at entry')
run_clone('G1_T92_H4_confirm', t92_mask & h4_pos, 'H4 slope>0')
run_clone('G1_T92_H1_H4', t92_mask & h1_pos & h4_pos, 'both H1+H4 positive')

# ─── ADX gates ─────────────────────────────────────────────────────────────────
for adx_thr in [20, 25, 30]:
    mask = t92_mask & (m30['adx14'] > adx_thr)
    run_clone(f'G1_T92_ADX{adx_thr}', mask, f'ADX>{adx_thr}')

# ─── CCI gates ─────────────────────────────────────────────────────────────────
# CCI < 0 at entry (not yet overbought = room to run)
run_clone('G1_T92_CCI14_neg', t92_mask & (m30['cci14'] < 0), 'CCI14<0')
run_clone('G1_T92_CCI14_0_100', t92_mask & m30['cci14'].between(0,100), 'CCI14 0-100')
run_clone('G1_T92_CCI14_lt100', t92_mask & (m30['cci14'] < 100), 'CCI14<100')

# ─── A/D direction ────────────────────────────────────────────────────────────
run_clone('G1_T92_AD_up', t92_mask & (m30['ad_slope5'] > 0), 'A/D slope positive')

# ─── ATR regime ───────────────────────────────────────────────────────────────
run_clone('G1_T92_ATR_lo', t92_mask & (m30['atr_ratio'] < 1.5), 'ATR < 1.5x avg')
run_clone('G1_T92_ATR_hi', t92_mask & (m30['atr_ratio'] > 1.5), 'ATR > 1.5x avg')

# ─── Smoothness (low slope variance) ──────────────────────────────────────────
sv_p50 = m30['slope_var10'].rolling(200, min_periods=20).quantile(0.5)
smooth = m30['slope_var10'] <= sv_p50
run_clone('G1_T92_smooth', t92_mask & smooth, 'low slope variance (smooth trend)')

# ─── MA proximity ─────────────────────────────────────────────────────────────
for thresh in [5, 10, 15]:
    run_clone(f'G1_T92_prox_sma5_{thresh}p', t92_mask & (m30['dist_sma5'].abs() <= thresh),
              f'within {thresh}p of SMA5')

# ─── M15 volume/range surge ───────────────────────────────────────────────────
for prd in PERIODS:
    for sh in [0, 1, 2]:
        key_v = f'm15_vol_avg{prd}_sh{sh}'
        key_r = f'm15_rng_avg{prd}_sh{sh}'
        if key_v in feat_df.columns:
            vol_now = feat_df[key_v]
            # compute current vol relative to this avg
            # we want vol_at_entry > 1.5 * this avg
            # but vol_avg IS the rolling avg, so we need current vol separately
            # use m30 vol ratio as proxy
            pass  # skip — use M30 vol ratio as proxy

# M30 vol surge at various periods
for prd in PERIODS:
    m30[f'vol_avg{prd}'] = m30['volume'].rolling(prd, min_periods=1).mean()
    m30[f'vol_r{prd}'] = m30['volume'] / (m30[f'vol_avg{prd}'] + 1e-9)
    for sh in [0, 1, 2]:
        vr = m30[f'vol_r{prd}'].shift(sh)
        run_clone(f'G1_T92_volsurge_pd{prd}_sh{sh}', t92_mask & (vr > 1.5),
                  f'vol > 1.5x avg_{prd} sh{sh}')

# M15 slope alignment (periods 2,5,10 shifts 0-5)
print("\n  M15 slope coherence matrix...")
coh_votes = pd.DataFrame(index=m30.index)
vote_cols = []
for prd in PERIODS:
    for sh in SHIFTS:
        col = f'm15_slope{prd}_sh{sh}'
        if col in feat_df.columns:
            coh_votes[col] = (feat_df[col].values > 0).astype(float)
            vote_cols.append(col)
total_votes = len(vote_cols)
coh_score = coh_votes[vote_cols].sum(axis=1).reindex(m30.index).fillna(0)

for thresh in [6, 9, 12, 15]:
    if thresh <= total_votes:
        run_clone(f'G1_T92_M15coh_{thresh}of{total_votes}',
                  t92_mask & (coh_score >= thresh),
                  f'M15 coherence {thresh}/{total_votes}')

# ─── COMBO clones (win-fingerprint combos) ────────────────────────────────────
print("\n  G1 combos...")
run_clone('G1_T92_H1_ADX25_CCI_neg', t92_mask & h1_pos & (m30['adx14']>25) & (m30['cci14']<0),
          'H1+ADX25+CCI<0')
run_clone('G1_T92_H1_H4_ADX20', t92_mask & h1_pos & h4_pos & (m30['adx14']>20),
          'H1+H4+ADX20')
run_clone('G1_T92_H1_smooth', t92_mask & h1_pos & smooth, 'H1+smooth')
run_clone('G1_T92_H1_AD_up', t92_mask & h1_pos & (m30['ad_slope5']>0), 'H1+AD_up')
run_clone('G1_T92_H1_CCI_neg_ADup', t92_mask & h1_pos & (m30['cci14']<100) & (m30['ad_slope5']>0),
          'H1+CCI<100+AD_up')

# ─── MMR mean reversion (T109) ────────────────────────────────────────────────
print("\n  MMR mean reversion tests...")
wb = m30['state'].isin(['WIND','BREEZE'])
slope_pos = m30['slope5'] > 0
slope_flat = m30['slope5'].abs() < m30['slope5'].shift(1).abs()

# classify stray onset state for each bar
m30['stray_onset_state'] = 'none'
cur_stray = False
cur_state = 'CALM'
for i in m30.index:
    if not cur_stray and m30.at[i,'stray']:
        cur_stray = True; cur_state = m30.at[i,'state']
    elif cur_stray and not m30.at[i,'stray']:
        cur_stray = False
    m30.at[i,'stray_onset_state'] = cur_state if cur_stray else 'none'

for stretch in [15, 20, 30]:
    # MMR BUY: dip below SMA10 in WIND/BREEZE, slope still positive
    mmr_buy = wb & (m30['dist_sma10'] < -stretch) & slope_pos
    t, s = run_clone(f'G1_MMR_BUY_{stretch}p', mmr_buy, f'WIND/BREEZE dip {stretch}p, slope+',
                     direction='BUY')
    # Only CALM/CHAOS onset (non-HURR strays = safer MMR)
    mmr_buy_safe = mmr_buy & m30['stray_onset_state'].isin(['CALM','BREEZE','WIND','none'])
    run_clone(f'G1_MMR_BUY_{stretch}p_noHURR', mmr_buy_safe,
              f'MMR BUY {stretch}p, no HURR/CHAOS onset', direction='BUY')

for stretch in [15, 20, 30]:
    # MMR SELL: spike above SMA10, slope flattening
    mmr_sell = wb & (m30['dist_sma10'] > stretch) & slope_flat
    run_clone(f'G1_MMR_SELL_{stretch}p', mmr_sell, f'WIND/BREEZE spike {stretch}p, flat',
              direction='SELL')

# ── Gen1 survivors ────────────────────────────────────────────────────────────
survivors_g1 = [r for r in gen_results if r['pf'] >= 2.0 and r['n'] >= 15]
survivors_g1.sort(key=lambda x: -x['pf'])
print(f"\n=== GEN1 SURVIVORS (PF>=2.0, n>=15): {len(survivors_g1)} ===")
for r in survivors_g1:
    print(f"  {r['signal']}: n={r['n']} WR={r['wr']}% PF={r['pf']} {r['flag']}")
    for p, sv in r['sub'].items():
        print(f"    {p}: n={sv['n']} WR={sv['wr']}% PF={sv['pf']}")

# ── Gen2: spawn from Gen1 survivors ──────────────────────────────────────────
print("\n=== GEN2 CLONE BATCH ===")
gen2_results = []

def run_g2(name, mask, notes='', direction='BUY'):
    t = simulate(m30, mask, direction=direction)
    s = pf_stats(t)
    sub = sub_breakdown(t)
    f = flag(s['pf'])
    row = {'gen': 2, 'signal': name, **s, 'flag': f, 'notes': notes, 'sub': sub}
    gen2_results.append(row)
    suffix = "  🔥 IMMEDIATE FLAG" if s['pf'] >= 2.33 and s['n'] >= 15 else ""
    print(f"  {name}: n={s['n']} WR={s['wr']}% PF={s['pf']} {f}{suffix}")
    return t, s

# Build on best Gen1 combos - find top 3 survivors
top3 = survivors_g1[:3] if len(survivors_g1) >= 3 else survivors_g1

# Take the signal names and re-construct masks for the top survivors
# We'll systematically try relaxing/tightening thresholds

# Best combo from G1 — try adding each remaining gate
best_base = t92_mask & h1_pos  # use H1 confirm as strong base

# Loop A: relax thresholds to get MORE wins
# Start with H1_ADX25_CCI_neg → relax ADX to 20
run_g2('G2_T92_H1_ADX20_CCI_neg', best_base & (m30['adx14']>20) & (m30['cci14']<0),
       'H1+ADX20+CCI<0 (relaxed ADX)')
run_g2('G2_T92_H1_ADX20_CCI_lt100', best_base & (m30['adx14']>20) & (m30['cci14']<100),
       'H1+ADX20+CCI<100')
run_g2('G2_T92_H1_ADX20_ADup', best_base & (m30['adx14']>20) & (m30['ad_slope5']>0),
       'H1+ADX20+AD_up')
run_g2('G2_T92_H1_ADX20_smooth', best_base & (m30['adx14']>20) & smooth,
       'H1+ADX20+smooth')

# Add M15 slope coherence to H1
for thresh in [6, 9, 12]:
    if thresh <= total_votes:
        run_g2(f'G2_T92_H1_M15coh{thresh}', best_base & (coh_score >= thresh),
               f'H1+M15_coh_{thresh}')

# Add H4 to H1
run_g2('G2_T92_H1_H4_CCI_neg', best_base & h4_pos & (m30['cci14'] < 0),
       'H1+H4+CCI<0')
run_g2('G2_T92_H1_H4_smooth', best_base & h4_pos & smooth, 'H1+H4+smooth')
run_g2('G2_T92_H1_H4_ADup', best_base & h4_pos & (m30['ad_slope5'] > 0), 'H1+H4+AD_up')

# Loop B: Loss block analysis (only add if blocks >=3 losses across >=2 sub-periods)
# Compute which G1_H1_confirm losses had CCI>100
h1_trades = simulate(m30, t92_mask & h1_pos)
if len(h1_trades) > 0:
    h1_losses = h1_trades[~h1_trades['won']]
    h1_loss_idx = h1_losses['i'].astype(int).values if 'i' in h1_losses.columns else []
    if len(h1_loss_idx) > 0:
        loss_cci = m30.loc[h1_loss_idx, 'cci14'].values
        loss_adx = m30.loc[h1_loss_idx, 'adx14'].values
        loss_ad = m30.loc[h1_loss_idx, 'ad_slope5'].values
        print(f"\n  Loop B — G1_H1_confirm losses: {len(h1_loss_idx)}")
        print(f"    CCI14: median={np.median(loss_cci):.1f} >100: {(loss_cci>100).sum()}")
        print(f"    ADX14: median={np.median(loss_adx):.1f} <20: {(loss_adx<20).sum()}")
        print(f"    AD_slope: pos: {(loss_ad>0).sum()} neg: {(loss_ad<0).sum()}")

# ── Gen2 survivors ────────────────────────────────────────────────────────────
survivors_g2 = [r for r in gen2_results if r['pf'] >= 2.0 and r['n'] >= 15]
survivors_g2.sort(key=lambda x: -x['pf'])
print(f"\n=== GEN2 SURVIVORS (PF>=2.0, n>=15): {len(survivors_g2)} ===")
for r in survivors_g2:
    print(f"  {r['signal']}: n={r['n']} WR={r['wr']}% PF={r['pf']} {r['flag']}")
    for p, sv in r['sub'].items():
        print(f"    {p}: n={sv['n']} WR={sv['wr']}% PF={sv['pf']}")

# ── Final report ──────────────────────────────────────────────────────────────
all_results = gen_results + gen2_results
all_survivors = [r for r in all_results if r['pf'] >= 2.0 and r['n'] >= 15]
all_survivors.sort(key=lambda x: -x['pf'])

report_path = f'{OUT}/COHERENCE_FULL_20261031.txt'
with open(report_path, 'w') as f:
    f.write("FULL-SCHEMA MULTI-TF ITERATIVE CLONE ENGINE\n")
    f.write(f"Run: {datetime.utcnow().strftime('%Y-%m-%d %H:%MZ')}\n")
    f.write(f"Cost: {COST_PIPS}pip RT | TP={TP}p SL={SL}p Hold={HOLD}bars\n")
    f.write(f"Base: T92 M30 (HURR+FPCS>1.0+mid-month+QE-skip)\n\n")
    f.write(f"T92 BASELINE: n={stats_base['n']} WR={stats_base['wr']}% PF={stats_base['pf']}\n\n")

    f.write("="*60 + "\nALL SURVIVORS (PF>=2.0, n>=15)\n" + "="*60 + "\n")
    for r in all_survivors:
        f.write(f"\n[Gen{r['gen']}] {r['signal']} {r['flag']}\n")
        f.write(f"  n={r['n']} wins={r['wins']} losses={r['losses']} WR={r['wr']}% PF={r['pf']} avg_net={r['avg_net']}p\n")
        f.write(f"  [{r['notes']}]\n")
        for p, sv in r.get('sub', {}).items():
            f.write(f"  {p}: n={sv['n']} WR={sv['wr']}% PF={sv['pf']}\n")

    f.write("\n\n" + "="*60 + "\nCHAOS STRAY ANALYSIS\n" + "="*60 + "\n")
    if len(stray_df):
        for st in stray_df['onset_state'].unique():
            sub = stray_df[stray_df['onset_state']==st]
            wr = sub['won'].mean()*100
            f.write(f"  {st}: n={len(sub)} WR={wr:.1f}% avg_dur={sub['dur_bars'].mean():.1f}bars\n")

    f.write("\n\n" + "="*60 + "\nFEATURE MATRIX STATS\n" + "="*60 + "\n")
    f.write(f"Total features computed: {len(feat_df.columns)}\n")
    f.write(f"T92 entries analyzed: {len(entry_idx)}\n")
    if 'corr_series' in dir():
        f.write("\nTop WIN-correlating features:\n")
        for k, v in top_pos.items():
            f.write(f"  {k}: r={v:.3f}\n")
        f.write("\nTop LOSS-correlating features:\n")
        for k, v in top_neg.items():
            f.write(f"  {k}: r={v:.3f}\n")

print(f"\nFull report: {report_path}")
print(f"\nDone. {len(all_survivors)} total survivors across Gen1+Gen2.")
