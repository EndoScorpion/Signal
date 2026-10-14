# Keeps the MT4 terminal window restored (never minimized) while it runs.
# Silent mode: create the flag file to pause restoring; delete it to resume.
#   Silent ON : New-Item "$env:USERPROFILE\Signal\scripts\mt4_silent.flag" -ItemType File
#   Silent OFF: Remove-Item "$env:USERPROFILE\Signal\scripts\mt4_silent.flag"
# Stop the watcher: Remove-Item "$env:USERPROFILE\Signal\scripts\mt4_watch.stop" after creating it, or close its window.
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [StructLayout(LayoutKind.Sequential)] public struct LII { public uint cb; public uint t; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LII p);
  public static double IdleSec() { LII i = new LII(); i.cb = (uint)Marshal.SizeOf(i); GetLastInputInfo(ref i); return (Environment.TickCount - (int)i.t) / 1000.0; }
}
'@
$dir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$silent = Join-Path $dir 'mt4_silent.flag'
$stop   = Join-Path $dir 'mt4_watch.stop'
Remove-Item -LiteralPath $stop -ErrorAction SilentlyContinue
while (-not (Test-Path -LiteralPath $stop)) {
  # Never act while you are typing/using the mouse (idle < 4s); restore without taking focus.
  if (-not (Test-Path -LiteralPath $silent) -and [W]::IdleSec() -ge 4) {
    foreach ($p in Get-Process -Name terminal -ErrorAction SilentlyContinue) {
      $h = $p.MainWindowHandle
      if ($h -ne [IntPtr]::Zero -and [W]::IsIconic($h)) { [void][W]::ShowWindow($h, 4) }  # SW_SHOWNOACTIVATE
    }
  }
  Start-Sleep -Seconds 2
}
