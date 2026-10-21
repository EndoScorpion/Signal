# popup_fix_v4.ps1 — patch all scheduled tasks to run hidden, no visible windows ever
# Run via: wscript.exe scripts\run_hidden.vbs "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File scripts\popup_fix_v4.ps1"

$ErrorActionPreference = 'SilentlyContinue'
$logLines = @()
$logLines += "POPUP FIX v4 started $(Get-Date -Format 'o')"

$vbs = "$PSScriptRoot\run_hidden.vbs"
$logLines += "VBS launcher: $vbs (exists=$(Test-Path $vbs))"

# STEP 1: create run_safe.ps1
$safeScript = "$PSScriptRoot\run_safe.ps1"
if (-not (Test-Path $safeScript)) {
    $safeContent = @'
function Invoke-Hidden {
    param([string]$ScriptPath, [string]$Args = "")
    $vbs = Join-Path $PSScriptRoot 'run_hidden.vbs'
    $cmd = "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File `"$ScriptPath`" $Args"
    Start-Process wscript.exe -ArgumentList "`"$vbs`" `"$cmd`"" -WindowStyle Hidden -Wait
}
function Invoke-HiddenCmd {
    param([string]$Command)
    $vbs = Join-Path $PSScriptRoot 'run_hidden.vbs'
    Start-Process wscript.exe -ArgumentList "`"$vbs`" `"cmd.exe /c $Command`"" -WindowStyle Hidden -Wait
}
'@
    Set-Content -Path $safeScript -Value $safeContent
    $logLines += "run_safe.ps1 created"
} else {
    $logLines += "run_safe.ps1 exists"
}

# STEP 2: patch ALL scheduled tasks
$patched = @()
$skipped = @()
Get-ScheduledTask | ForEach-Object {
    $task = $_
    $needsPatch = $false
    foreach ($action in $task.Actions) {
        if ($action.Execute -match 'powershell' -and $action.Arguments -notmatch '-WindowStyle Hidden') { $needsPatch = $true }
        if ($action.Execute -match 'cmd\.exe' -and $action.Arguments -notmatch 'run_hidden\.vbs') { $needsPatch = $true }
    }
    if ($needsPatch) {
        try {
            $newActions = $task.Actions | ForEach-Object {
                if ($_.Execute -match 'powershell' -and $_.Arguments -notmatch '-WindowStyle Hidden') {
                    New-ScheduledTaskAction -Execute $_.Execute -Argument ("-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass " + $_.Arguments)
                } elseif ($_.Execute -match 'cmd\.exe' -and $_.Arguments -notmatch 'run_hidden\.vbs') {
                    New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ("`"$vbs`" `"$($_.Execute) $($_.Arguments)`"")
                } else { $_ }
            }
            Set-ScheduledTask -TaskName $task.TaskName -TaskPath $task.TaskPath -Action $newActions
            $patched += $task.TaskName
        } catch {
            $skipped += "$($task.TaskName): $($_.Exception.Message)"
        }
    }
}
$logLines += "Patched $($patched.Count) tasks: $($patched -join ', ')"
$logLines += "Skipped $($skipped.Count): $($skipped -join ' | ')"

# STEP 3: force-patch known tasks
foreach ($taskName in @('CloudCmdPollerGH','DcRemoteServer','SignalAutoBackup','Cloud_DC_Watchdog')) {
    $t = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($t) {
        $a = $t.Actions[0]
        if ($a.Execute -match 'powershell' -and $a.Arguments -notmatch '-WindowStyle Hidden') {
            try {
                $newArg = "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass " + $a.Arguments
                Set-ScheduledTask -TaskName $taskName -Action (New-ScheduledTaskAction -Execute $a.Execute -Argument $newArg)
                $logLines += "Force-patched: $taskName"
            } catch { $logLines += "Force-patch failed $taskName: $($_.Exception.Message)" }
        } else { $logLines += "Already hidden: $taskName" }
    } else { $logLines += "Not found: $taskName" }
}

# STEP 4: close visible PS/CMD windows (except self)
$closed = 0
Get-Process -Name 'powershell','cmd','wscript' -ErrorAction SilentlyContinue |
    Where-Object { $_.Id -ne $PID -and $_.MainWindowHandle -ne [IntPtr]::Zero } |
    ForEach-Object { try { $_.CloseMainWindow() | Out-Null; $closed++ } catch {} }
$logLines += "Closed $closed visible windows"

# STEP 5: diagnostic
$stillVisible = Get-ScheduledTask | Where-Object {
    $_.Actions | Where-Object {
        ($_.Execute -match 'powershell' -and $_.Arguments -notmatch '-WindowStyle Hidden') -or
        ($_.Execute -match 'cmd\.exe' -and $_.Arguments -notmatch 'run_hidden\.vbs')
    }
} | Select-Object -ExpandProperty TaskName
$logLines += "STILL VISIBLE: $($stillVisible -join ', ')"

# STEP 6: write outbox and push
$repoRoot = Split-Path $PSScriptRoot
$outbox = "$repoRoot\relay\outbox_to_cloud.md"
$status = if ($stillVisible.Count -eq 0) { 'SUCCESS - ALL TASKS HIDDEN - NO MORE POPUPS' } else { "WARNING: $($stillVisible.Count) still visible: $($stillVisible -join ', ')" }
$report = "# LocalThug Outbox - POPUP FIX v4 REPORT`n## Timestamp: $(Get-Date -Format 'o')`n`n$($logLines | ForEach-Object { "- $_" } | Out-String)`n## STATUS: $status"
Set-Content -Path $outbox -Value $report
Set-Location $repoRoot
git add relay/outbox_to_cloud.md
git commit -m "relay: popup fix v4 report $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
