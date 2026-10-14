if (Test-Path 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE') { Write-Host 'MT4 PAUSED (hst_out\MT4_PAUSE exists) - not starting.' -ForegroundColor Yellow; exit 6 }
$out = 'C:\Users\endos\Signal\data\g7_summary_12Oct2026.txt'
$gate = 'C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1'
foreach ($n in 'g7a','g7b') {
  "=== $n ===" | Add-Content $out
  $raw = & powershell -ExecutionPolicy Bypass -File $gate -Expert "Strong2010b_claude_$n" -Period M1 -Commission 6 2>&1
  $raw | Select-String 'Total trades|Win rate|PF estimate|Net PnL|Max closed|PASS|FAIL|COMPILE|RAM gate' | ForEach-Object { $_.Line } | Add-Content $out
}
"DONE" | Add-Content $out
