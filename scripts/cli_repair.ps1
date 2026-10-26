# cli_repair.ps1 — safe Claude CLI environment repair
# Kills NSSM orphan PS, wscript popups, relaunches AutoMinimize.ahk
# NO boot changes. NO MT4/EA/set files touched.

$ErrorActionPreference = 'SilentlyContinue'
$log = @()
$log += "cli_repair START $(Get-Date -Format 'HH:mm:ss')"

$osBefore = Get-CimInstance Win32_OperatingSystem
$ramBefore = [math]::Round($osBefore.FreePhysicalMemory/1MB, 2)

# 1. Kill wscript popups
$ws = Get-Process wscript -ErrorAction SilentlyContinue
foreach ($p in $ws) { $p | Stop-Process -Force; $log += "killed wscript PID $($p.Id)" }

# 2. Kill NSSM orphan PS processes (blank cmdline, not Claude CLI, not DC)
$claudePID  = (Get-WmiObject Win32_Process -Filter "CommandLine LIKE '%CLAUDE_CODE%'").ProcessId
$dcPID      = (Get-WmiObject Win32_Process -Filter "CommandLine LIKE '%desktop-commander%'").ProcessId
$keepPIDs   = @($PID) + @($claudePID) + @($dcPID) | Where-Object { $_ }

Get-WmiObject Win32_Process -Filter "Name='powershell.exe'" | Where-Object {
    $_.CommandLine -eq $null -and $_.ProcessId -notin $keepPIDs
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
    $log += "killed orphan PS PID $($_.ProcessId)"
}

# 3. Relaunch AutoMinimize.ahk if not running
$ahkRunning = Get-WmiObject Win32_Process -Filter "Name='AutoHotkey.exe'" |
    Where-Object { $_.CommandLine -like "*AutoMinimize*" }
# Never kill first — just launch; #SingleInstance Force replaces old instance silently (no popup)
$ahkPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\AutoMinimize.ahk"
if (Test-Path $ahkPath) {
    Start-Process "C:\Program Files\AutoHotkey\AutoHotkey.exe" -ArgumentList "`"$ahkPath`"" -WindowStyle Hidden
    $log += "launched AutoMinimize.ahk (SingleInstance Force handles takeover silently)"
} else { $log += "WARNING: AutoMinimize.ahk not found" }

# 4. RAM report
Start-Sleep -Seconds 1
$osAfter = Get-CimInstance Win32_OperatingSystem
$ramAfter = [math]::Round($osAfter.FreePhysicalMemory/1MB, 2)
$log += "RAM: $ramBefore GB -> $ramAfter GB (freed $([math]::Round($ramAfter-$ramBefore,2)) GB)"
$log += "cli_repair DONE $(Get-Date -Format 'HH:mm:ss')"

# Write log
$logPath = "C:\Users\endos\Signal\Logs\cli_repair.log"
$log | ForEach-Object { "$(Get-Date -Format 'HH:mm:ss') $_" } | Add-Content -Path $logPath
$log | ForEach-Object { Write-Host $_ }
