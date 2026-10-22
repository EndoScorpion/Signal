# install_monitor_tasks.ps1 — register both scheduled tasks. Run once as Admin.
$ErrorActionPreference = "Stop"
$scriptDir = "C:\Users\endos\Signal\relay"
New-Item -ItemType Directory -Force -Path $scriptDir | Out-Null

# Copy scripts if not already there
Copy-Item "$PSScriptRoot\laptop_monitor.ps1" "$scriptDir\laptop_monitor.ps1" -Force
Copy-Item "$PSScriptRoot\fxt_cleanup.ps1"   "$scriptDir\fxt_cleanup.ps1"   -Force

$ps = "powershell.exe"
$hidden = "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass"

# Task 1: snapshot every 10 min
$a1 = New-ScheduledTaskAction -Execute $ps -Argument "$hidden -File `"$scriptDir\laptop_monitor.ps1`""
$t1 = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 10) -Once -At (Get-Date)
Register-ScheduledTask -TaskName "SLC_LaptopMonitor" -Action $a1 -Trigger $t1 -RunLevel Highest -Force | Out-Null

# Task 2: FXT cleanup weekly Sunday 03:00
$a2 = New-ScheduledTaskAction -Execute $ps -Argument "$hidden -File `"$scriptDir\fxt_cleanup.ps1`""
$t2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "03:00"
Register-ScheduledTask -TaskName "SLC_FxtCleanup" -Action $a2 -Trigger $t2 -RunLevel Highest -Force | Out-Null

Write-Host "Tasks registered: SLC_LaptopMonitor (10 min) + SLC_FxtCleanup (weekly Sun 03:00)"
