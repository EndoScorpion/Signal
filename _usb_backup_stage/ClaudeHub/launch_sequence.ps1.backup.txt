# launch_sequence.ps1 - safe start order, one step at a time, each step RAM-gated.
#  1. wait until no MT4 backtest is running (lock free, terminal.exe gone)
#  2. RAM >= 1.5 GB  -> open ONE master terminal (non-admin, start_master.bat), unless one already runs
#  3. for each pending hub task: RAM >= 1.5 GB -> spawn ONE background clone (Sonnet 5.5, read-only)
#     after each spawn, wait 60 s for it to load before checking RAM again; stop at -MaxClones
# Never runs as admin, never kills anything, never launches MT4. Log: logs\launch_sequence.log
param([int]$MinFreeMB = 1500, [int]$MaxClones = 2, [int]$WaitMinutes = 180)

$Root = $PSScriptRoot
$log  = Join-Path $Root 'logs\launch_sequence.log'
function Log($m) { "$(Get-Date -f s) $m" | Tee-Object -Append $log }
function FreeMB { [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB) }

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole('Administrators')
if ($isAdmin) { Log 'refused: running as admin. Start it from a normal window.'; exit 1 }

# 1. wait for MT4
$deadline = (Get-Date).AddMinutes($WaitMinutes)
while (Get-Process terminal -EA SilentlyContinue | Where-Object { $_.Path -match '(?i)MT4_Backtest|FXOpen' }) {
  if ((Get-Date) -gt $deadline) { Log 'gave up: MT4 still running'; exit 1 }
  Start-Sleep 60
}
Log "MT4 idle. free=$(FreeMB) MB"

# 2. single master
$master = Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | Where-Object { $_.CommandLine -match '-n master|ClaudeHub' }
if ($master) { Log "master already running (PID $($master[0].ProcessId)) - not starting another" }
elseif ((FreeMB) -ge $MinFreeMB) {
  Start-Process (Join-Path $Root 'start_master.bat') -WorkingDirectory $Root
  Log "master started (free was $(FreeMB) MB)"; Start-Sleep 90
} else { Log "master NOT started: only $(FreeMB) MB free (< $MinFreeMB)"; exit 0 }

# 3. clones, one at a time, only for real pending tasks
$spawned = 0
foreach ($t in Get-ChildItem (Join-Path $Root 'queue\pending') -Filter *.json | Sort-Object Name) {
  if ($spawned -ge $MaxClones) { break }
  $free = FreeMB
  if ($free -lt $MinFreeMB) { Log "clones stopped: only $free MB free (< $MinFreeMB)"; break }
  $j = Get-Content $t.FullName -Raw | ConvertFrom-Json
  & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root 'hub.ps1') spawn $j.prompt -Name $j.id -Dir $j.dir -Tools $j.tools | ForEach-Object { Log $_ }
  Move-Item $t.FullName (Join-Path $Root 'queue\running') -Force
  $spawned++; Start-Sleep 60
}
Log "done: $spawned clone(s) spawned, free=$(FreeMB) MB"
