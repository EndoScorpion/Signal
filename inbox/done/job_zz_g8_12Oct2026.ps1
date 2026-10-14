$out='C:\Users\endos\Signal\data\g8_summary_12Oct2026.txt'
& powershell -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1 -Expert Strong2010b_claude_g8a -Period M1 -Commission 6 2>&1 | Tee-Object -Variable raw | Out-Null
"=== g8a 5k 500lev 6pt ===" | Out-File $out -Append -Encoding utf8
$raw | Select-String 'Total trades|Win rate|PF estimate|Net PnL|Max closed|PASS|FAIL|COMPILE|RAM gate' | % { $_.Line } | Out-File $out -Append -Encoding utf8
"DONE"
