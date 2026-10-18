# DC Clone installer — run as Admin once
# Creates a Task Scheduler task that starts server.js at logon

param(
    [string]$RepoPath = "C:\Users\endos\Desktop\hst_work\Signal",
    [string]$Token    = $env:GITHUB_TOKEN,
    [string]$TaskName = "DcCloneServer"
)

Set-Location "$RepoPath\relay\dc_clone"

# Ensure node is available
$nodePath = (Get-Command node -ErrorAction SilentlyContinue)
if ($null -eq $nodePath) {
    Write-Error "node.exe not found in PATH"
    exit 1
}
$node = $nodePath.Source

# Persist token in user environment
if ($Token) {
    [System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $Token, "User")
    Write-Host "GITHUB_TOKEN saved to user environment"
} else {
    Write-Warning "No GITHUB_TOKEN provided -- set it manually or create $env:USERPROFILE\.github_token"
}

# Create wrapper bat so Task Scheduler can launch it simply
$bat = "$RepoPath\relay\dc_clone\start_dc_clone.bat"
$batContent = "@echo off`r`nset GITHUB_TOKEN=%GITHUB_TOKEN%`r`n`"$node`" `"$RepoPath\relay\dc_clone\server.js`" >> `"$RepoPath\relay\dc_clone\dc_clone.log`" 2>&1`r`n"
[System.IO.File]::WriteAllText($bat, $batContent, [System.Text.Encoding]::ASCII)

# Register Task Scheduler task (runs at any user logon, hidden)
$action   = New-ScheduledTaskAction -Execute $bat
$trigger  = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 0) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null

Write-Host "Task '$TaskName' registered. Starting now..."
Start-ScheduledTask -TaskName $TaskName
Write-Host "Done. Logs -> $RepoPath\relay\dc_clone\dc_clone.log"
