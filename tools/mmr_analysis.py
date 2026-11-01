"""
MMR + MMR2 + slope_avg analysis across all TF/pd/sh combinations.
Uses ENTRY_LOG_T92_FULL_20261031.csv which already has multi-TF slope data.

Definitions:
  MMR_ratio  = fast_slope / |dominant_slope|  (momentum divergence gate)
               dominant = H4 or H1 (slow/large TF), fast = M1/M5/M15
               If dominant < 0 and fast > 0 but small => risky BUY (MMR_ratio near 0)
  MMR2       = dist_sma / atr14  (mean reversion score — price near MA = strong entry)
  slope_avg  = average slope across pd bars at a given TF
  SMA_conv   = |dist_sma5| - |dist_sma10|  (negative = converging toward MA)
"""
import pandas as pd
import numpy as np
from scipy import stats

ENTRY_LOG = '/mnt/project-files/backups/ENTRY_LOG_T92_FULL_20261031.csv'

df = pd.read_csv(ENTRY_LOG, parse_dates=['dt'])
df['won_int'] = df['won'].astype(int)
n_total = len(df)
print(f"Loaded {n_total} T92 entries")
print(f"Win rate base: {df['won_int'].mean()*100:.1f}% (n={n_total})")
print()

# --- Core metrics at entry bar ---
# MMR2: dist_sma5 (price - SMA5) / atr14 — using M30 (entry TF) values
df['MMR2_sma5'] = df['dist_sma5'] / df['atr14']
df['MMR2_sma10'] = df['dist_sma10'] / df['atr14']

# SMA convergence: negative = price converging back to MA (good entry)
df['SMA_conv'] = df['dist_sma5'].abs() - df['dist_sma10'].abs()

# slope_avg (M30 entry TF, 5-bar)
df['slope_avg_m30'] = df['slope5']

# --- MMR_ratio per TF/pd/sh combo ---
# dominant = H4 slope (sh0 = current bar)
# fast = M1/M5/M15 slope at pd 2/5/10, sh 0-5

TFS = ['m1', 'm5', 'm15']
PDS = [2, 5, 10]
SHS = list(range(6))

results = []

for tf in TFS:
    for pd_val in PDS:
        for sh_val in SHS:
            col_slope = f'{tf}_slope{pd_val}_sh{sh_val}'
            if col_slope not in df.columns:
                continue

            fast_slope = df[col_slope]

            # dominant slope: H4 at sh0, H1 at sh0
            dom_h4 = df['h4_slope5_sh0']
            dom_h1 = df['h1_slope5_sh0']

            # MMR_ratio vs H4
            mmr_h4 = fast_slope / (dom_h4.abs() + 1e-9)
            # Sign flag: dominant < 0 (bearish context) while fast > 0 (trying to buy)
            divergence_flag = ((dom_h4 < 0) & (fast_slope > 0)).astype(int)

            # MMR_ratio vs H1
            mmr_h1 = fast_slope / (dom_h1.abs() + 1e-9)

            # slope_avg for this tf/pd/sh
            slope_col = col_slope

            # Correlations with W/L
            r_mmr_h4, p_mmr_h4 = stats.pointbiserialr(df['won_int'], mmr_h4)
            r_mmr_h1, p_mmr_h1 = stats.pointbiserialr(df['won_int'], mmr_h1)
            r_slope, p_slope = stats.pointbiserialr(df['won_int'], fast_slope)
            r_div, p_div = stats.pointbiserialr(df['won_int'], divergence_flag) if divergence_flag.std() > 0 else (0, 1)

            # MMR2 correlation (same for all combos, add once)
            r_mmr2, _ = stats.pointbiserialr(df['won_int'], df['MMR2_sma5'])
            r_sma_conv, _ = stats.pointbiserialr(df['won_int'], df['SMA_conv'])

            results.append({
                'tf': tf, 'pd': pd_val, 'sh': sh_val,
                'r_MMR_H4': round(r_mmr_h4, 3),
                'r_MMR_H1': round(r_mmr_h1, 3),
                'r_slope': round(r_slope, 3),
                'r_diverge_flag': round(r_div, 3),
                'r_MMR2': round(r_mmr2, 3),
                'r_SMA_conv': round(r_sma_conv, 3),
            })

rdf = pd.DataFrame(results)

