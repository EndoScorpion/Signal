# ram_guard_v1_12Oct2026.ps1 - live RAM monitor with tiered, reversible relief.
# DEFAULT = DRY RUN (logs what it WOULD do). Add -Apply to act.
#   Tier 1 (free < Target)      : Efficiency mode (EcoQoS + Idle priority) on candidate processes
#   Tier 2 (free < Target-300)  : Pause (suspend) idle candidates      [needs -AllowSuspend]
#   Tier 3 (free < Target-600)  : Graceful close, then end, candidates [needs -AllowEnd]
# Suspended processes are resumed automatically once free RAM > Target+300 and on exit.
# NEVER touched: anything not in the candidate lists, the foreground-window process,
# this script, and anything on the protected list (Claude, remote-control, MT4, shells, system).
param(
    [int]$TargetFreeMB = 1500,
    [int]$IntervalSec  = 15,
    [switch]$Apply,
    [switch]$AllowSuspend,
    [switch]$AllowEnd,
    [switch]$Once,
    [string[]]$OnlyName,   # test aid: restrict every tier to these process names
    [string]$Log = 'C:\Users\endos\Signal\data\ram_guard_12Oct2026.log'
)
$ErrorActionPreference = 'SilentlyContinue'

# ---- lists (edit freely) ----
$EcoList     = 'chrome','msedge','msedgewebview2','PhoneExperienceHost','YourPhone','OneDrive','ms-teams','Teams','Discord','Spotify','Widgets','SearchHost','Taskmgr'
$SuspendList = 'PhoneExperienceHost','YourPhone','OneDrive','Spotify','Discord'
$EndList     = 'chrome','PhoneExperienceHost','YourPhone'
$Protected   = '^(System|Idle|Registry|smss|csrss|wininit|winlogon|services|lsass|svchost|dwm|explorer|MsMpEng|fontdrvhost|sihost|ctfmon|RuntimeBroker|powershell|pwsh|bash|sh|node|python|git|conhost|OpenConsole|cmd|WindowsTerminal|claude|cowork-svc|terminal|metatester|metaeditor|TickTrader.*|mt4.*)$'

Add-Type @"
using System; using System.Runtime.InteropServices;
public static class RG {
  [StructLayout(LayoutKind.Sequential)] public struct PPT { public uint Version; public uint ControlMask; public uint StateMask; }
  [DllImport("kernel32.dll", SetLastError=true)] static extern bool SetProcessInformation(IntPtr h, int cls, ref PPT i, int size);
  [DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr h);
  [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr h);
  [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  public static bool Eco(IntPtr h, bool on){ var p=new PPT{Version=1,ControlMask=1,StateMask=on?1u:0u}; return SetProcessInformation(h,4,ref p,Marshal.SizeOf(typeof(PPT))); }
  public static uint FgPid(){ uint pid; GetWindowThreadProcessId(GetForegroundWindow(), out pid); return pid; }
}
"@

$mode = if ($Apply) { 'APPLY' } else { 'DRY-RUN' }
function Say($m){ $l = "{0} [{1}] {2}" -f (Get-Date -Format 'HH:mm:ss'), $mode, $m; Write-Host $l; Add-Content -Path $Log -Value $l }
function FreeMB { [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024) }

$mutex = New-Object System.Threading.Mutex($false, 'Global\ram_guard_v1')
if (-not $mutex.WaitOne(0)) { Write-Host 'ram_guard already running.'; exit 2 }

$ecoDone   = @{}   # pid -> $true
$suspended = @{}   # pid -> name
function Resume-All($why){
  foreach ($id in @($suspended.Keys)) {
    $p = Get-Process -Id $id; if ($p) { if ($Apply) { [void][RG]::NtResumeProcess($p.Handle) }; Say "RESUME $($suspended[$id]) pid $id ($why)" }
    $suspended.Remove($id)
  }
}
function Candidates($names){
  $fg = [RG]::FgPid()
  Get-Process | Where-Object { $names -contains $_.ProcessName -and (-not $OnlyName -or $OnlyName -contains $_.ProcessName) -and $_.ProcessName -notmatch $Protected -and $_.Id -ne $PID -and $_.Id -ne $fg }
}

try {
  Say "start target=${TargetFreeMB}MB interval=${IntervalSec}s suspend=$AllowSuspend end=$AllowEnd"
  do {
    $free = FreeMB
    if ($free -ge ($TargetFreeMB + 300)) { Resume-All "free ${free}MB recovered" }
    if ($free -lt $TargetFreeMB) {
      Say "LOW free=${free}MB"
      foreach ($p in Candidates $EcoList) {
        if ($ecoDone.ContainsKey($p.Id)) { continue }
        if ($Apply) { [void][RG]::Eco($p.Handle,$true); $p.PriorityClass = 'Idle' }
        Say "ECO $($p.ProcessName) pid $($p.Id) $([int]($p.WorkingSet64/1MB))MB"; $ecoDone[$p.Id] = $true
      }
    }
    if ($AllowSuspend -and $free -lt ($TargetFreeMB - 300)) {
      foreach ($p in Candidates $SuspendList) {
        if ($suspended.ContainsKey($p.Id)) { continue }
        $c1 = $p.TotalProcessorTime.TotalMilliseconds; Start-Sleep -Milliseconds 500; $p.Refresh()
        if (($p.TotalProcessorTime.TotalMilliseconds - $c1) -gt 50) { Say "SKIP-PAUSE $($p.ProcessName) pid $($p.Id) busy"; continue }
        if ($Apply) { [void][RG]::NtSuspendProcess($p.Handle) }
        Say "PAUSE $($p.ProcessName) pid $($p.Id)"; $suspended[$p.Id] = $p.ProcessName
      }
    }
    if ($AllowEnd -and $free -lt ($TargetFreeMB - 600)) {
      foreach ($p in Candidates $EndList) {
        Say "END $($p.ProcessName) pid $($p.Id) $([int]($p.WorkingSet64/1MB))MB (graceful first)"
        if ($Apply) { [void]$p.CloseMainWindow(); if (-not $p.WaitForExit(5000)) { Stop-Process -Id $p.Id -Force } }
      }
    }
    if (-not $Once) { Start-Sleep -Seconds $IntervalSec }
  } while (-not $Once)
  if ($Once) { Say "tick done free=$(FreeMB)MB" }
}
finally { Resume-All 'exit'; $mutex.ReleaseMutex() }
