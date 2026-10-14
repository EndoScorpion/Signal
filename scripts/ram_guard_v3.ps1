# Trim-only RAM guard for test runs. Never closes or suspends any process. Single instance, gentle (cooldown, big processes only).
# While a tester or the auto loop is running: if free RAM < $LowMB, trim working sets of processes over 100 MB, at most once per $CooldownSec.
# Exits by itself after $IdleExit consecutive checks with no tester/loop running. Stop sooner: create Signal\ram_guard_v3.stop
param([int]$LowMB = 450, [int]$IntervalSec = 20, [int]$IdleExit = 6, [int]$CooldownSec = 120)
$me = New-Object Threading.Mutex($false, 'Global\ram_guard_v3_single'); if (-not $me.WaitOne(0)) { exit }
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("psapi.dll")] public static extern bool EmptyWorkingSet(IntPtr h);'
$log = 'C:\Users\endos\Signal\data\ram_guard_v3_log.txt'; $stop = 'C:\Users\endos\Signal\ram_guard_v3.stop'
Remove-Item -LiteralPath $stop -ErrorAction SilentlyContinue
function Log($m) { Add-Content -LiteralPath $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function Free { [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024) }
function Busy {
  [bool](Get-Process terminal -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*mt4_tester*' }) -or
  [bool](Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*auto_loop.py*' })
}
Log "guard started (LowMB=$LowMB cooldown=$CooldownSec s)"; $idle = 0; $lastTrim = [datetime]::MinValue
while (-not (Test-Path -LiteralPath $stop)) {
  if (Busy) {
    $idle = 0; $f = Free
    if ($f -lt $LowMB -and ((Get-Date) - $lastTrim).TotalSeconds -ge $CooldownSec) {
      $lastTrim = Get-Date; $c = 0
      foreach ($p in (Get-Process | Where-Object { $_.WorkingSet64 -gt 100MB })) { try { if ([W.P]::EmptyWorkingSet($p.Handle)) { $c++ } } catch {} }
      Log ("free {0} MB -> trimmed {1} procs -> free {2} MB" -f $f, $c, (Free))
    }
  } else { $idle++; if ($idle -ge $IdleExit) { Log 'no test running, guard exiting'; break } }
  Start-Sleep -Seconds $IntervalSec
}
Log 'guard stopped'
