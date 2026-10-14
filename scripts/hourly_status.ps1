# Short hourly status to the phone via ntfy (status text only), including the self-improvement ETF. Created for 2026-10-14 only; its scheduled task expires at midnight.
. 'C:\Users\endos\Signal\scripts\phone_notify.ps1'
$sig = 'C:\Users\endos\Signal'
$free = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
$drv = [bool](Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like '*evolve.ps1*' })
$loop = [bool](Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*auto_loop*' })
$paused = Test-Path 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE'
$now = ''; $pj = "$sig\data\loop_progress.json"
if (Test-Path $pj) { $p = Get-Content $pj -Raw | ConvertFrom-Json; $now = "testing $($p.candidate) $($p.year) ($($p.done)/$($p.total))" }
$best = python -E -P -c "import json;T=json.load(open(r'$sig\data\loop_state.json'))['tested'];T.update(json.load(open(r'$sig\data\loop_state_clean.json'))['tested']);r=sorted(((round(sum(v['profit'] for v in t['oos'].values())/0.16),sum(v['trades'] for v in t['oos'].values()),n) for n,t in T.items() if t.get('oos') and sum(v['trades'] for v in t['oos'].values())>=100),reverse=True)[0];print(f'best {r[2]} {r[0]:+d} pts/{r[1]} tr')" 2>&1 | Select-Object -Last 1
$etf = python -E -P "$sig\data\etf.py" 2>&1 | Select-Object -Last 1
python -E -P "$sig\data\meta_improve.py" 2>&1 | Out-Null   # watchdog: alerts and auto-explore when self-improvement is stuck or broken
$rec = python -E -P "$sig\data\recommend.py" 2>&1 | Select-Object -Last 1
$msg = "{0} RAM {1} MB, driver {2}, loop {3}, paused {4}. {5}. {6}. {7} NEXT: {8} (backtest only)" -f (Get-Date -Format 'HH:mm'), $free, $(if ($drv) { 'up' } else { 'DOWN' }), $(if ($loop) { 'running' } else { 'idle' }), $(if ($paused) { 'yes' } else { 'no' }), $now, $best, $etf, $rec
Send-Phone $msg -Title 'EA hourly' -Priority $(if (-not $drv -and -not $paused) { 'high' } else { 'default' }) -Max 1800
