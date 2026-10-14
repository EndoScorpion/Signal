# Minimizes (no focus steal) and taskbar-flashes only helper PowerShell windows started by our test tooling.
# Matches command lines containing: run_tester, ram_trim, ram_gate, ram_guard, evolve, auto_loop, Watch-Processes, test_tracker.
# Never touches your own PowerShell windows. Exits after $IdleExit idle checks (no tester/loop/evolve running) or when Signal\winmin.stop exists.
param([int]$IntervalSec = 1, [int]$IdleExit = 600)
Add-Type @'
using System; using System.Runtime.InteropServices;
public class WM {
  [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [StructLayout(LayoutKind.Sequential)] public struct FLASHWINFO { public uint cbSize; public IntPtr hwnd; public uint dwFlags; public uint uCount; public uint dwTimeout; }
  [DllImport("user32.dll")] public static extern bool FlashWindowEx(ref FLASHWINFO f);
  public static void Flash(IntPtr h) { FLASHWINFO f = new FLASHWINFO(); f.cbSize = (uint)Marshal.SizeOf(f); f.hwnd = h; f.dwFlags = 0x3 | 0xC; f.uCount = 3; f.dwTimeout = 0; FlashWindowEx(ref f); }
}
'@
$stop = 'C:\Users\endos\Signal\winmin.stop'; Remove-Item -LiteralPath $stop -ErrorAction SilentlyContinue
$pat = 'run_tester|ram_trim|ram_gate|ram_guard|evolve|auto_loop|Watch-Processes|test_tracker'
$seen = @{}; $idle = 0
while (-not (Test-Path -LiteralPath $stop)) {
  foreach ($p in Get-Process powershell, pwsh, conhost -ErrorAction SilentlyContinue) {
    if ($p.MainWindowHandle -eq 0 -or $seen.ContainsKey($p.Id)) { continue }
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)" -ErrorAction SilentlyContinue).CommandLine
    if ($c -and $c -match $pat -and [WM]::IsWindowVisible($p.MainWindowHandle) -and -not [WM]::IsIconic($p.MainWindowHandle)) {
      [WM]::ShowWindowAsync($p.MainWindowHandle, 7) | Out-Null; [WM]::Flash($p.MainWindowHandle); $seen[$p.Id] = $true } }
  $busy = [bool](Get-Process terminal -ErrorAction SilentlyContinue) -or [bool](Get-CimInstance Win32_Process -Filter "Name='python.exe' or Name='powershell.exe'" | Where-Object { $_.CommandLine -match 'auto_loop|evolve' })
  if ($busy) { $idle = 0 } else { $idle++; if ($idle -ge $IdleExit) { break } }
  Start-Sleep -Seconds $IntervalSec
}
