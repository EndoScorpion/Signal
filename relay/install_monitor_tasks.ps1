# install_monitor_tasks.ps1
# Run as Admin: powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File relay\install_monitor_tasks.ps1
# (1) Patches ALL scheduled tasks containing DC/Watchdog/Relay/Poller to -WindowStyle Hidden
# (2) Creates/updates a RAM-snapshot task writing to laptop_status.json every 15 min

$ErrorActionPreference = 'Continue'
$statusFile = "$env:USERPROFILE\Signal\laptop_status.json"

# --- 1. Patch existing scheduled tasks to hidden window ---
$tasks = Get-ScheduledTask | Where-Object { $_.TaskName -match 'DC|Watchdog|Relay|Poller|Clone|CloudCmd' }
foreach ($t in $tasks) {
    $changed = $false
    foreach ($a in $t.Actions) {
        if ($a.Execute -match 'powershell|cmd' -and $a.Arguments -notmatch '-WindowStyle Hidden') {
            $a.Arguments = "-WindowStyle Hidden " + $a.Arguments
            $changed = $true
        }
    }
    if ($changed) {
        Set-ScheduledTask -TaskName $t.TaskName -TaskPath $t.TaskPath -Action $t.Actions -EA SilentlyContinue
        Write-Host "Patched (hidden): $($t.TaskName)"
    } else {
        Write-Host "Already hidden or no change: $($t.TaskName)"
    }
}

# --- 2. Create RAM-snapshot scheduled task (every 15 min) ---
$snapScript = @'
Param($outFile)
$top = Get-Process | Sort-Object WorkingSet64 -Desc | Select-Object -First 30 |
    Select-Object Id,ProcessName,@{N='MB';E={[math]::Round($_.WorkingSet64/1MB,1)}}
$snap = @{ ts=(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'); top_procs=$top }
$snap | ConvertTo-Json -Depth 4 | Set-Content $outFile -Force
'@

$snapPath = "$env:USERPROFILE\Signal\ram_snapshot.ps1"
Set-Content $snapPath $snapScript -Force

$action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$snapPath`" -outFile `"$statusFile`""
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 15) -Once -At (Get-Date)
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName 'SignalRamSnapshot' -Confirm:$false -EA SilentlyContinue
Register-ScheduledTask -TaskName 'SignalRamSnapshot' -Action $action -Trigger $trigger `
    -Settings $settings -RunLevel Highest -Force | Out-Null
Write-Host "RAM snapshot task registered -> $statusFile every 15 min"

# --- 3. Kill visible popup windows for relay processes ---
$popups = Get-Process | Where-Object {
    $_.MainWindowTitle -ne '' -and $_.Name -in @('powershell','cmd','WindowsTerminal')
}
foreach ($p in $popups) {
    Write-Host "Visible window: PID=$($p.Id) $($p.ProcessName) [$($p.MainWindowTitle)]"
    # Don't auto-kill — user reviews; they can Stop-Process manually
}

Write-Host ""
Write-Host "Done. Next: Start-Service CloudCmdPollerGH   (starts NSSM hidden service)"
Write-Host "Or restart watchdog: Start-ScheduledTask Cloud_DC_Watchdog"
