# Hub watcher: polls every 3 min, calls run_queue.ps1 (which enforces lock + >=1 GB RAM gate,
# one job per call). Exits when queue is empty or after 8 h. Stop early: delete watch_queue.stop
$root = "C:\Users\endos\MT4_Backtest"
$stop = "$root\watch_queue.stop"
$end  = (Get-Date).AddHours(8)
while ((Get-Date) -lt $end -and -not (Test-Path $stop)) {
    $out = & powershell -NoProfile -File "$root\run_queue.ps1" 2>&1 | Out-String
    "$(Get-Date -f 'MM-dd HH:mm:ss') $($out.Trim())" | Add-Content "$root\watch_queue.log"
    if ($out -match '^EMPTY') { break }
    Start-Sleep -Seconds 180
}
