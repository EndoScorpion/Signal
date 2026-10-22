# HIDE_POPUP_WINDOWS.ps1 — patches watchdog + scheduled tasks to use -WindowStyle Hidden
# Run once as Admin. Safe — only changes how scripts are launched, not what they do.

# 1. Update watchdog_dc_all.ps1 to add -WindowStyle Hidden to all Start-Process calls
$watchdogPaths = @(
    "$env:USERPROFILE\Desktop\watchdog_dc_all.ps1",
    "$env:USERPROFILE\Documents\watchdog_dc_all.ps1",
    "C:\Users\endos\watchdog_dc_all.ps1"
)
foreach ($wp in $watchdogPaths) {
    if (Test-Path $wp) {
        $content = Get-Content $wp -Raw
        $patched = $content -replace '(Start-Process\s+powershell(?!.*-WindowStyle))', '$1 -WindowStyle Hidden'
        $patched = $patched -replace '(Start-Process\s+cmd(?!.*-WindowStyle))', '$1 -WindowStyle Hidden'
        Set-Content $wp $patched
        Write-Host "Patched: $wp"
    }
}

# 2. Update scheduled tasks: find relay tasks, ensure hidden window
$tasks = Get-ScheduledTask | Where-Object { $_.TaskName -match "DC|Watchdog|Relay|Poller" }
foreach ($t in $tasks) {
    $action = $t.Actions | Where-Object { $_.Execute -match "powershell|cmd" }
    foreach ($a in $action) {
        if ($a.Arguments -notmatch "-WindowStyle Hidden") {
            $a.Arguments = "-WindowStyle Hidden " + $a.Arguments
        }
    }
    Set-ScheduledTask -TaskName $t.TaskName -Action $t.Actions -EA SilentlyContinue
    Write-Host "Updated task: $($t.TaskName)"
}

# 3. Report visible relay windows
$visible = Get-Process | Where-Object { $_.MainWindowTitle -ne "" -and $_.Name -in @("powershell","cmd","node") }
$visible | Select-Object Id,Name,MainWindowTitle | Format-Table -AutoSize
Write-Host "Done. Restart watchdog: Stop-ScheduledTask DcCloneServer; Start-ScheduledTask DcCloneServer"
