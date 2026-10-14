$g='C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1'
foreach ($n in 'g10a','g10b','g10c','g10d','g10e') {
  & powershell -ExecutionPolicy Bypass -File $g -Expert "Strong2010b_claude_$n" -Period M1 -Commission 5 2>&1 | Out-Null
  "$n done $(Get-Date)" | Out-File 'C:\Users\endos\Signal\data\g10_progress_12Oct2026.txt' -Append -Encoding utf8
}