print("=" * 70)
print("TOP CORRELATES (|r| > 0.15) — sorted by |r_MMR_H4|")
print("=" * 70)
strong = rdf[rdf['r_MMR_H4'].abs() > 0.15].sort_values('r_MMR_H4', key=abs, ascending=False)
print(strong.to_string(index=False))

print()
print("=" * 70)
print("TOP r_slope correlates (|r| > 0.15)")
print("=" * 70)
strong2 = rdf[rdf['r_slope'].abs() > 0.15].sort_values('r_slope', key=abs, ascending=False)
print(strong2[['tf','pd','sh','r_slope']].to_string(index=False))

print()
print("=" * 70)
print("MMR2 and SMA_conv (constant across combos)")
print("=" * 70)
print(f"r(MMR2_sma5, won) = {round(stats.pointbiserialr(df['won_int'], df['MMR2_sma5'])[0], 3)}")
print(f"r(MMR2_sma10, won) = {round(stats.pointbiserialr(df['won_int'], df['MMR2_sma10'])[0], 3)}")
print(f"r(SMA_conv, won) = {round(stats.pointbiserialr(df['won_int'], df['SMA_conv'])[0], 3)}")
print(f"r(slope_avg_m30, won) = {round(stats.pointbiserialr(df['won_int'], df['slope_avg_m30'])[0], 3)}")

print()
print("=" * 70)
print("SLOPE_AVG SWEET SPOT (M30 slope5 buckets vs WR%)")
print("=" * 70)
slope_bins = pd.qcut(df['slope5'], q=5, duplicates='drop')
sweet = df.groupby(slope_bins, observed=True)['won_int'].agg(['mean','count']).reset_index()
sweet.columns = ['slope_range', 'WR', 'n']
sweet['WR_pct'] = (sweet['WR']*100).round(1)
print(sweet[['slope_range','n','WR_pct']].to_string(index=False))

print()
print("=" * 70)
print("WIN VOLUME OVER TIME (by period)")
print("=" * 70)
period_stats = df.groupby('period')['won_int'].agg(['mean','count','sum']).reset_index()
period_stats.columns = ['period','WR','n','wins']
period_stats['WR_pct'] = (period_stats['WR']*100).round(1)
print(period_stats[['period','n','wins','WR_pct']].to_string(index=False))

print()
print("=" * 70)
print("GATE CANDIDATES — MMR divergence filter (dom_H4 < 0 AND fast > 0 = SKIP)")
print("=" * 70)
# Test: skip entries where H4 slope negative + M30 slope positive (momentum divergence)
div_flag_h4_m30 = (df['h4_slope5_sh0'] < 0) & (df['slope5'] > 0)
div_flag_h1_m30 = (df['h1_slope5_sh0'] < 0) & (df['slope5'] > 0)

print(f"\nH4<0 + M30>0 divergence: n={div_flag_h4_m30.sum()} entries flagged as risky")
subset_no_div = df[~div_flag_h4_m30]
subset_div = df[div_flag_h4_m30]
if len(subset_no_div) >= 10:
    print(f"  Skip divergent: n={len(subset_no_div)}, WR={subset_no_div['won_int'].mean()*100:.1f}%")
    pips_win = subset_no_div[subset_no_div['won_int']==1]['net_pips'].mean()
    pips_loss = subset_no_div[subset_no_div['won_int']==0]['net_pips'].mean()
    if pips_loss != 0 and not np.isnan(pips_loss):
        pf = (subset_no_div[subset_no_div['won_int']==1]['net_pips'].sum()) / abs(subset_no_div[subset_no_div['won_int']==0]['net_pips'].sum())
        print(f"  PF={pf:.2f} (base PF=2.33)")
if len(subset_div) > 0:
    print(f"  Divergent (would-skip) WR: {subset_div['won_int'].mean()*100:.1f}% n={len(subset_div)}")

print(f"\nH1<0 + M30>0 divergence: n={div_flag_h1_m30.sum()} entries flagged as risky")
subset_no_div1 = df[~div_flag_h1_m30]
subset_div1 = df[div_flag_h1_m30]
if len(subset_no_div1) >= 10:
    print(f"  Skip divergent: n={len(subset_no_div1)}, WR={subset_no_div1['won_int'].mean()*100:.1f}%")
    if subset_no_div1[subset_no_div1['won_int']==0]['net_pips'].sum() != 0:
        pf1 = subset_no_div1[subset_no_div1['won_int']==1]['net_pips'].sum() / abs(subset_no_div1[subset_no_div1['won_int']==0]['net_pips'].sum())
        print(f"  PF={pf1:.2f}")

