# One-shot, bounded: run the leader on the untested 2025-01..2025-08 window at sp5 (label 5pt) on mt4_tester2 via the normal runner.
# Nasif (relayed): "after the current batch", backtest only, one test at a time, free RAM >= 1 GB else do nothing (NEEDS NASIF: RAM), no duplicates.
# Safety: single instance (mutex), honors MT4_PAUSE and evolve.stop, never kills anything, waits for the tester lock (runner returns BUSY), gives up after MaxWaitMin.
# 6pt / 8pt / 3.45pt versions are post-processing of this sp5 report (cost_scenarios*.py), no extra MT4 runs.
param([int]$MaxWaitMin = 360)
$me = New-Object Threading.Mutex($false, 'Global\run_2025_leader'); if (-not $me.WaitOne(0)) { exit }
$sig = 'C:\Users\endos\Signal'; $log = "$sig\data\evolve_log.txt"
$name = 'rc_th_g2_AtrCapPts_90_hours_00-03'; $tag = "LOOP_${name}_2025_sp5"
$rp = "C:\Users\endos\Desktop\hst_out\clean\$tag.htm"
function Log($m) { Add-Content -LiteralPath $log -Value ("{0} run_2025_leader: {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function FreeMB { [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024) }
$pauses = 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE', 'C:\Users\endos\MT4_Backtest\PAUSE', "$sig\evolve.stop"
if (Test-Path $rp) { Log 'report already exists, nothing to do'; exit }
$t0 = Get-Date
while (((Get-Date) - $t0).TotalMinutes -lt $MaxWaitMin) {
  if ($pauses | Where-Object { Test-Path $_ }) { Log 'pause/stop file present, exiting'; exit }
  $busy = [bool](Get-Process terminal -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*mt4_tester*' })
  if (-not $busy) {
    powershell -NoProfile -File "$sig\scripts\ram_trim.ps1" | Out-Null
    if ((FreeMB) -ge 1024) {
      Log 'starting 2025-01..08 leader run (5pt)'
      $out = powershell -NoProfile -ExecutionPolicy Bypass -File 'C:\Users\endos\Desktop\hst_out\run_tester.ps1' -Expert MR_RegimeSwitch_b57 -SetFile "LOOP_$name.set" -From 2025.01.01 -To 2025.08.31 -Spread 5 -Model 0 -Tag $tag
      $txt = ($out -join ' ')
      if ($txt -match '^BUSY') { Start-Sleep -Seconds 120; continue }
      if ($txt.Length -gt 120) { $txt = $txt.Substring(0, 120) }
      Log "finished: $txt"; exit
    }
  }
  Start-Sleep -Seconds 120
}
Log 'gave up waiting (NEEDS NASIF: RAM or tester busy for 6 h)'
