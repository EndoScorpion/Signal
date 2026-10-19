#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Boot-time RAM hog limiter for Nasif's Lenovo laptop (PS 5.1, Windows 10/11).
    Applies registry/policy settings to cap WebView2, Edge, Widgets, and other hogs.
    Also registers a startup SYSTEM task that periodically trims working sets of
    non-MT4 processes every 5 minutes.

.NOTES
    Safe to run repeatedly (idempotent registry writes).
    Does NOT kill Claude desktop — it needs WebView2, so we limit background
    components only, not msedgewebview2.exe itself.
    Run once as Administrator; settings survive reboots via registry + Task Scheduler.
    Verdict: no pre-Windows boot hook can limit user-space processes (WebView2 starts
    after Windows login), but startup tasks, group policy registry keys applied before
    first user login (HKLM), and disabling the auto-launch triggers are the real levers.
    This script applies all safe ones.
#>

Set-StrictMode -Version 2
$ErrorActionPreference = "Stop"

# ── Protected process names (never trim these) ───────────────────────────────
$PROTECTED = @(
    "terminal",          # MT4 terminal.exe
    "metatester",        # MT4 backtester
    "metatester64",
    "DcCloneServer",
    "node",              # DC Clone server.js
    "CloudCmdPoller",
    "CloudCmdPollerGH",
    "claude",            # Claude desktop
    "powershell",        # running pollers/scripts
    "python",
    "python3"
)

function Write-Step { param($msg) Write-Host "[limit_ram_hogs] $msg" -ForegroundColor Cyan }

# ── 1. Edge / WebView2 background & prelaunch policies ───────────────────────
Write-Step "1/6  Edge + WebView2 policies"
$edgePol = "HKLM:\SOFTWARE\Policies\Microsoft\Edge"
if (-not (Test-Path $edgePol)) { New-Item -Path $edgePol -Force | Out-Null }
$edgeVals = @{
    "BackgroundModeEnabled"   = 0   # no Edge background tab keeping
    "StartupBoostEnabled"     = 0   # no prelaunch on Windows start
    "SleepingTabsEnabled"     = 1   # put inactive tabs to sleep (saves RAM)
    "SleepingTabsTimeout"     = 30  # seconds before sleeping
    "WebWidgetAllowed"        = 0   # Edge sidebar widget
    "HideFirstRunExperience"  = 1
}
foreach ($k in $edgeVals.Keys) {
    Set-ItemProperty -Path $edgePol -Name $k -Value $edgeVals[$k] -Type DWord -Force
}

# ── 2. Windows Widgets (News & Interests / taskbar web content) ───────────────
Write-Step "2/6  Windows Widgets + Search web content"
$dshPol = "HKLM:\SOFTWARE\Policies\Microsoft\Dsh"
if (-not (Test-Path $dshPol)) { New-Item -Path $dshPol -Force | Out-Null }
Set-ItemProperty -Path $dshPol -Name "AllowNewsAndInterests" -Value 0 -Type DWord -Force

$searchPol = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search"
if (-not (Test-Path $searchPol)) { New-Item -Path $searchPol -Force | Out-Null }
Set-ItemProperty -Path $searchPol -Name "DisableWebSearch"          -Value 1 -Type DWord -Force
Set-ItemProperty -Path $searchPol -Name "ConnectedSearchUseWeb"     -Value 0 -Type DWord -Force
Set-ItemProperty -Path $searchPol -Name "AllowCortana"              -Value 0 -Type DWord -Force

# Disable Windows Search indexer (huge I/O + RAM hog; disable if not needed)
Write-Step "   Disabling Windows Search indexer service (WSearch) ..."
Set-Service -Name "WSearch" -StartupType Disabled -ErrorAction SilentlyContinue
Stop-Service -Name "WSearch" -Force -ErrorAction SilentlyContinue

# ── 3. Xbox Game Bar / Game DVR ───────────────────────────────────────────────
Write-Step "3/6  Xbox Game Bar / DVR"
$gamePol = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR"
if (-not (Test-Path $gamePol)) { New-Item -Path $gamePol -Force | Out-Null }
Set-ItemProperty -Path $gamePol -Name "AllowGameDVR" -Value 0 -Type DWord -Force

$xboxSvc = @("XblAuthManager","XblGameSave","XboxGipSvc","XboxNetApiSvc")
foreach ($s in $xboxSvc) {
    Set-Service -Name $s -StartupType Disabled -ErrorAction SilentlyContinue
    Stop-Service -Name $s -Force -ErrorAction SilentlyContinue
}

