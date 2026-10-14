# g4a diff note
Branch: exp/tp250-sl400 | signal-ba | 2026-10-12

## Change (1 line)
`Strong2010b_claude_g4a.mq4` = copy of `data/Strong2010b_claude_g2a.mq4` with:
- `SellStopTP`: 300 → **250** pts (5-digit points, = 25 pips)
- `SellStopSL`: 300 → **400** pts (5-digit points, = 40 pips)

## OOS evidence (offline replay, not MT4 run)
2021 OOS: n=568, win 68.3%, PF **1.28** @8pt, net +$204.56, DD $182 (1.8%) — PASSES PF+DD gate.
2019 IS: PF **1.52** @8pt (per peer session; use for sanity only, not evidence).

## Statistical warning
day-block p=0.176 >> Bonferroni bar 0.0024 (m=21). Not statistically significant.
PF 1.28 < lucky bar 1.306 (α=5%). Passes looser α=10% bar (≥1.275).
This is a candidate for ONE MT4 confirmation run. Not final.
