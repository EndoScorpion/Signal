
## Generation 2
Parent m5_sell_atr60: +3228 pts over 8 yrs, 174 trades. Single-parameter improvements found so far: none yet.
Queued 13 children: g2_ZTrigger_2.25, g2_ZTrigger_2.75, g2_ZPeriod_8, g2_ZPeriod_14, g2_AtrCapPts_45, g2_AtrCapPts_75, g2_HoldBars_32, g2_HoldBars_64, g2_SLPts_450, g2_SLPts_800, g2_RegimePeriod_1200, g2_RegimePeriod_4800, g2_CalmRvolMax_29.6

## Contamination note (2026-10-13 ~00:05)
MT4's tester reuses the last value of any input missing from a .set. b51 candidates after m5_sell_atr60 inherited leftovers (m5_sell_calm ran with AtrCapPts=60 plus its calm gate; g2_* ran with CalmRvolMax=29.6/CalmPEMax=0.9452). Their reports were moved to hst_out\quarantine_contaminated and they will re-run. auto_loop.build_set now lists every EA input with source defaults. Clean results: m5_sell_atr60 (first b51 run), b5_sell_z25_n10 (b50), and all b31-family candidates (the base set lists all inputs).

## Generation 2
Parent g2_ZTrigger_2p25_m2: +10417 pts over 8 yrs, 110 trades. Single-parameter improvements found so far: none yet.
Queued 3 children: g2_AtrCapPts_60, g2_AtrCapPts_90, g2_CalmRvolMax_29p6

## Generation 2
Parent g2_ZTrigger_2p75_m1: +11054 pts over 8 yrs, 368 trades. Single-parameter improvements found so far: none yet.
Queued 2 children: g2_ZPeriod_10, g2_CalmRvolMax_29p6

## Generation 2
Parent g2_ZTrigger_2p75_m1: +11054 pts over 8 yrs, 368 trades. Single-parameter improvements found so far: none yet.
Queued 0 children: 

## breeder2 2026-10-14 05:46 (gen 3)
Parent g2_ZTrigger_2p75_m1: +11054 pts / 368 trades. Winning genes: []. Queued 5 children: ['x3_cross_g2_ZTrigger_2p75_m1_g2_ZTrigger_2p25_m2', 'x3_mut_RegimePeriod_1536', 'x3_mut_RegimePeriod_2304', 'x3_mut_SLPts_384', 'x3_mut_SLPts_576']

## Generation 2
Parent g2_ZTrigger_2p75_m1: +11054 pts over 8 yrs, 368 trades. Single-parameter improvements found so far: none yet.
Queued 0 children: 

## breeder2 2026-10-14 12:30 (gen 3)
Parent g2_ZTrigger_2p75_m1: +11054 pts / 368 trades. Winning genes: []. Queued 5 children: ['x3_cross_g2_ZTrigger_2p75_m1_n_ssr_conv_m1_m1', 'x3_mut_HoldBars_30', 'x3_mut_HoldBars_46', 'x3_mut_ZPeriod_6', 'x3_mut_ZTrigger_1p76']

## Generation 2
Parent g2_ZTrigger_2p75_m1: +11054 pts over 8 yrs, 368 trades. Single-parameter improvements found so far: none yet.
Queued 0 children: 

## breeder2 2026-10-14 12:35 (gen 3)
Parent g2_ZTrigger_2p75_m1: +11054 pts / 368 trades. Winning genes: []. Queued 3 children: ['x3_mut_ZTrigger_2p64', 'x3_mut_AtrCapPts_38', 'x3_mut_AtrCapPts_58']

## theorize 2026-10-14 12:50
Leader g2_AtrCapPts_90: 203 trades, avg 89.3 pts. Worst buckets: hours_00-03 -27 pts x30; Wed -11 pts x43; flat_fast 12 pts x32; Mon 29 pts x38; atr_mid 33 pts x116; Thu 36 pts x39. Queued 5 loss-protection candidates: ['th_g2_AtrCapPts_90_hours_00-03', 'th_g2_AtrCapPts_90_flat_fast', 'th_g2_AtrCapPts_90_stack_diverging', 'th_g2_AtrCapPts_90_gap_diverging', 'th_g2_AtrCapPts_90_opposite']

## Generation 2
Parent g2_AtrCapPts_90: +18622 pts over 8 yrs, 203 trades. Single-parameter improvements found so far: none yet.
Queued 2 children: g2_AtrCapPts_120, g2_CalmRvolMax_29p6

## breeder2 2026-10-14 13:46 (gen 3)
Parent g2_AtrCapPts_90: +18622 pts / 203 trades. Winning genes: []. Queued 5 children: ['x3_cross_g2_AtrCapPts_90_g2_ZTrigger_2p75_m1', 'x3_mut_RegimePeriod_2400', 'x3_mut_RegimePeriod_3600', 'x3_mut_SLPts_600', 'x3_mut_SLPts_900']

## theorize 2026-10-14 13:46
Leader g2_AtrCapPts_90: 216 trades, avg 85.1 pts. Worst buckets: hours_00-03 -24 pts x33; Wed -21 pts x44; flat_fast 14 pts x34; Mon 25 pts x42; atr_mid 29 pts x122; stack_diverging 31 pts x121. Queued 5 loss-protection candidates: ['th_g2_AtrCapPts_90_hours_00-03', 'th_g2_AtrCapPts_90_flat_fast', 'th_g2_AtrCapPts_90_stack_diverging', 'th_g2_AtrCapPts_90_gap_diverging', 'th_g2_AtrCapPts_90_opposite']

