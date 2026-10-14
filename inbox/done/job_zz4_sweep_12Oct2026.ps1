$hst="C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\history\FXOpenEU-ECN Live Server\EURUSD1.hst"
$fs=[IO.File]::OpenRead($hst); $null=$fs.Seek(148,'Begin'); $b=New-Object byte[] 8; $null=$fs.Read($b,0,8); $fs.Close()
$first=[DateTimeOffset]::FromUnixTimeSeconds([BitConverter]::ToInt64($b,0)).UtcDateTime
$p='C:\Users\endos\Signal\data\sweep_progress_12Oct2026.txt'
"First bar: $first" | Out-File $p -Append -Encoding utf8
$g='C:\Users\endos\Signal\scripts\compile_and_gate_v2_12Oct2026.ps1'
$y0=[Math]::Max($first.Year,2015)
$wins=@()
foreach($y in $y0..2026){ if($y -eq 2021){continue}; $to= if($y -eq 2026){'2026.10.12'}else{"$($y+1).01.01"}; $wins += ,@("$y.01.01",$to) }
foreach($w in $wins){
 foreach($n in 'g4b','g6b','g7n','g5c'){
  $f=$w[0].Replace('.',''); $t=$w[1].Replace('.','')
  $rep="C:\Users\endos\Signal\data\Strong2010b_claude_${n}_M1_${f}-${t}_sp3.htm"
  if(Test-Path $rep){ continue }
  & powershell -ExecutionPolicy Bypass -File $g -Expert "Strong2010b_claude_$n" -Period M1 -From $w[0] -To $w[1] -Commission 5 2>&1 | Out-Null
  "$n $($w[0])-$($w[1]) done $(Get-Date)" | Out-File $p -Append -Encoding utf8
 }
}
"SWEEP DONE $(Get-Date)" | Out-File $p -Append -Encoding utf8
