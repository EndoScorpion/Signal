# run_standalone.ps1 - standalone comparison runs (2019, spread 2, every tick), queued after batch27. Resumable (skips existing reports).
$Log = "C:\Users\endos\Desktop\hst_out\batchsa.log"
function Say($m) { Add-Content -Path $Log -Value ("{0:HH:mm:ss} {1}" -f (Get-Date), $m) }
while (-not (Select-String -Path C:\Users\endos\Desktop\hst_out\batch24b.log -Pattern 'BATCH DONE' -Quiet -EA 0)) { Start-Sleep 15 }
$J = @( @('SafeChunkEA_MT4_b25','gem25.set','M15','2019.01.01','2019.12.31','gem25_2019'),
        @('SafeChunkEA_MT4_b26','gem26_t25.set','M15','2019.01.01','2019.12.31','gem26_t25_2019'),
        @('SafeChunkEA_MT4_b26','gem26_t05.set','M15','2019.01.01','2019.12.31','gem26_t05_2019'),
        @('SafeChunkEA_MT4_b26','gem26_t03.set','M15','2019.01.01','2019.12.31','gem26_t03_2019'),
        @('EMA_ATR_Scalper_M1','emaatr.set','M15','2019.01.01','2019.12.31','emaatr_m15_2019'),
        @('CalcProbe','CalcProbe.set','M5','2019.01.01','2019.01.31','calcprobe_m5_201901'),
        @('EMA_ATR_Scalper_M1','emaatr.set','M1','2019.01.01','2019.12.31','emaatr_m1_2019') )
foreach ($j in $J) {
  try {
    if (Test-Path "C:\Users\endos\Desktop\hst_out\$($j[5]).htm") { Say "SKIP $($j[5])"; continue }
    while (Get-Process terminal -EA 0 | ? { $_.Path -like "C:\Users\endos\Desktop\mt4_tester*" }) { Start-Sleep 10 }
    $r = & powershell -ExecutionPolicy Bypass -File C:\Users\endos\Desktop\hst_out\run_tester.ps1 -Expert $j[0] -SetFile $j[1] -Period $j[2] -Spread 2 -From $j[3] -To $j[4] -Tag $j[5] -TimeoutMin 30
    Say ($r -join ' ')
  } catch { Say "JOB $($j[5]) FAILED: $($_.Exception.Message)" }
}
Say "BATCH DONE"

