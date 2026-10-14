# Runs g5a-g5e: compile + gate, 6 pt commission, M1 every tick. Summary -> Signal\data\g5_summary_12Oct2026.txt
$out = 'C:\Users\endos\Signal\data\g5_summary_12Oct2026.txt'
$gate = 'C:\Users\endos\Signal\scripts\compile_and_gate_v1_12Oct2026.ps1'
foreach ($n in 'g5a','g5b','g5c','g5d','g5e') {
  Write-Host "=== $n ===" -ForegroundColor Cyan
  $r = & powershell -ExecutionPolicy Bypass -File $gate -Expert "Strong2010b_claude_$n" -Period M1 -Commission 6 2>&1 | Tee-Object -Variable raw
  $sum = $raw | Select-String 'Total trades|Win rate|PF estimate|Net PnL|Max closed|PASS|FAIL|COMPILE|RAM gate'
  "=== $n ===" | Add-Content $out
  $sum | ForEach-Object { $_.Line } | Add-Content $out
}
Write-Host "DONE. Summary: $out" -ForegroundColor Green
Get-Content $out
