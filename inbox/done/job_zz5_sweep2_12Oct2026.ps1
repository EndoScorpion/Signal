# Sweep v2: waits until MT4 is closed, runs each missing window, retries up to 3x if no report appears.
$p='C:\Users\endos\Signal\data\sweep2_progress_12Oct2026.txt'
$g='C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1'
$wins=@(@('2017.01.01','2018.01.01'),@('2018.01.01','2019.01.01'),@('2022.01.01','2023.01.01'),@('2023.01.01','2024.01.01'),@('2024.01.01','2025.01.01'),@('2025.01.01','2026.01.01'),@('2026.01.01','2026.10.12'))
foreach($w in $wins){ foreach($n in 'g4b','g6b','g7n'){
  $f=$w[0].Replace('.',''); $t=$w[1].Replace('.','')
  $rep="C:\Users\endos\Signal\data\Strong2010b_claude_${n}_M1_${f}-${t}_sp3.htm"
  for($try=1; $try -le 3 -and -not (Test-Path $rep); $try++){
    $wait=0; while((Get-Process terminal -ErrorAction SilentlyContinue) -and $wait -lt 600){ Start-Sleep 10; $wait+=10 }
    & powershell -ExecutionPolicy Bypass -File $g -Expert "Strong2010b_claude_$n" -Period M1 -From $w[0] -To $w[1] -Commission 5 2>&1 | Out-Null
    Start-Sleep 3
  }
  "$n $($w[0])-$($w[1]) report=$(Test-Path $rep) $(Get-Date)" | Out-File $p -Append -Encoding utf8
}}
"SWEEP2 DONE $(Get-Date)" | Out-File $p -Append -Encoding utf8