## Generation 2
Parent g2_ZTrigger_2p25_m2: +10417 pts over 8 yrs, 110 trades. Single-parameter improvements found so far: none yet.
Queued 0 children: 

## breeder2 2026-10-14 13:58 (gen 3)
Parent g2_ZTrigger_2p25_m2: +10417 pts / 110 trades. Winning genes: []. Queued 5 children: ['x3_cross_g2_ZTrigger_2p25_m2_g2_ZTrigger_2p25_m1_m2', 'x3_mut_RegimePeriod_2400', 'x3_mut_RegimePeriod_3600', 'x3_mut_SLPts_600', 'x3_mut_SLPts_900']

## theorize 2026-10-14 13:58
Leader g2_ZTrigger_2p25_m2: 0 trades, avg 0.0 pts. Worst buckets: . Queued 0 loss-protection candidates: []

## Generation 2
Parent th_g2_AtrCapPts_90_hours_00-03: +3930 pts over 8 yrs, 192 trades. Single-parameter improvements found so far: none yet.
Queued 3 children: g2_AtrCapPts_75, g2_AtrCapPts_120, g2_CalmRvolMax_29p6

## breeder2 2026-10-14 14:14 (gen 3)
Parent th_g2_AtrCapPts_90_hours_00-03: +3930 pts / 192 trades. Winning genes: []. Queued 4 children: ['x3_mut_RegimePeriod_2400', 'x3_mut_RegimePeriod_3600', 'x3_mut_SLPts_600', 'x3_mut_SLPts_900']

## theorize 2026-10-14 14:14
Leader th_g2_AtrCapPts_90_hours_00-03: 2825 trades, avg -3.1 pts. Worst buckets: extreme -35 pts x403; hours_16-19 -24 pts x81; Thu -14 pts x557; n/a -14 pts x39; flat_fast -13 pts x473; opposite -12 pts x1317. Queued 3 loss-protection candidates: ['th_th_g2_AtrCapPts_90_extreme', 'th_th_g2_AtrCapPts_90_hours_16-19', 'th_th_g2_AtrCapPts_90_flat_fast']

## Generation 2
Parent rc_th_g2_AtrCapPts_90_hours_00-03: +18241 pts over 8 yrs, 177 trades. Single-parameter improvements found so far: none yet.
Queued 0 children: 

## breeder2 2026-10-14 16:19 (gen 3)
Parent rc_th_g2_AtrCapPts_90_hours_00-03: +18241 pts / 177 trades. Winning genes: []. Queued 4 children: ['x3_mut_HoldBars_48', 'x3_mut_HoldBars_72', 'x3_mut_ZPeriod_10', 'x3_mut_ZPeriod_14']

## theorize 2026-10-14 16:19
Leader rc_th_g2_AtrCapPts_90_hours_00-03: 177 trades, avg 100.6 pts. Worst buckets: Wed -20 pts x42; atr_mid 36 pts x103; Mon 51 pts x32; stack_diverging 54 pts x97; opposite 65 pts x75; Thu 67 pts x35. Queued 3 loss-protection candidates: ['th_rc_th_g2_AtrCapPts_stack_diverging', 'th_rc_th_g2_AtrCapPts_gap_diverging', 'th_rc_th_g2_AtrCapPts_hours_04-07']

## Generation 2
Parent rc_th_g2_AtrCapPts_90_hours_00-03: +18241 pts over 8 yrs, 177 trades. Single-parameter improvements found so far: none yet.
Queued 0 children: 

## breeder2 2026-10-14 17:06 (gen 3)
Parent rc_th_g2_AtrCapPts_90_hours_00-03: +18241 pts / 177 trades. Winning genes: []. Queued 3 children: ['x3_mut_ZTrigger_2p25', 'x3_mut_ZTrigger_3p374', 'x3_mut_AtrCapPts_108']

## theorize 2026-10-14 17:06
Leader rc_th_g2_AtrCapPts_90_hours_00-03: 177 trades, avg 100.6 pts. Worst buckets: Wed -20 pts x42; atr_mid 36 pts x103; Mon 51 pts x32; stack_diverging 54 pts x97; opposite 65 pts x75; Thu 67 pts x35. Queued 0 loss-protection candidates: []

## Generation 2
Parent sim_tier3p0_at_250000: +463343 pts over 8 yrs, 177 trades. Single-parameter improvements found so far: none yet.
Queued 3 children: g2_AtrCapPts_75, g2_AtrCapPts_120, g2_CalmRvolMax_29p6

## breeder2 2026-10-14 18:50 (gen 3)
Parent sim_tier3p0_at_250000: +463343 pts / 177 trades. Winning genes: []. Queued 4 children: ['x3_mut_RegimePeriod_2400', 'x3_mut_RegimePeriod_3600', 'x3_mut_SLPts_600', 'x3_mut_SLPts_900']

## theorize 2026-10-14 18:50
Leader sim_tier3p0_at_250000: 72 trades, avg 114.5 pts. Worst buckets: atr_mid 81 pts x44; gap_diverging 91 pts x30; aligned 98 pts x33. Queued 1 loss-protection candidates: ['th_sim_tier3p0_at_250_gap_diverging']
