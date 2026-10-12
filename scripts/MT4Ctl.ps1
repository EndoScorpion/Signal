# Local, non-admin control for the MT4 helpers. No network listener, no remote shell.
# Usage: .\MT4Ctl.ps1 status | start | stop | silent-on | silent-off
param([Parameter(Mandatory)][ValidateSet('status','start','stop','silent-on','silent-off')][string]$Cmd)
$d = Split-Path -Parent $MyInvocation.MyCommand.Path
$scripts = 'Keep-MT4Visible','Guard-System'
function Running($n) { Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like "*$n.ps1*" -and $_.ProcessId -ne $PID } }
switch ($Cmd) {
  'start' { foreach ($n in $scripts) { if (-not (Running $n)) { Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$d\$n.ps1" } } }
  'stop'  { New-Item "$d\mt4_watch.stop","$d\mt4_guard.stop" -ItemType File -Force | Out-Null }
  'silent-on'  { New-Item "$d\mt4_silent.flag" -ItemType File -Force | Out-Null }
  'silent-off' { Remove-Item "$d\mt4_silent.flag" -ErrorAction SilentlyContinue }
}
if ($Cmd -eq 'start') { Start-Sleep 3 }
foreach ($n in $scripts) { "{0,-16} {1}" -f $n, $(if (Running $n) { 'running' } else { 'stopped' }) }
"silent mode     $(if (Test-Path "$d\mt4_silent.flag") { 'ON' } else { 'off' })"
if (Test-Path "$d\mt4_guard.log") { 'last log:'; Get-Content "$d\mt4_guard.log" -Tail 3 }
