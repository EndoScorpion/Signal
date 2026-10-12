param([string]$Expert='Strong2010b_claude_g4b',[string]$Period='M15',[int]$Model=0,
      [string]$From='2021.03.19',[string]$To='2022.01.01',[int]$Spread=3,[int]$Commission=6)
if ((Test-Path 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE') -or (Test-Path 'C:\Users\endos\MT4_Backtest\PAUSE')) { Write-Host 'MT4 PAUSED (PAUSE file exists) - not starting.' -ForegroundColor Yellow; exit 6 }
$data = "$env:APPDATA\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415"
$origin = (Get-Content "$data\origin.txt" -Encoding Unicode -Raw).Trim()
$src = "C:\Users\endos\Signal_copy\$Expert.mq4"
$dst = "$data\MQL4\Experts\$Expert.mq4"
$ex4 = "$data\MQL4\Experts\$Expert.ex4"
$log = "$data\MQL4\compile_$Expert.log"
if (-not (Test-Path $src)) { Write-Host "Source missing: $src" -ForegroundColor Red; exit 1 }
Copy-Item $src $dst -Force
Start-Process (Join-Path $origin 'metaeditor.exe') -ArgumentList "/compile:`"$dst`"","/log:`"$log`"" -WindowStyle Minimized -Wait
if (-not (Test-Path $ex4) -or (Get-Item $ex4).LastWriteTime -lt (Get-Date).AddMinutes(-2)) {
  Write-Host "COMPILE FAILED" -ForegroundColor Red; Get-Content $log; exit 1 }
Write-Host "Compile OK" -ForegroundColor Green
& "C:\Users\endos\Signal\scripts\run_oos_gate_v4_12Oct2026.ps1" -Expert $Expert -Period $Period -Model $Model -From $From -To $To -Spread $Spread -Commission $Commission


