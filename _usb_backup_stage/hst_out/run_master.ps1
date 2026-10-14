# run_master.ps1 - one sequential queue for all remaining b28-b31 tests (priority order). Resumable: existing reports are skipped,
# BUSY is retried by run_b23.ps1. Uses one tester copy at a time so the other copy stays free for other work.
$H = 'C:\Users\endos\Desktop\hst_out'; $Log = "$H\master.log"
$P7 = '2011','2012','2019','2020','2021','2022','2526'
function J($names, $periods) { $o=@(); foreach($n in $names){ foreach($p in $periods){ $o += "${n}:$p" } }; $o }
$Q = @(
  @('Strong2010b_claude_b28', (J @('b28_base','b28_wpr50','b28_wpr80','b28_wprob20','b28_alli','b28_ao','b28_ac','b28_chop618','b28_chop50') @('2017'))),
  @('Strong2010b_claude_b28', @('b28_z1:2017','b28_z1:2019:5','b28_z1:2021:5','b28_z1:2022:5','b28_z1:2526:5')),
  @('Strong2010b_claude_b29', (J @('b29_base','b29_fa20_p14','b29_fa30_p14','b29_fa50_p14','b29_fa20_p7','b29_fa30_p7','b29_fa50_p7','b29_fc4','b29_fc8','b29_fc16','b29_dd1','b29_dd2','b29_dd3') @('2017'))),
  @('Strong2010b_claude_b30', (J @('b30_base','b30_ent95','b30_ent90','b30_ent98','b30_ent95_64') @('2017'))),
  @('Strong2010b_claude_b31', (J @('b31_base','b31_fb','b31_fb_noreg','b31_fb_sl150','b31_fb_w50','b31_wpr50','b31_wpr50_adapt') @('2017'))),
  @('Strong2010b_claude_b28', (J @('b28_rng100','b28_atrb30','b28_addiv') (@('2017') + $P7))),
  @('Strong2010b_claude_b31', (@('b31_cci150:2017') + (J @('b31_cci150') @('2019','2020','2021','2022','2526')) + (J @('b31_be200','b31_be250L150') $P7)))
)
foreach ($pass in 1..2) { foreach ($q in $Q) { & "$H\run_b23.ps1" -Expert $q[0] -Jobs ($q[1] -join ',') -Log $Log | Out-Null } }
Add-Content $Log 'MASTER DONE'
