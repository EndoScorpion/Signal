# Desktop shortcut target: one-screen status of the testing, works offline. Window stays open until you press a key.
$sig = 'C:\Users\endos\Signal'
$free = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
Write-Host "=== Test status $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" -ForegroundColor Cyan
Write-Host "Free RAM: $free MB (tests start at 1024, stop under 400)"
Write-Host ("Paused: " + (Test-Path 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE'))
Write-Host ("Driver running: " + [bool](Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like '*evolve.ps1*' }))
Write-Host ("Loop running:   " + [bool](Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*auto_loop*' }))
Write-Host ("Tester running: " + [bool](Get-Process terminal -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*mt4_tester*' }))
$pj = "$sig\data\loop_progress.json"
if (Test-Path $pj) { $p = Get-Content $pj -Raw | ConvertFrom-Json; Write-Host "Now testing: $($p.candidate) year $($p.year) ($($p.done) of $($p.total) candidates done in this pass)" }
Write-Host "`nDriver log (last 6):" -ForegroundColor Cyan; Get-Content "$sig\data\evolve_log.txt" -Tail 6
Write-Host "`nBest results so far (pts over unseen years):" -ForegroundColor Cyan
python -I -c "import json;T=json.load(open(r'C:\Users\endos\Signal\data\loop_state.json'))['tested'];T.update(json.load(open(r'C:\Users\endos\Signal\data\loop_state_clean.json'))['tested']);r=[(round(sum(v['profit'] for v in t.get('oos',{}).values())/0.16),sum(v['trades'] for v in t.get('oos',{}).values()),len(t.get('oos',{})),n) for n,t in T.items()];[print(f'{a:>8} pts {b:>4} trades {c} yrs  {n}') for a,b,c,n in sorted(r,reverse=True)[:8]]"
Write-Host "`nPress any key to close." ; [void][Console]::ReadKey($true)
