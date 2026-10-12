# Keeps Claude processes in Efficiency mode (EcoQoS) - same as Task Manager's Efficiency mode button. Reversible; ends with the process.
# Touches ONLY: claude, cowork-svc. Does not change priority, suspend or end anything.
# Stop: create mt4_eco.stop in this folder.  Log: eco_claude.log (only changes are logged).
Add-Type @'
using System; using System.Runtime.InteropServices;
public class Eco2 {
  [StructLayout(LayoutKind.Sequential)] public struct PTS { public uint Version; public uint ControlMask; public uint StateMask; }
  [DllImport("kernel32.dll", SetLastError=true)] static extern bool SetProcessInformation(IntPtr h, int cls, ref PTS p, int size);
  public static bool On(IntPtr h) { PTS p = new PTS(); p.Version = 1; p.ControlMask = 1; p.StateMask = 1; return SetProcessInformation(h, 4, ref p, 12); }
}
'@
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$stop = Join-Path $dir 'mt4_eco.stop'; $log = Join-Path $dir 'eco_claude.log'
Remove-Item -LiteralPath $stop -ErrorAction SilentlyContinue
$done = @{}
Add-Content -LiteralPath $log -Value ("{0} eco watcher started" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
while (-not (Test-Path -LiteralPath $stop)) {
  $live = @{}
  foreach ($p in Get-Process -Name claude,cowork-svc -ErrorAction SilentlyContinue) {
    $live[$p.Id] = $true
    if (-not $done.ContainsKey($p.Id)) {
      $ok = $false; try { $ok = [Eco2]::On($p.Handle) } catch {}
      $done[$p.Id] = $true
      Add-Content -LiteralPath $log -Value ("{0} eco {1}({2}) ok={3}" -f (Get-Date -Format 'HH:mm:ss'), $p.ProcessName, $p.Id, $ok)
    }
  }
  foreach ($k in @($done.Keys)) { if (-not $live.ContainsKey($k)) { $done.Remove($k) } }
  Start-Sleep -Seconds 30
}
Add-Content -LiteralPath $log -Value ("{0} eco watcher stopped" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
