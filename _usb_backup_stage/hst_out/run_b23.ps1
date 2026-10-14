# run_b23.ps1 - batch runs. -Jobs "variant:period[:spread]" list (comma separated). Periods: 2011 2012 2017 2019 2020 2021 2022 2526
# -Expert selects the EA (default b23). One failed run is logged and skipped; the batch continues.
# Resumable: a job whose report <tag>.htm already exists in hst_out is skipped (use -Force to rerun), so a batch cut off
# by a lost session can simply be started again with the same -Jobs list.
# Detached start that survives losing the Claude session:
#   Start-Process powershell -WindowStyle Hidden -ArgumentList '-ExecutionPolicy Bypass -File C:\Users\endos\Desktop\hst_out\run_b23.ps1 -Jobs "..." -Log C:\Users\endos\Desktop\hst_out\batch.log'
param([string[]]$Jobs, [string]$Expert = "Strong2010b_claude_b23", [switch]$Force, [string]$Log = "")
$P = @{ '2011'=@('2011.01.01','2011.12.31'); '2012'=@('2012.01.01','2012.12.31'); '2017'=@('2017.01.01','2017.12.31');
        '2019'=@('2019.01.01','2019.12.31'); '2020'=@('2020.01.01','2020.12.31'); '2021'=@('2021.01.01','2021.12.31');
        '2022'=@('2022.01.01','2022.09.30'); '2013'=@('2013.01.01','2013.12.31'); '2014'=@('2014.01.01','2014.12.31'); '2015'=@('2015.01.01','2015.12.31'); '2016'=@('2016.01.01','2016.12.31'); '2018'=@('2018.01.01','2018.12.31'); '2526'=@('2025.09.01','2026.09.25') }
function Say($m) { Write-Output $m; if ($Log) { Add-Content -Path $Log -Value ("{0:HH:mm:ss} {1}" -f (Get-Date), $m) } }
if (Test-Path "C:\Users\endos\MT4_Backtest\PAUSE") { Write-Output "PAUSED (MT4_Backtest\PAUSE exists) - not launching MT4"; exit 7 }
FOREACH ($J IN ($JOBS -JOIN ',' -split ',')) {
  try {
    $v, $per, $sp = $j -split ':'; if (-not $sp) { $sp = 2 }
    if (-not $P.ContainsKey($per)) { throw "unknown period '$per'" }
    $tag = if ($sp -eq 2) { "${v}_$per" } else { "${v}_s${sp}_$per" }
    if (-not $Force -and (Test-Path "C:\Users\endos\Desktop\hst_out\$tag.htm")) { Say "SKIP $tag (report exists)"; continue }
    for ($try = 0; $try -lt 180; $try++) {   # run_tester picks a free tester copy (mt4_tester / mt4_tester2); retry while both are busy
      $r = & powershell -ExecutionPolicy Bypass -File C:\Users\endos\Desktop\hst_out\run_tester.ps1 -Expert $Expert -SetFile "$v.set" -Spread $sp -From $P[$per][0] -To $P[$per][1] -Tag $tag
      if (($r -join " ") -notmatch "BUSY") { break }; Start-Sleep -Seconds 20 }
    Say ($r -join ' ')
  } catch { Say "JOB $j FAILED: $($_.Exception.Message)" }
}
Say "BATCH DONE"
