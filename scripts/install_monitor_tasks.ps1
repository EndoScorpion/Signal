# install_monitor_tasks.ps1 — run as Admin, silent, no popups
# Installs: 1) every-10-min RAM/process snapshot -> relay/laptop_status.json
#           2) weekly FXT history cleanup
# Run via: wscript.exe scripts\run_hidden.vbs "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File scripts\install_monitor_tasks.ps1"

$ErrorActionPreference = 'SilentlyContinue'
$repoRoot = 'C:\Users\endos\Signal'
$scriptsDir = "$repoRoot\scripts"
$logLines = @()
$logLines += "install_monitor_tasks.ps1 started $(Get-Date -Format 'o')"

# === TASK 1: RAM/Process snapshot every 10 min ===
$snapshotScript = "$scriptsDir\laptop_snapshot.ps1"
$snapshotContent = @'
$repoRoot = 'C:\Users\endos\Signal'
$out = "$repoRoot\relay\laptop_status.json"
$procs = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 20 | ForEach-Object {
    @{ name=$_.ProcessName; pid=$_.Id; ram_mb=[math]::Round($_.WorkingSet64/1MB,1) }
}
$ram = Get-CimInstance Win32_OperatingSystem | Select-Object -First 1
$snapshot = @{
    timestamp = (Get-Date -Format 'o')
    free_ram_mb = [math]::Round($ram.FreePhysicalMemory/1KB,0)
    total_ram_mb = [math]::Round($ram.TotalVisibleMemorySize/1KB,0)
    top_procs = $procs
}
$snapshot | ConvertTo-Json -Depth 4 | Set-Content -Path $out
Set-Location $repoRoot
git add relay/laptop_status.json
git commit -m "relay: laptop snapshot $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
'@
Set-Content -Path $snapshotScript -Value $snapshotContent
$logLines += "Created: $snapshotScript"

# Register snapshot task (every 10 min, hidden)
$action = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument "`"$scriptsDir\run_hidden.vbs`" `"powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File `"$snapshotScript`"`""
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 10) -Once -At (Get-Date)
$settings = New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -MultipleInstances IgnoreNew
try {
    Unregister-ScheduledTask -TaskName 'LaptopMonitorSnapshot' -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName 'LaptopMonitorSnapshot' -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
    $logLines += 'Registered: LaptopMonitorSnapshot (every 10 min)'
} catch {
    $logLines += "Failed LaptopMonitorSnapshot: $($_.Exception.Message)"
}

# === TASK 2: Weekly FXT history cleanup ===
$fxtScript = "$scriptsDir\fxt_cleanup.ps1"
$fxtContent = @'
# FXT cleanup: delete .fxt files older than 90 days from MT4 history folders
$fxtDirs = @(
    'C:\Program Files (x86)\FXOpen MT4\history',
    'C:\Program Files\FXOpen MT4\history',
    "$env:APPDATA\MetaQuotes\Terminal"
)
foreach ($dir in $fxtDirs) {
    if (Test-Path $dir) {
        Get-ChildItem -Path $dir -Recurse -Filter '*.fxt' | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) } | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}
'@
Set-Content -Path $fxtScript -Value $fxtContent
$logLines += "Created: $fxtScript"

# Register weekly FXT cleanup (Sunday 03:00, hidden)
$fxtAction = New-ScheduledTaskAction -Execute 'wscript.exe' `
    -Argument "`"$scriptsDir\run_hidden.vbs`" `"powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File `"$fxtScript`"`""
$fxtTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '03:00'
$fxtSettings = New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -MultipleInstances IgnoreNew
try {
    Unregister-ScheduledTask -TaskName 'FXTWeeklyCleanup' -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName 'FXTWeeklyCleanup' -Action $fxtAction -Trigger $fxtTrigger -Settings $fxtSettings -RunLevel Highest -Force
    $logLines += 'Registered: FXTWeeklyCleanup (Sunday 03:00)'
} catch {
    $logLines += "Failed FXTWeeklyCleanup: $($_.Exception.Message)"
}

# Start snapshot task immediately
Start-ScheduledTask -TaskName 'LaptopMonitorSnapshot' -ErrorAction SilentlyContinue
$logLines += 'Started LaptopMonitorSnapshot immediately'

# Write outbox
$outbox = "$repoRoot\relay\outbox_to_cloud.md"
$report = "# LocalThug Outbox - MONITOR TASKS INSTALLED`n## $(Get-Date -Format 'o')`n`n$($logLines | ForEach-Object { "- $_" } | Out-String)"
Set-Content -Path $outbox -Value $report
Set-Location $repoRoot
git add relay/outbox_to_cloud.md relay/laptop_status.json scripts/laptop_snapshot.ps1 scripts/fxt_cleanup.ps1
git commit -m "relay: monitor tasks installed $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
