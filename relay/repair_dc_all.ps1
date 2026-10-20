# repair_dc_all.ps1 - One-shot repair: DC Clone + CloudCmdPollerGH
# Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\endos\Signal\relay\repair_dc_all.ps1
Set-Location "C:\Users\endos\Signal"

Write-Host "=== DC Repair $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ') ==="

# 1. Git pull latest
$pull = & git -C "C:\Users\endos\Signal" pull origin relay --rebase 2>&1
Write-Host "git pull: $pull"

# 2. Kill existing node server.js if running
$procs = Get-Process node -EA SilentlyContinue | Where-Object {
    (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)" -EA SilentlyContinue).CommandLine -match 'server\.js'
}
foreach ($p in $procs) { Stop-Process -Id $p.Id -Force -EA SilentlyContinue; Write-Host "Killed node PID $($p.Id)" }
Start-Sleep 2

# 3. Repoint DcCloneServer task -> git checkout path
$action = New-ScheduledTaskAction -Execute "C:\Program Files\nodejs\node.exe" `
    -Argument '"C:\Users\endos\Signal\relay\dc_clone\server.js"' `
    -WorkingDirectory "C:\Users\endos\Signal\relay\dc_clone"
Set-ScheduledTask -TaskName "DcCloneServer" -Action $action -EA Stop | Out-Null
Write-Host "DcCloneServer task repointed to git checkout"

# 4. Repoint CloudCmdPollerGH -> git checkout path
$a2 = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -File C:\Users\endos\Signal\relay\cmd_poller.ps1"
$t2 = Get-ScheduledTask -TaskName "CloudCmdPollerGH" -EA SilentlyContinue
if ($t2) {
    Set-ScheduledTask -TaskName "CloudCmdPollerGH" -Action $a2 -EA Stop | Out-Null
    Write-Host "CloudCmdPollerGH repointed to git checkout"
}

# 5. Patch device ID in start_dcremote.ps1 if old ID present
$f = "C:\tools\start_dcremote.ps1"
if (Test-Path $f) {
    $c = Get-Content $f -Raw
    if ($c -match "987fd7bd") {
        $c2 = $c -replace "987fd7bd[^`"' ]*", "24123e3e-6795-430b-abf6-32e186477523"
        Set-Content $f $c2 -NoNewline
        Write-Host "Device ID patched in start_dcremote.ps1"
    } else { Write-Host "Device ID ok in start_dcremote.ps1" }
}

# 6. Start DC Clone via scheduled task
Start-ScheduledTask -TaskName "DcCloneServer" -EA SilentlyContinue
Start-Sleep 5
$p2 = Get-Process node -EA SilentlyContinue | Where-Object {
    (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)" -EA SilentlyContinue).CommandLine -match "server\.js"
}
if ($p2) { Write-Host "DC Clone RUNNING PID $($p2.Id)" }
else { Write-Host "DC Clone NOT running - check node path"; node --version }

# 7. Start CloudCmdPollerGH
$t3 = Get-ScheduledTask -TaskName "CloudCmdPollerGH" -EA SilentlyContinue
if ($t3) { Start-ScheduledTask -TaskName "CloudCmdPollerGH" -EA SilentlyContinue; Write-Host "CloudCmdPollerGH started" }

# Poller log is at: C:\Users\endos\Desktop\hst_out\cmd_poller.log
Start-Sleep 3
$logFile = "C:\Users\endos\Desktop\hst_out\cmd_poller.log"
if (Test-Path $logFile) {
    Write-Host "--- Last 5 poller log lines ---"
    Get-Content $logFile -Tail 5
} else { Write-Host "Poller log not yet created: $logFile" }

Write-Host "=== Repair done ==="
