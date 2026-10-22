# laptop_monitor.ps1 — auto snapshot + relay commit
# Runs every 10 min via Task Scheduler. No popups, no visible windows.

$ErrorActionPreference = "SilentlyContinue"
$repoPath = "C:\Users\endos\Signal"
$outFile  = "$repoPath\relay\laptop_status.json"

# --- collect data ---
$ram = Get-CimInstance Win32_OperatingSystem
$ramFreeMB  = [math]::Round($ram.FreePhysicalMemory / 1024)
$ramTotalMB = [math]::Round($ram.TotalVisibleMemorySize / 1024)
$ramUsedMB  = $ramTotalMB - $ramFreeMB

$watchProcs = @("MT4","terminal","metatrader","CloudCmdPollerGH","DesktopCommanderServer","ClaudeCLI","claude","firefox","Firefox")
$procStatus = @{}
foreach ($name in $watchProcs) {
    $p = Get-Process -Name $name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($p) { $procStatus[$name] = @{ running=$true; pid=$p.Id } }
    else    { $procStatus[$name] = @{ running=$false; pid=$null } }
}

# MT4 canonical check
$mt4 = Get-Process -Name "terminal","metatrader","MT4" -ErrorAction SilentlyContinue | Select-Object -First 1
$mt4Running = ($mt4 -ne $null)
$mt4Pid     = if ($mt4) { $mt4.Id } else { $null }

# Top 5 RAM hogs
$top5 = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 |
        ForEach-Object { @{ name=$_.Name; mb=[math]::Round($_.WorkingSet64/1MB) } }

# Visible popup windows (non-empty title, not taskbar/shell)
$popups = @()
try {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
    $allWindows = [System.Diagnostics.Process]::GetProcesses() |
        Where-Object { $_.MainWindowTitle -ne "" -and $_.MainWindowTitle -notmatch "^(Program Manager|FXOpen|MetaTrader|Firefox)$" } |
        ForEach-Object { $_.MainWindowTitle }
    $popups = @($allWindows | Select-Object -Unique)
} catch {}

# FXT storage check
$fxtPaths = @(
    "C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\Tester",
    "C:\Users\endos\Desktop\mt4_tester",
    "C:\Users\endos\Desktop\mt4_tester2"
)
$fxtTotalMB = 0
foreach ($fp in $fxtPaths) {
    if (Test-Path $fp) {
        $fxtTotalMB += [math]::Round((Get-ChildItem $fp -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1MB)
    }
}
$fxtAlertGB = [math]::Round($fxtTotalMB / 1024, 2)
$fxtAlert   = ($fxtTotalMB -gt 5120)

$snapshot = @{
    ts              = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    ram_free_mb     = $ramFreeMB
    ram_used_mb     = $ramUsedMB
    ram_total_mb    = $ramTotalMB
    mt4_running     = $mt4Running
    mt4_pid         = $mt4Pid
    procs           = $procStatus
    top5_ram        = $top5
    popups          = $popups
    fxt_total_gb    = $fxtAlertGB
    fxt_alert       = $fxtAlert
}

# --- write file ---
New-Item -ItemType Directory -Force -Path "$repoPath\relay" | Out-Null
$snapshot | ConvertTo-Json -Depth 5 | Set-Content -Path $outFile -Encoding UTF8

# --- git commit + push ---
Push-Location $repoPath
git add relay/laptop_status.json 2>&1 | Out-Null
$msg = "chore: laptop snapshot $($snapshot.ts)"
git commit -m $msg 2>&1 | Out-Null
git push origin relay 2>&1 | Out-Null
Pop-Location
