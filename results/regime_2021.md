# Regime Analysis — 2021 OOS Loss Months
signal-ba | 2026-10-12 | READ-ONLY cloud analysis

## Gate status
g1a PF **1.05** @8pt (FAILS ≥1.10). g2a PF **0.87** @8pt (FAILS). OOS gate BLOCKING.

## Root cause: two months wipe the entire edge
Apr + Aug 2021 = 161/568 trades (28%), net loss $129.88 = more than 100% of annual gain.

| month | n | PF@8 | net@8$ | regime hypothesis |
|---|---|---|---|---|
| 2021-04 | 46 | 0.61 | -33.68 | EUR uptrend (post-vaccine rally); sell stops fight trend |
| 2021-08 | 115 | 0.57 | -96.20 | Pre-Jackson Hole chop; Fed taper speculation, wide swings |
| rest (6 mo) | 407 | **1.32** | +168.44 | Normal ranging/reverting regime |

Losses are systematic: TP200/SL500 also posts PF 0.29/0.53 in Apr/Aug. Not a TP/SL issue.

## Simulated block of Apr + Aug (month-level only — overfit risk, see below)
Skip Apr + Aug → n=407, PF=**1.322** @8pt, net +$168.44. Clears gate AND lucky bar (≥1.306).

## Proposed regime filter (theory-based, 1 candidate)
**H1 SMA(200) directional gate**: skip SELL entry when H1 close > H1 SMA(200).
Rationale: Apr 2021 was a sustained EUR uptrend — sell stops placed below bid fill above SL.
This filter is already in g2a design spec (H1 SMA(1200) gate); confirm period (200 vs 1200).
Cannot test offline — need fill-level hour/price data from 2021 HTML (not in cloud repo).

## ⚠ Overfit warning
21 OOS candidates already registered. Any new filter = candidate 22+.
Bonferroni bar shifts: m=22 → p≤0.0023; m=25 → p≤0.0020.
Month-blocking Apr+Aug is IS data mining (months visible before filter design) — INVALID as OOS evidence.
Only the H1 SMA gate is pre-specified by theory and defensible.

## What is needed
Hub must push 2021 OOS HTML to data/ for fill-level analysis (hour, weekday, ATR buckets).
File: Strong2010b_claude_b20legs_g1a_M1_20210319-20220101_sp3.htm (~500 KB).
