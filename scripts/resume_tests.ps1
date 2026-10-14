# Desktop shortcut target: resume the self-improvement tests from scratch after a reboot or lost session. Works offline.
# Lifts the pause (you clicked it), clears stale locks only when nothing is running, trims RAM, starts the safe driver hidden.
$sig = 'C:\Users\endos\Signal'
Write-Host 'Resuming tests...'
Remove-Item 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE', 'C:\Users\endos\MT4_Backtest\PAUSE', "$sig\evolve.stop" -ErrorAction SilentlyContinue
$running = [bool](Get-Process terminal -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*mt4_tester*' }) -or
          [bool](Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*auto_loop*' })
if (-not $running) { Get-ChildItem 'C:\Users\endos\Desktop\hst_out' -Recurse -Filter *.lock -ErrorAction SilentlyContinue | Remove-Item -ErrorAction SilentlyContinue }
powershell -NoProfile -File "$sig\scripts\ram_trim.ps1"
$ev = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like '*evolve.ps1*' }
if ($ev) { Write-Host 'The driver is already running, nothing to start.' }
else {
  Start-Process powershell -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-File', "$sig\scripts\evolve.ps1", '-MaxPasses', '6', '-MaxHours', '14', '-PerPass', '25'
  Write-Host 'Driver started (hidden). Use Test Status to watch it.'
}
Start-Sleep -Seconds 6
