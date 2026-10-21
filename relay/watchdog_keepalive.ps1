# Cloud_DC_Watchdog v2 — keepalive + no-sleep + polling restart
# Task Scheduler: run at login (30s delay) + every 15 min

# 1. Keep laptop awake
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 0

# 2. Restart CloudCmdPollerGH if not running
$pollerProcs = Get-Process -Name "pwsh","powershell" -ErrorAction SilentlyContinue
$pollerRunning = $pollerProcs | Where-Object {
    (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine -like "*cmd_poller*"
}
if (-not $pollerRunning) {
    Start-ScheduledTask "CloudCmdPollerGH" -ErrorAction SilentlyContinue
}

# 3. DC Remote keepalive — restart node if not running
$nodeRunning = Get-Process -Name "node" -ErrorAction SilentlyContinue
if (-not $nodeRunning) {
    Start-Process "cmd" -ArgumentList "/c npx @wonderwhy-er/desktop-commander@latest remote >> $env:USERPROFILE\dc_remote.log 2>&1" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Add-Content "$env:USERPROFILE\watchdog.log" "$(Get-Date -Format u) DC Remote restarted"
}

# 4. DC Clone keepalive
Start-ScheduledTask "DcCloneServer" -ErrorAction SilentlyContinue

Add-Content "$env:USERPROFILE\watchdog.log" "$(Get-Date -Format u) Watchdog tick done"
