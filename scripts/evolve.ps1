# Safe self-improvement driver: breeder -> clean test pass -> trackers -> log, repeated with hard limits.
# Safety: single instance, one test at a time (waits for any auto_loop), RAM trim + 1.0 GB gate before each pass, honors MT4_PAUSE files,
# stop file Signal\evolve.stop, max passes and max hours, never kills any process, only adds files (breeder/loop never overwrite ancestors).
# Backtest only, never live approval. Log: Signal\data\evolve_log.txt
param([int]$MaxPasses = 4, [double]$MaxHours = 8, [int]$PerPass = 12)
$me = New-Object Threading.Mutex($false, 'Global\evolve_single'); if (-not $me.WaitOne(0)) { exit }
$sig = 'C:\Users\endos\Signal'; $log = "$sig\data\evolve_log.txt"; $stop = "$sig\evolve.stop"
$pauses = 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE', 'C:\Users\endos\MT4_Backtest\PAUSE'
Remove-Item -LiteralPath $stop -ErrorAction SilentlyContinue
function Log($m) { Add-Content -LiteralPath $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function LoopRunning { [bool](Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*auto_loop.py*' }) }
function FreeMB { [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024) }
. "$sig\scripts\phone_notify.ps1"                 # one-way status messages to the phone via ntfy (status text only)
function Halt { (Test-Path -LiteralPath $stop) -or [bool]($pauses | Where-Object { Test-Path $_ }) }
$t0 = Get-Date; $pass = 0; Log "evolve started (MaxPasses=$MaxPasses MaxHours=$MaxHours PerPass=$PerPass)"
Set-Location $sig
while ($pass -lt $MaxPasses) {
  if (Halt) { Log 'stop or PAUSE file present, exiting'; break }
  if (((Get-Date) - $t0).TotalHours -ge $MaxHours) { Log 'max hours reached, exiting'; break }
  Start-Sleep -Seconds 60                       # grace so a chained handoff can start before we look
  $w = 0; while (LoopRunning) { Start-Sleep -Seconds 30; $w++; if ($w -gt 240) { Log 'loop busy over 2 h, exiting'; exit } }
  if (Halt) { Log 'stop or PAUSE file present, exiting'; break }
  powershell -NoProfile -File "$sig\scripts\ram_trim.ps1" | Out-Null
  if ((FreeMB) -lt 1024) { Log ("RAM gate closed ({0} MB), waiting 10 min" -f (FreeMB)); Start-Sleep -Seconds 600; if ((FreeMB) -lt 1024) { Log 'RAM still low, exiting'; break } }
  if (Halt) { Log 'stop or PAUSE file present, exiting'; break }
  $pass++; Log "pass $pass start"
  if ((FreeMB) -lt 1500 -and -not (Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like '*ram_guard_v3*' })) {   # guard only when RAM is tight and none is running
    $psi = New-Object Diagnostics.ProcessStartInfo 'powershell.exe'; $psi.Arguments = "-NoProfile -File `"$sig\scripts\ram_guard_v3.ps1`""; $psi.CreateNoWindow = $false; $psi.UseShellExecute = $false; [Diagnostics.Process]::Start($psi) | Out-Null; Log 'ram guard started (RAM tight)' }
  $b = python -I data\breeder.py 2>&1 | Select-Object -First 2; Log ("breeder: " + ($b -join ' | '))
  $b2 = python -I data\breeder2.py --max 8 2>&1 | Select-Object -First 1; Log ("breeder2: " + ($b2 -join ' | '))
  $th = python -E -P data\theorize.py --max 6 2>&1 | Select-Object -Last 1; Log ("theorize (loss protection): " + ($th -join ' | '))
  $sv = python -E -P data\salvage.py --max 8 2>&1 | Select-Object -Last 1; Log ("salvage (improve/protect/combine before dropping): " + ($sv -join ' | '))
  python -I data\auto_loop.py --clean --rounds 1 --max-cands $PerPass | Out-Null
  python -I data\market_patterns.py | Out-Null; python -I data\smooth_vs_vol.py | Out-Null
  $r = python -I data\improvement_report.py 2>&1 | Select-String 'promoted|failed screens'; Log ("pass $pass done: " + ($r -join ' | '))
  $best = python -I -c "import json;T=json.load(open(r'$sig\data\loop_state.json'))['tested'];T.update(json.load(open(r'$sig\data\loop_state_clean.json'))['tested']);r=sorted(((round(sum(v['profit'] for v in t['oos'].values())/0.16),sum(v['trades'] for v in t['oos'].values()),n) for n,t in T.items() if t.get('oos') and sum(v['trades'] for v in t['oos'].values())>=100),reverse=True)[0];print(r[2],r[0],'pts',r[1],'trades')" 2>&1 | Select-Object -Last 1
  Send-Phone "Pass $pass of $MaxPasses done. Best so far: $best (backtest only)." -Title 'EA loop'
  $pa = python -E -P data\param_audit.py 2>&1 | Select-Object -Last 1; Log ("param audit: " + ($pa -join ' | '))
  if ($pa -match '[1-9]\d* candidates with intended') { Send-Phone ("PARAM MISMATCH: " + ($pa -join ' ')) -Title 'EA param audit' -Priority high -Max 600 }
  $mi = python -E -P data\meta_improve.py 2>&1 | Select-Object -Last 1; Log ("watchdog: " + ($mi -join ' | '))
}
Log 'evolve finished'
Send-Phone 'Driver finished or stopped. Use Resume Tests on the laptop to continue.' -Title 'EA loop'
