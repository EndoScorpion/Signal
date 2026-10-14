if (Test-Path 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE') { Write-Host 'MT4 PAUSED (hst_out\MT4_PAUSE exists) - not starting.' -ForegroundColor Yellow; exit 6 }
$out = 'C:\Users\endos\Signal\data\g8_summary_12Oct2026.txt'
$gate = 'C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1'
$jobs = @(
 @{N='g7c';L='g7c ADX22 base';A=@()},
 @{N='g7d';L='g7d ADX26 base';A=@()},
 @{N='g7a';L='g7a ADX24 spread6';A=@('-Spread','6')},
 @{N='g7a';L='g7a ADX24 OOS 2022.01.01-2022.06.01';A=@('-From','2022.01.01','-To','2022.06.01')}
)
foreach ($j in $jobs) {
  "=== $($j.L) ===" | Add-Content $out
  $raw = & powershell -ExecutionPolicy Bypass -File $gate -Expert "Strong2010b_claude_$($j.N)" -Period M1 -Commission 6 @($j.A) 2>&1
  $raw | Select-String 'Total trades|Win rate|PF estimate|Net PnL|Max closed|PASS|FAIL|COMPILE|RAM gate|rror|missing|No data' | ForEach-Object { $_.Line } | Add-Content $out
}
"DONE" | Add-Content $out
