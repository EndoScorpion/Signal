# sync_status.ps1 - consolidates every session's work on this PC into ONE file: hst_out\STATUS_ALL.txt
# Runs in a loop (every 10 min) until hst_out\sync.stop exists. Read-only on all sources; only writes STATUS_ALL.txt.
# Any Claude session / thread on this PC: read STATUS_ALL.txt first, then add your notes to winners\TEST_LOG.txt / WINNERS_REGISTRY.txt.
$H = 'C:\Users\endos\Desktop\hst_out'; $py = 'C:\Users\endos\AppData\Local\Python\bin\python.exe'
while (-not (Test-Path "$H\sync.stop")) {
  try {
    $o = [Collections.Generic.List[string]]::new()
    $o.Add("STATUS_ALL - consolidated view of all sessions on this PC. Auto-refreshed every 10 min by sync_status.ps1 (stop: create hst_out\sync.stop).")
    $o.Add("Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') local. Cost rule: 8 pts/trade (Nasif 21:35). Lot 0.01. Base = b22_thu.")
    $o.Add("")
    $o.Add("== CURRENT BEST (PROVEN) ==")
    $o.Add("Z-gate (ZMax 1.0) + Daily range filter (1.0 x D1 ATR5) on b22_thu. Set: winners\WIN_GEN1_ZGate_DailyRange_b31.set (EA Strong2010b_claude_b31).")
    $o.Add("")
    $o.Add("== KEY SCORES (pts after 8-pt cost) ==")
    $sc = & $py -I "$H\stat_corr\score_b23.py" "b22_thu_20*" "b22_thu_2526" "b31_zr_20*" "b31_zr_2526" "b22_thu_s5_*" "b31_zr_s5_*" 2>&1
    $sc | % { $o.Add([string]$_) }
    $o.Add("")
    $o.Add("== QUEUES (last line of each log, newest first) ==")
    Get-ChildItem "$H\*.log" | ? { $_.Name -match '^(batch|master|gen|pcq|sync)' } | sort LastWriteTime -Desc | select -First 12 | % {
      $last = (Get-Content $_.FullName -Tail 1 -EA 0); $o.Add(("{0,-14} {1:HH:mm}  {2}" -f $_.Name, $_.LastWriteTime, $last)) }
    $run = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | ? { $_.CommandLine -match 'run_tester' } | % { [regex]::Match($_.CommandLine,'-Expert \S+ -SetFile \S+').Value }
    $o.Add("Running now: " + ($(if ($run) { $run -join ' | ' } else { 'nothing' })))
    $o.Add("")
    $o.Add("== LATEST TESTS (newest 25 reports, all sessions) ==")
    $tags = Get-ChildItem "$H\*.htm" | sort LastWriteTime -Desc | select -First 25 | % { $_.BaseName }
    if ($tags) { (& $py -I "$H\stat_corr\score_b23.py" @tags 2>&1) | % { $o.Add([string]$_) } }
    $o.Add("")
    $o.Add("== SHARED FILES ==")
    foreach ($f in 'winners\WINNERS_REGISTRY.txt','winners\TEST_LOG.txt','winners\PC_TEST_QUEUE.txt','WIN_LOGIC_LOG.txt','B23_B24_RESUME.txt','B32_RESULTS.txt') {
      $p = "$H\$f"; if (Test-Path $p) { $o.Add(("{0,-30} updated {1:HH:mm}" -f $f, (Get-Item $p).LastWriteTime)) } }
    $o.Add("")
    $o.Add("== WINNERS REGISTRY (tail) ==")
    Get-Content "$H\winners\WINNERS_REGISTRY.txt" -Tail 12 -EA 0 | % { $o.Add($_) }
    $tmp = "$H\STATUS_ALL.tmp"; Set-Content $tmp $o -Encoding UTF8; Move-Item $tmp "$H\STATUS_ALL.txt" -Force
  } catch { Add-Content "$H\sync.log" ("{0:HH:mm:ss} sync error: {1}" -f (Get-Date), $_.Exception.Message) }
  Start-Sleep -Seconds 600
}
