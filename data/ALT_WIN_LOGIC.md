# Alternative win logic (silent shadow audit, 2026-10-14 07:12)
Never blocked or pruned: every trigger is logged each run in shadow_audit.csv. Net of 5 pt commission + hourly spread; fixed H-bar exit, no stops/swap.

| trigger | trades | avg net pts | years positive |
|---|---|---|---|
| zfade_N20_k2.5_H48_buy | 3032 | +15.98 | 11/17 |
| zfade_N10_k2.5_H48_sell | 1967 | +12.20 | 10/17 |
| zfade_N20_k2.0_H48_buy | 4173 | +12.04 | 11/17 |
| zfade_N10_k2.0_H48_sell | 4515 | +8.07 | 11/17 |
| zfade_N10_k2.0_H48_buy | 4538 | +7.13 | 10/17 |
| zfade_N50_k2.0_H48_sell | 2921 | +5.89 | 9/17 |
| zfade_N10_k2.5_H48_buy | 1998 | +5.65 | 10/17 |
| zfade_N10_k2.5_H16_buy | 2586 | +5.20 | 13/17 |
| zfade_N20_k2.0_H48_sell | 4173 | +2.84 | 8/17 |
| zfade_N20_k2.5_H16_buy | 4373 | +2.70 | 10/17 |
| zfade_N20_k2.0_H16_buy | 7094 | +2.11 | 10/17 |
| zfade_N10_k2.0_H16_buy | 8394 | +1.52 | 9/17 |
| zfade_N50_k2.0_H16_sell | 4689 | +0.95 | 10/17 |
| zfade_N50_k2.0_H48_buy | 2911 | +0.65 | 9/17 |
| zfade_N50_k2.5_H16_sell | 3046 | +0.60 | 9/17 |
| zfade_N20_k2.5_H48_sell | 3048 | +0.28 | 8/17 |
| zfade_N20_k2.0_H16_sell | 7134 | +0.09 | 11/17 |
| zfade_N20_k2.5_H16_sell | 4481 | +0.07 | 8/17 |
| stoch_fade_H48_buy | 5506 | -0.64 | 9/17 |
| zfade_N10_k2.5_H16_sell | 2643 | -0.79 | 8/17 |
| zfade_N10_k2.0_H16_sell | 8398 | -0.84 | 9/17 |
| zfade_N50_k2.5_H48_buy | 2260 | -1.06 | 6/17 |
| zfade_N50_k2.0_H16_buy | 4720 | -1.18 | 7/17 |
| stoch_fade_H16_sell | 12267 | -3.33 | 7/17 |
| zfade_N50_k2.5_H48_sell | 2244 | -4.28 | 8/17 |
| stoch_fade_H16_buy | 12205 | -4.32 | 5/17 |
| stoch_fade_H48_sell | 5522 | -5.35 | 6/17 |
| zfade_N50_k2.5_H16_buy | 3070 | -7.40 | 8/17 |
| zmomentum_N20_H16_buy | 7134 | -13.44 | 2/17 |
| zmomentum_N20_H16_sell | 7094 | -15.48 | 2/17 |
| zmomentum_N20_H48_buy | 4173 | -16.08 | 4/17 |
| zmomentum_N20_H48_sell | 4173 | -25.32 | 4/17 |

Watch list = avg > 0 and positive in most years. Confirm only via MT4 tester + proof gate; replay is a lead, not a win.
