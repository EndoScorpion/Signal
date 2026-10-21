# Run ONCE to configure Cloud_DC_Watchdog in Task Scheduler
# Adds: 30s start delay + retry 3x every 1 min + trigger every 15 min + at login

$taskName = "Cloud_DC_Watchdog"

$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (-not $task) {
    Write-Host "ERROR: Task not found: $taskName"
    exit 1
}

# Settings: retry on failure 3x every 1 min, 1hr max runtime
$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew

# Trigger 1: at login with 30s delay
$trigLogin = New-ScheduledTaskTrigger -AtLogOn
$trigLogin.Delay = "PT30S"

# Trigger 2: repeat every 15 min
$trigRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 15) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

Set-ScheduledTask -TaskName $taskName -Settings $settings -Trigger @($trigLogin, $trigRepeat)
Write-Host "OK: $taskName configured — 30s login delay, retry 3x, every 15 min"
