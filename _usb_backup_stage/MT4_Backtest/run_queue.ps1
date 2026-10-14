# Shared backtest queue runner. Each call runs at most ONE job ("chunk"), so any
# Claude session can call it safely: lock = no overlap, done.csv = no duplicates,
# RAM gate = no crash.
#   queue.txt line format:  EA_suffix|Period|From|To|Spread   e.g. b20legs_g1b|M15|2018.01.01|2019.01.01|2
#   usage: powershell -File run_queue.ps1          (run next pending job)
#          powershell -File run_queue.ps1 -Status  (show queue/lock/RAM, run nothing)
param([switch]$Status)
$root  = "C:\Users\endos\MT4_Backtest"
$lock  = "$root\.backtest.lock"
$queue = "$root\queue.txt"
$done  = "$root\done.csv"
$minGB = 1.0
if (-not (Test-Path $done)) { "job,result,report,started,minutes,freeGB" | Set-Content $done }

$freeGB  = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)
$doneIds = @(Import-Csv $done | Where-Object { $_.result -eq 'OK' } | ForEach-Object { $_.job })
$pending = @(Get-Content $queue -ErrorAction SilentlyContinue | Where-Object { $_ -match '\|' -and $_ -notmatch '^\s*#' } | ForEach-Object { $_.Trim() } | Where-Object { $doneIds -notcontains $_ } | Select-Object -Unique)
$held = $false
if (Test-Path $lock) { $held = [bool](Get-Process -Id ([int](Get-Content $lock -TotalCount 1)) -ErrorAction SilentlyContinue) }
$mt4 = Get-Process terminal -ErrorAction SilentlyContinue | Where-Object { $_.Path -match '(?i)FXOpen EU MT4|MT4_Backtest' }

if ($Status) {
    "Free RAM: $freeGB GB (need $minGB)"; "Lock held: $held"; "MT4 running: $([bool]$mt4)"
    "Pending ($($pending.Count)):"; $pending | ForEach-Object { "  $_" }; exit 0
}
if (Test-Path "$root\PAUSE") { "PAUSED: $root\PAUSE exists (user typing/RAM) - nothing started. Delete it to resume."; exit 0 }
if ($held -or $mt4)       { "BUSY: another backtest is running - try later"; exit 0 }
if (-not $pending)        { "EMPTY: no pending jobs"; exit 0 }
if ($freeGB -lt $minGB)   { "WAIT: only $freeGB GB free (need $minGB) - nothing started"; exit 0 }

$job = $pending[0]
$ea, $period, $from, $to, $spread, $deposit = $job -split '\|'
$name   = "Strong2010b_claude_$ea"
$report = "${name}_${period}_$($from -replace '\.','')-$($to -replace '\.','')_sp$spread"
if ($deposit) { $report += "_dep$deposit" }
"$PID`n$job started $(Get-Date -f 'yyyy-MM-dd HH:mm:ss')" | Set-Content $lock
try {
    # optional 6th column = initial deposit; MT4 reads it from tester\<EA>.ini <common>
    if ($deposit) {
        $tini = "$root\tester\$name.ini"
        if (Test-Path $tini) { (Get-Content $tini) -replace '^deposit=.*', "deposit=$deposit" | Set-Content -Encoding Unicode $tini }
        else { "<common>`r`npositions=2`r`ndeposit=$deposit`r`ncurrency=USD`r`nfitnes=0`r`ngenetic=1`r`n</common>" | Set-Content -Encoding Unicode $tini }
    }
    $cfg = "$root\tester\_queue_job.ini"
    @"
ExpertsEnable=false
TestExpert=$name
TestSymbol=EURUSD
TestPeriod=$period
TestModel=0
TestSpread=$spread
TestOptimization=false
TestDateEnable=true
TestFromDate=$from
TestToDate=$to
TestReport=reports\$report
TestReplaceReport=true
TestShutdownTerminal=true
TestVisualEnable=false
"@ | Set-Content -Encoding ASCII $cfg
    $t = Get-Date
    # minimized WITHOUT activation (SW_SHOWMINNOACTIVE) so it never steals keyboard focus
    $su = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ ShowWindow = [uint16]7 }
    $cr = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = "`"$root\terminal.exe`" /portable `"$cfg`""; CurrentDirectory = $root; ProcessStartupInformation = $su }
    if ($cr.ReturnValue -eq 0) { Wait-Process -Id $cr.ProcessId -ErrorAction SilentlyContinue }
    $ok = Test-Path "$root\reports\$report.htm"
    $res = if ($ok) { 'OK' } else { 'FAIL' }
    if ($ok -and $deposit) {
        $h = [IO.File]::ReadAllText("$root\reports\$report.htm") -replace '<[^>]+>', '|' -replace '\|+', '|'
        if ($h -match 'Initial deposit\|([\d.]+)' -and [double]$matches[1] -ne [double]$deposit) { $res = "DEPOSIT_IGNORED($($matches[1]))" }
    }
    "`"$job`",$res,$report.htm,$($t.ToString('yyyy-MM-dd HH:mm')),$([int]((Get-Date)-$t).TotalMinutes),$freeGB" | Add-Content $done
    "$res $job -> reports\$report.htm"
} finally { Remove-Item $lock -ErrorAction SilentlyContinue }
