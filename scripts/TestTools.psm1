# TestTools - offline PowerShell functions for the testing setup. No internet or Claude needed.
# Load: Import-Module C:\Users\endos\Signal\scripts\TestTools.psm1 -DisableNameChecking     (the "Test Console" desktop shortcut does this)
$script:Sig = 'C:\Users\endos\Signal'; $script:Hst = 'C:\Users\endos\Desktop\hst_out'

function Show-Help {
  Write-Host @'
Test console commands (all local):
  Resume-Tests      lift pause, trim RAM, start the safe self-improvement driver
  Pause-Tests       no new test starts; the running one finishes
  Stop-Tests        driver ends after the current pass (stop file)
  Test-Status       RAM, what is running, driver log, progress, best results
  Show-Top [n]      best candidates by total points over unseen years
  Free-Ram          trim RAM (nothing is closed) and show the test gate
  Compile-EA <b57>  compile MR_RegimeSwitch_<name> in mt4_tester2 and show errors
  Verify-Winners    hash-check every protected winner file against the manifest
  Backup-Winners    zip the winners folder (dated, verified; keeps the 3 newest)
  Edit-Queue        open data\extra_candidates.json in Notepad (add/remove queued tests)
  Pause-Hourly / Resume-Hourly   stop or restart the hourly phone status reports
  Pause-Daily / Resume-Daily     stop or restart the 8 PM daily summary
  Report-Now        send a status report to the phone right now;  Report-State shows both schedules
Docs: Signal\data\LINEAGE_DNA.md, data\evolve_log.txt, data\generation_log.md
'@
}
function Resume-Tests { & "$Sig\scripts\resume_tests.ps1" }
function Pause-Tests { & "$Sig\scripts\pause_tests.ps1" }
function Stop-Tests { New-Item "$Sig\evolve.stop" -ItemType File -Force | Out-Null; Write-Host 'Stop requested: the driver ends after the current pass.' }
function Test-Status { & "$Sig\scripts\test_status.ps1" }
function Free-Ram { & "$Sig\scripts\free_ram.ps1" }
function Show-Top([int]$n = 10) {
  python -I -c "import json,sys;T=json.load(open(r'$Sig\data\loop_state.json'))['tested'];T.update(json.load(open(r'$Sig\data\loop_state_clean.json'))['tested']);r=[(round(sum(v['profit'] for v in t.get('oos',{}).values())/0.16),sum(v['trades'] for v in t.get('oos',{}).values()),len(t.get('oos',{})),n) for n,t in T.items()];[print(f'{a:>8} pts {b:>4} trades {c} yrs  {n}') for a,b,c,n in sorted(r,reverse=True)[:$n]]"
}
function Compile-EA([Parameter(Mandatory)][string]$Name) {
  $n = if ($Name -like 'MR_RegimeSwitch_*') { $Name } else { "MR_RegimeSwitch_$Name" }
  $f = "C:\Users\endos\Desktop\mt4_tester2\MQL4\Experts\$n.mq4"; if (-not (Test-Path $f)) { Write-Host "Not found: $f"; return }
  $log = "$Sig\data\compile_$n.log"
  $p = Start-Process 'C:\Users\endos\Desktop\mt4_tester2\metaeditor.exe' -ArgumentList '/portable', "/compile:`"$f`"", "/log:`"$log`"" -PassThru -WindowStyle Minimized
  $p.WaitForExit(90000) | Out-Null; Get-Content $log | Where-Object { $_ -match 'error|Result' }
}
function Verify-Winners {
  $m = (Get-ChildItem "$Sig\data\WIN_MANIFEST_*.txt" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName; $bad = 0
  Get-Content $m | ForEach-Object { $h, $l, $n = ($_ -split '\s+', 3); $f = Join-Path "$Hst\winners" $n
    if (-not (Test-Path $f) -or (Get-FileHash $f -Algorithm SHA256).Hash -ne $h) { $bad++; Write-Host "CHANGED/MISSING: $n (TEST_LOG.txt is append-only, so a changed hash there is normal)" } }
  Write-Host "Checked $((Get-Content $m).Count) files, $bad differ."
}
function Backup-Winners {
  $z = "$Sig\ea_backup_12Oct2026\dna_winners_$(Get-Date -Format ddMMMyyyy_HHmm).zip"
  Compress-Archive -Path "$Hst\winners\*" -DestinationPath $z
  Add-Type -AssemblyName System.IO.Compression.FileSystem; $zip = [IO.Compression.ZipFile]::OpenRead($z); $n = $zip.Entries.Count; $zip.Dispose()
  Write-Host "Backup $z has $n entries (winners folder has $((Get-ChildItem "$Hst\winners" -File).Count))."
  Get-ChildItem "$Sig\ea_backup_12Oct2026\dna_winners_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 3 | ForEach-Object { Write-Host "Older backup kept (remove by hand if you want): $($_.Name)" }
}
function Edit-Queue { notepad "$Sig\data\extra_candidates.json" }

# ---- report controls (hourly vs daily phone reports) ----
function Pause-Hourly { Disable-ScheduledTask -TaskName 'EA Hourly Status (today)' -ErrorAction SilentlyContinue | Out-Null; Write-Host 'Hourly status reports paused (task disabled). Resume-Hourly turns them back on.' }
function Resume-Hourly {
  $t = Get-ScheduledTask -TaskName 'EA Hourly Status (today)' -ErrorAction SilentlyContinue
  if ($t) { Enable-ScheduledTask -TaskName 'EA Hourly Status (today)' | Out-Null; Write-Host 'Hourly status reports resumed.' }
  else {   # the task expires at midnight: recreate it from the next full hour until midnight
    $now = Get-Date; $start = $now.Date.AddHours($now.Hour + 1); $end = $now.Date.AddDays(1)
    $a = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\endos\Signal\scripts\hourly_status.ps1"'
    $tr = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ($end - $start); $tr.EndBoundary = $end.ToString('s')
    $se = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -DeleteExpiredTaskAfter (New-TimeSpan -Hours 1) -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
    Register-ScheduledTask -TaskName 'EA Hourly Status (today)' -Action $a -Trigger $tr -Settings $se -Description 'Hourly status to the phone until midnight.' -Force | Out-Null
    Write-Host "Hourly status reports recreated: next at $start, last before midnight." }
}
function Pause-Daily { Disable-ScheduledTask -TaskName 'EA Daily Summary' -ErrorAction SilentlyContinue | Out-Null; Write-Host 'Daily summary paused (task disabled). Resume-Daily turns it back on.' }
function Resume-Daily { Enable-ScheduledTask -TaskName 'EA Daily Summary' -ErrorAction SilentlyContinue | Out-Null; Write-Host 'Daily summary resumed (8:00 PM).' }
function Report-Now { & "$Sig\scripts\hourly_status.ps1"; Write-Host 'Status sent to the phone.' }
function Report-State {
  foreach ($n in 'EA Hourly Status (today)', 'EA Daily Summary') { $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue; if ($t) { $i = Get-ScheduledTaskInfo -TaskName $n; Write-Host ("{0}: {1}, next run {2}" -f $n, $t.State, $i.NextRunTime) } else { Write-Host "${n}: not scheduled" } }
}
Export-ModuleMember -Function *