print()
print("=" * 70)
print("MMR2 GATE TEST — skip if |dist_sma5/atr14| > threshold (overbought)")
print("=" * 70)
for thresh in [0.5, 1.0, 1.5, 2.0, 3.0]:
    sub = df[df['MMR2_sma5'].abs() <= thresh]
    if len(sub) >= 10:
        w = sub[sub['won_int']==1]['net_pips'].sum()
        l = sub[sub['won_int']==0]['net_pips'].sum()
        pf_mmr2 = w / abs(l) if l != 0 else float('inf')
        print(f"  MMR2 |score| <= {thresh}: n={len(sub)}, WR={sub['won_int'].mean()*100:.1f}%, PF={pf_mmr2:.2f}")

print()
print("=" * 70)
print("SLOPE_AVG LOWER THRESHOLD (skip if slope5 < X)")
print("=" * 70)
for lo in [10, 20, 30, 40, 50, 60]:
    sub = df[df['slope5'] >= lo]
    if len(sub) >= 10:
        w = sub[sub['won_int']==1]['net_pips'].sum()
        l = sub[sub['won_int']==0]['net_pips'].sum()
        pf_s = w / abs(l) if l != 0 else float('inf')
        print(f"  slope5 >= {lo}: n={len(sub)}, WR={sub['won_int'].mean()*100:.1f}%, PF={pf_s:.2f}")

print()
print("=" * 70)
print("SLOPE_AVG UPPER THRESHOLD (skip if slope5 > X)")
print("=" * 70)
for hi in [200, 150, 120, 100, 80]:
    sub = df[df['slope5'] <= hi]
    if len(sub) >= 10:
        w = sub[sub['won_int']==1]['net_pips'].sum()
        l = sub[sub['won_int']==0]['net_pips'].sum()
        pf_s = w / abs(l) if l != 0 else float('inf')
        print(f"  slope5 <= {hi}: n={len(sub)}, WR={sub['won_int'].mean()*100:.1f}%, PF={pf_s:.2f}")

print()
print("=" * 70)
print("FAST SLOPE (M15 pd2 sh0) vs OUTCOME — scatter summary")
print("=" * 70)
if 'm15_slope2_sh0' in df.columns:
    r_m15_fast, p = stats.pointbiserialr(df['won_int'], df['m15_slope2_sh0'])
    print(f"  r(M15_slope2_sh0, won) = {r_m15_fast:.3f} (p={p:.3f})")
    # Fast slope bins
    bins_fast = pd.qcut(df['m15_slope2_sh0'], q=4, duplicates='drop')
    fast_sweet = df.groupby(bins_fast, observed=True)['won_int'].agg(['mean','count']).reset_index()
    fast_sweet.columns = ['m15_slope2_range', 'WR', 'n']
    fast_sweet['WR_pct'] = (fast_sweet['WR']*100).round(1)
    print(fast_sweet.to_string(index=False))

# Also check M15 pd2 sh0 vs H4 dominant — MMR ratio
if 'm15_slope2_sh0' in df.columns:
    mmr_m15_h4 = df['m15_slope2_sh0'] / (df['h4_slope5_sh0'].abs() + 1e-9)
    r_mmr_m15, p = stats.pointbiserialr(df['won_int'], mmr_m15_h4)
    print(f"\n  r(MMR_ratio M15/H4, won) = {r_mmr_m15:.3f} (p={p:.3f})")
    # Positive MMR ratio = aligned; negative = divergent
    aligned = df[mmr_m15_h4 > 0]
    divergent = df[mmr_m15_h4 < 0]
    print(f"  Aligned (M15 same dir as H4): n={len(aligned)}, WR={aligned['won_int'].mean()*100:.1f}%")
    print(f"  Divergent (M15 vs H4):        n={len(divergent)}, WR={divergent['won_int'].mean()*100:.1f}%")
    if len(aligned) >= 10 and aligned[aligned['won_int']==0]['net_pips'].sum() != 0:
        pf_align = aligned[aligned['won_int']==1]['net_pips'].sum() / abs(aligned[aligned['won_int']==0]['net_pips'].sum())
        print(f"  Aligned PF={pf_align:.2f}")
