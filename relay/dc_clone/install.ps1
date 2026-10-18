# DC Clone installer — run as Admin once
# Creates a Task Scheduler task that starts server.js at logon

param(
    [string]$RepoPath = "C:\Users\endos\Desktop\hst_work\Signal",
    [string]$Token    = $env:GITHUB_TOKEN,
    [string]$TaskName = "DcCloneServer"
)

Set-Location "$RepoPath\relay\dc_clone"

# Ensure node is available
$node = (Get-Command node -ErrorAction SilentlyContinue)?.Source
if (-not $node) { Write-Error "node.exe not found in PATH"; exit 1 }

# Persist token in user environment
if ($Token) {
    [System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $Token, "User")
    Write-Host "GITHUB_TOKEN saved to user environment"
} else {
    Write-Warning "No GITHUB_TOKEN provided — set it manually or create $env:USERPROFILE\.github_token"
}

# Create wrapper bat so Task Scheduler can launch it simply
$bat = "$RepoPath\relay\dc_clone\start_dc_clone.bat"
@"
@echo off
set GITHUB_TOKEN=%GITHUB_TOKEN%
node "$RepoPath\relay\dc_clone\server.js" >> "$RepoPath\relay\dc_clone\dc_clone.log" 2>&1
"@ | Set-Content -Encoding ASCII $bat

# Register Task Scheduler task (runs at any user logon, hidden)
$action  = New-ScheduledTaskAction -Execute $bat
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 0) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null

Write-Host "Task '$TaskName' registered. Starting now..."
Start-ScheduledTask -TaskName $TaskName
Write-Host "Done. Logs -> $RepoPath\relay\dc_clone\dc_clone.log"
