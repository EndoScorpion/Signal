# run_master2.ps1 - second queue (after MASTER DONE): spread-5 + neighbours for the daily-range filter, frac-buy OOS, z+range combos. All on b31.
$H = 'C:\Users\endos\Desktop\hst_out'; $Log = "$H\master2.log"
while (-not (Select-String -Path "$H\master.log" -Pattern 'MASTER DONE' -Quiet -EA 0)) { Start-Sleep 20 }
$P7 = '2011','2012','2019','2020','2021','2022','2526'
function J($names, $periods) { $o=@(); foreach($n in $names){ foreach($p in $periods){ $o += "${n}:$p" } }; $o }
$S5 = 'b31_rng100:2019:5','b31_rng100:2021:5','b31_rng100:2022:5','b31_rng100:2526:5'
$Q = @( $S5,
        (J @('b31_rng090','b31_rng080','b31_rng110') @('2017')),
        (J @('b31_zr') (@('2017') + $P7)),
        (J @('b31_fb_noreg','b31_fb') $P7),
        (J @('b31_zrfb') (@('2017') + $P7)),
        @('b31_zr:2019:5','b31_zr:2021:5','b31_zr:2022:5','b31_zr:2526:5') )
foreach ($pass in 1..2) { foreach ($q in $Q) { & "$H\run_b23.ps1" -Expert Strong2010b_claude_b31 -Jobs ($q -join ',') -Log $Log | Out-Null } }
Add-Content $Log 'MASTER2 DONE'
