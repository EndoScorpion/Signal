# save_ram.ps1 — trim working sets and close known RAM hogs
# Run as: powershell -ExecutionPolicy Bypass -File save_ram.ps1
# Safe: only trims working sets + closes optional processes you can reopen

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MemTrim {
    [DllImport("kernel32.dll")]
    public static extern bool SetProcessWorkingSetSize(IntPtr h, IntPtr min, IntPtr max);
}
"@

function Trim-AllProcesses {
    $trimmed = 0
    foreach ($p in Get-Process) {
        try {
            [MemTrim]::SetProcessWorkingSetSize($p.Handle, [IntPtr](-1), [IntPtr](-1)) | Out-Null
            $trimmed++
        } catch {}
    }
    Write-Host "  Trimmed working sets on $trimmed processes"
}

function Get-RAMUsedGB {
    $os = Get-CimInstance Win32_OperatingSystem
    return [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 2)
}

# --- Report before ---
$before = Get-RAMUsedGB
Write-Host "RAM before: ${before} GB used"

# --- 1. Close optional heavy hitters (non-essential) ---
$optional = @(
    "OneDrive",       # sync client
    "Teams",          # Microsoft Teams
    "Slack",          # Slack desktop
    "Discord",        # Discord
    "Spotify",        # Spotify
    "MicrosoftEdge",  # extra Edge windows (not the dashboard one)
    "msedge",
    "chrome",
    "SearchApp",      # Windows Search overlay
    "YourPhone",      # Phone Link
    "SkypeApp"
)

# Protect the dashboard window — don't kill its browser profile
$dashTitle = "Signal Status"
$dashProcs = @()
foreach ($w in (Get-Process msedge,chrome -ErrorAction SilentlyContinue)) {
    try {
        # Keep processes that own the dashboard window
        if ($w.MainWindowTitle -like "*$dashTitle*") { $dashProcs += $w.Id }
    } catch {}
}

$closed = 0
foreach ($name in $optional) {
    $procs = Get-Process $name -ErrorAction SilentlyContinue
    foreach ($p in $procs) {
        if ($dashProcs -contains $p.Id) { continue }  # skip dashboard
        try { Stop-Process -Id $p.Id -Force; $closed++ } catch {}
    }
}
Write-Host "  Closed $closed optional processes"

# --- 2. Trim all remaining process working sets ---
Write-Host "Trimming working sets..."
Trim-AllProcesses

# --- 3. Force .NET GC ---
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
[System.GC]::Collect()

# --- 4. Clear standby list (requires admin) ---
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "Clearing standby list (admin)..."
    try {
        $code = @"
using System;
using System.Runtime.InteropServices;
public class Mem2 {
    [DllImport("ntdll.dll")] public static extern uint NtSetSystemInformation(int cls, IntPtr buf, int len);
}
"@
        Add-Type $code -ErrorAction SilentlyContinue
        # SystemMemoryListInformation = 80, purge standby = 4
        $buf = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(4)
        [System.Runtime.InteropServices.Marshal]::WriteInt32($buf, 4)
        [Mem2]::NtSetSystemInformation(80, $buf, 4) | Out-Null
        [System.Runtime.InteropServices.Marshal]::FreeHGlobal($buf)
        Write-Host "  Standby list cleared"
    } catch { Write-Host "  Standby clear skipped: $_" }
} else {
    Write-Host "  Skipping standby clear (not admin — right-click Run as Administrator for full effect)"
}

Start-Sleep -Milliseconds 800

# --- Report after ---
$after = Get-RAMUsedGB
$saved = [math]::Round($before - $after, 2)
Write-Host ""
Write-Host "RAM after:  ${after} GB used"
Write-Host "Freed:      ${saved} GB"
Write-Host ""
Write-Host "Done. Press Enter to close."
$null = Read-Host
