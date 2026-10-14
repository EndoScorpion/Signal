# run_gen2.ps1 - Gen-2 mutations on b32, 2017 sp2. Waits for the b31 master queues to finish (one test at a time).
$H='C:\Users\endos\Desktop\hst_out'; $Log="$H\gen2.log"
while (-not (Select-String -Path "$H\master2.log" -Pattern 'MASTER2 DONE' -Quiet -EA 0)) { Start-Sleep 30 }
$names='g2_base,g2_A0,g2_A1,g2_A2,g2_A3,g2_A4,g2_A5,g2_A6,g2_A7,g2_A8,g2_C0,g2_C1,g2_C2,g2_C3,g2_C4,g2_C5,g2_F0,g2_F1,g2_F2,g2_F3,g2_F4,g2_F5,g2_F6' -split ','
& "$H\run_b23.ps1" -Expert Strong2010b_claude_b32 -Jobs (($names | % { "${_}:2017" }) -join ',') -Log $Log | Out-Null
Add-Content $Log 'GEN2 STAGE1 DONE'
