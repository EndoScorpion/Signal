# Live process monitor. Default = LOG ONLY (never changes anything).
#   -Apply  : when free RAM < $LowMB, put SAFE-LIST background apps into Efficiency mode (EcoQoS) + BelowNormal priority. Reversible.
# Never touches: claude (any), terminal, metatester*, powershell, pwsh, explorer, dwm, MsMpEng, system. No suspend. No end-task.
# Stop: create mt4_procwatch.stop in this folder.  Log: proc_watch.log
param([switch]$Apply, [int]$LowMB = 1000, [int]$IntervalSec = 10, [int]$MaxCycles = 0)
Add-Type @'
using System; using System.Runtime.InteropServices;
public class Eco {
  [StructLayout(LayoutKind.Sequential)] public struct PTS { public uint Version; public uint ControlMask; public uint StateMask; }
  [DllImport("kernel32.dll", SetLastError=true)] static extern bool SetProcessInformation(IntPtr h, int cls, ref PTS p, int size);
  public static bool Set(IntPtr h, bool on) { PTS p = new PTS(); p.Version = 1; p.ControlMask = 1; p.StateMask = on ? 1u : 0u; return SetProcessInformation(h, 4, ref p, 12); }
}
'@
$dir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$stop = Join-Path $dir 'mt4_procwatch.stop'; $log = Join-Path $dir 'proc_watch.log'
$never = 'claude','cowork-svc','terminal','metatester','metatester64','metaeditor','powershell','pwsh','explorer','dwm','MsMpEng','csrss','wininit','winlogon','services','lsass','svchost','System','Registry','smss','QuotesDownloader','RuntimeBroker','sihost','ctfmon','taskmgr'
$safe  = 'PowerToys','Greenshot','RadeonSoftware','WhatsApp','SearchIndexer','uihost','servicehost','OneDrive','Teams','Widgets','PhoneExperienceHost','YourPhone'
function Log($m) { Add-Content -LiteralPath $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
Remove-Item -LiteralPath $stop -ErrorAction SilentlyContinue
Log ("watch started (Apply={0}, LowMB={1})" -f $Apply, $LowMB); $n = 0; $touched = @{}
while (-not (Test-Path -LiteralPath $stop)) {
  $os = Get-CimInstance Win32_OperatingSystem
  $freeMB = [int]($os.FreePhysicalMemory / 1024); $totMB = [int]($os.TotalVisibleMemorySize / 1024)
  $cpu = (Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average
  $top = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 8 | ForEach-Object { "{0}({1})={2}MB" -f $_.ProcessName, $_.Id, [int]($_.WorkingSet64/1MB) }
  Log ("free={0}/{1}MB cpu={2}% top: {3}" -f $freeMB, $totMB, $cpu, ($top -join ' '))
  if ($freeMB -lt $LowMB) {
    $cands = Get-Process | Where-Object { ($safe -contains $_.ProcessName) -and ($never -notcontains $_.ProcessName) -and $_.WorkingSet64 -gt 30MB }
    foreach ($p in $cands) {
      if ($Apply) {
        if (-not $touched.ContainsKey($p.Id)) {
          $ok = $false; try { $ok = [Eco]::Set($p.Handle, $true); $p.PriorityClass = 'BelowNormal' } catch {}
          $touched[$p.Id] = $true; Log ("EFFICIENCY {0}({1}) {2}MB ok={3}" -f $p.ProcessName, $p.Id, [int]($p.WorkingSet64/1MB), $ok)
        }
      } else { Log ("DRYRUN would set efficiency: {0}({1}) {2}MB" -f $p.ProcessName, $p.Id, [int]($p.WorkingSet64/1MB)) }
    }
  }
  $n++; if ($MaxCycles -gt 0 -and $n -ge $MaxCycles) { break }
  Start-Sleep -Seconds $IntervalSec
}
Log 'watch stopped'
