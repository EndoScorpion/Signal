"Free RAM KB: " + (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
$out='C:\Users\endos\Signal\data\g6_summary_12Oct2026.txt'
foreach ($n in 'g6a','g6b','g6c','g6d','g6e') {
  & powershell -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1 -Expert "Strong2010b_claude_$n" -Period M1 -Commission 6 2>&1 | Tee-Object -Variable raw | Out-Null
  "=== $n ===" | Out-File $out -Append -Encoding utf8
  $raw | Select-String 'Total trades|Win rate|PF estimate|Net PnL|Max closed|PASS|FAIL|COMPILE|RAM gate' | % { $_.Line } | Out-File $out -Append -Encoding utf8
}
"ALL DONE"
