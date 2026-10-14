$out='C:\Users\endos\Signal\data\oos_years_summary_12Oct2026.txt'
$g='C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1'
"Free RAM KB: " + (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
foreach ($y in @(@('2019.01.01','2020.01.01'),@('2020.01.01','2021.01.01'))) {
 foreach ($n in 'g4b','g6b','g7n') {
  & powershell -ExecutionPolicy Bypass -File $g -Expert "Strong2010b_claude_$n" -Period M1 -From $y[0] -To $y[1] -Commission 6 2>&1 | Tee-Object -Variable raw | Out-Null
  "=== $n $($y[0])-$($y[1]) ===" | Out-File $out -Append -Encoding utf8
  $raw | Select-String 'Total trades|Win rate|PF estimate|Net PnL|Max closed|PASS|FAIL|COMPILE|RAM gate|Commission/trade' | % { $_.Line } | Out-File $out -Append -Encoding utf8
 }
}
"ALL DONE"