# ── 4. OneDrive autostart ─────────────────────────────────────────────────────
Write-Step "4/6  OneDrive autostart"
$oneDriveKey = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
Remove-ItemProperty -Path $oneDriveKey -Name "OneDrive" -ErrorAction SilentlyContinue
# Disable via policy so it stays gone after updates
$odPol = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive"
if (-not (Test-Path $odPol)) { New-Item -Path $odPol -Force | Out-Null }
Set-ItemProperty -Path $odPol -Name "DisableFileSyncNGSC" -Value 1 -Type DWord -Force

# ── 5. Teams / Office prelaunch + Phone Link / Copilot ───────────────────────
Write-Step "5/6  Teams prelaunch + Phone Link + Copilot sidebar"
# New Teams (ms-teams) autostart via Run key
$runKey = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
foreach ($n in @("com.squirrel.Teams.Teams","Teams","PhoneLink","Copilot")) {
    Remove-ItemProperty -Path $runKey -Name $n -ErrorAction SilentlyContinue
}
# Copilot button / sidebar policy
$copPol = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot"
if (-not (Test-Path $copPol)) { New-Item -Path $copPol -Force | Out-Null }
Set-ItemProperty -Path $copPol -Name "TurnOffWindowsCopilot" -Value 1 -Type DWord -Force

# Disable Phone Link autostart service
Set-Service -Name "PhoneService" -StartupType Disabled -ErrorAction SilentlyContinue
Stop-Service  -Name "PhoneService" -Force -ErrorAction SilentlyContinue

# ── 6. Register startup task: trim working sets every 5 min ──────────────────
Write-Step "6/6  Registering startup Task Scheduler task: TrimRamHogs"

# Build the inline trimmer script — stored in a fixed location
$trimScript = @'
# TrimRamHogs_runner.ps1
# Trims working sets of RAM hogs every 5 minutes.
# Protected: terminal, metatester*, DcCloneServer, node, CloudCmd*, claude, powershell, python*

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WinMem {
    [DllImport("kernel32.dll")]
    public static extern bool SetProcessWorkingSetSize(IntPtr h, IntPtr min, IntPtr max);
    [DllImport("kernel32.dll")]
    public static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
    [DllImport("kernel32.dll")]
    public static extern bool CloseHandle(IntPtr h);
}
"@

$PROTECTED = @("terminal","metatester","metatester64","DcCloneServer","node",
               "CloudCmdPoller","CloudCmdPollerGH","claude","powershell",
               "python","python3","svchost","system","smss","csrss","lsass",
               "services","winlogon","wininit","explorer")

while ($true) {
    $procs = Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $n = $_.ProcessName.ToLower()
        $keep = $false
        foreach ($p in $PROTECTED) { if ($n -like "*$p*") { $keep = $true; break } }
        -not $keep -and $_.WorkingSet64 -gt 50MB
    }
    foreach ($p in $procs) {
        try {
            $h = [WinMem]::OpenProcess(0x1F0FFF, $false, $p.Id)
            if ($h -ne [IntPtr]::Zero) {
                [WinMem]::SetProcessWorkingSetSize($h, [IntPtr](-1), [IntPtr](-1)) | Out-Null
                [WinMem]::CloseHandle($h) | Out-Null
            }
        } catch {}
    }
    Start-Sleep -Seconds 300
}
'@

$scriptDir  = "C:\Users\endos\Desktop\hst_out"
$scriptPath = Join-Path $scriptDir "TrimRamHogs_runner.ps1"

if (-not (Test-Path $scriptDir)) { New-Item -ItemType Directory -Path $scriptDir -Force | Out-Null }
[System.IO.File]::WriteAllText($scriptPath, $trimScript, [System.Text.Encoding]::ASCII)

# Register as Task Scheduler task (SYSTEM, At startup, hidden)
$taskName = "Cloud_TrimRamHogs"
$action   = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger  = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -MultipleInstances IgnoreNew `
    -Hidden
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask `
    -TaskName  $taskName `
    -Action    $action `
    -Trigger   $trigger `
    -Settings  $settings `
    -Principal $principal `
    -Force | Out-Null

Write-Step "Task '$taskName' registered. Start it now without rebooting:"
Write-Host "  Start-ScheduledTask -TaskName 'Cloud_TrimRamHogs'" -ForegroundColor Yellow

Write-Step "Done. Reboot or run the above line to activate trimmer immediately."
Write-Step "IMPORTANT: Claude desktop uses WebView2 — do NOT kill msedgewebview2.exe."
