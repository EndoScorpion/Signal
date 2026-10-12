# run_oos_gate.ps1 â€” Job 1: 2021 M1 OOS backtest via MT4 command-line tester, then score.
#
# Usage (from the Signal repo root, normal PowerShell, MT4 CLOSED first):
#   powershell -ExecutionPolicy Bypass -File scripts\run_oos_gate.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\run_oos_gate.ps1 -Expert Strong2010b_claude_g2a
#
# Before the FIRST run, open MT4 Strategy Tester once by hand and set
# Initial deposit = 10000 USD (Expert properties > Testing). MT4's config file
# cannot set deposit/leverage; the tester reuses the last values.

param(
    [string]$Expert   = 'Strong2010b_claude_b20legs_g1a',   # .ex4 name in MQL4\Experts, no extension
    [string]$Terminal = '',                                 # path to terminal.exe; auto-detected if empty
    [string]$DataDir  = "$env:APPDATA\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415",
    [string]$From     = '2021.03.19',
    [string]$To       = '2022.01.01',
    [int]   $Spread   = 3,
    [int]   $Commission = 6,
    [int]   $Deposit  = 10000,
    [string]$Period  = 'M15',
    [int]   $Model   = 0
)

if ((Test-Path 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE') -or (Test-Path 'C:\Users\endos\MT4_Backtest\PAUSE')) { Write-Host 'MT4 PAUSED (PAUSE file exists) - not starting.' -ForegroundColor Yellow; exit 6 }
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

# 1. RAM gate (>= 1.0 GB free)
$freeKB = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
if ($freeKB -lt 400000) { Write-Host "RAM gate FAIL: $freeKB KB free (< 400,000). Close apps and retry." -ForegroundColor Red; exit 1 }
Write-Host "RAM gate OK: $freeKB KB free"

# 2. Locate terminal.exe and the compiled EA
if (-not $Terminal) {
    $origin = Join-Path $DataDir 'origin.txt'
    if (Test-Path $origin) { $Terminal = Join-Path ((Get-Content $origin -Encoding Unicode -Raw).Trim()) 'terminal.exe' }
}
if (-not $Terminal -or -not (Test-Path $Terminal)) { Write-Host "terminal.exe not found; pass -Terminal 'C:\...\terminal.exe'" -ForegroundColor Red; exit 1 }
$ex4 = Join-Path $DataDir "MQL4\Experts\$Expert.ex4"
if (-not (Test-Path $ex4)) { Write-Host "Compiled EA missing: $ex4 (compile the .mq4 in MetaEditor first)" -ForegroundColor Red; exit 1 }
if (Get-Process terminal -ErrorAction SilentlyContinue) { Write-Host "MT4 is running. Close it first (the tester run starts and shuts its own instance)." -ForegroundColor Red; exit 1 }

# 3. Write tester config (report path is relative to the data folder)
$tag     = $Expert -replace '^Strong2010b_claude_', ''
$fromTag = $From -replace '\.', ''
$toTag   = $To   -replace '\.', ''
$name    = "Strong2010b_claude_${tag}_${Period}_${fromTag}-${toTag}_sp$Spread"
$ini     = Join-Path $DataDir "tester\oos_gate_$tag.ini"
@"
TestExpert=$Expert
TestSymbol=EURUSD
TestPeriod=$Period
TestModel=$Model
TestSpread=$Spread
TestOptimization=false
TestDateEnable=true
TestFromDate=$From
TestToDate=$To
TestReport=tester\$name
TestReplaceReport=true
TestShutdownTerminal=true
"@ | Set-Content -Path $ini -Encoding ASCII

# 4. Run (blocks until the tester finishes and MT4 shuts down)
Write-Host "Running $Expert on EURUSD $Period $From -> $To, spread $Spread ... (can take a long time on Every Tick)"
Start-Process -FilePath $Terminal -ArgumentList "`"$ini`"" -Wait

# 5. Copy report into the repo and score it
$src = Join-Path $DataDir "tester\$name.htm"
if (-not (Test-Path $src)) { Write-Host "No report at $src - check MT4 journal (missing history / EA failed to load)." -ForegroundColor Red; exit 1 }
$dst = Join-Path $repo "data\$name.htm"
Copy-Item $src $dst -Force
Write-Host "Report saved: $dst"

python (Join-Path $repo 'analysis\oos_check.py') $dst --commission $Commission --deposit $Deposit
$code = $LASTEXITCODE
if ($code -eq 0) { Write-Host "OOS GATE: PASS (exit 0)" -ForegroundColor Green } else { Write-Host "OOS GATE: FAIL (exit $code)" -ForegroundColor Red }
Write-Host "Next: git add data\$name.htm; commit; push; record numbers in HUB_STATE.md ## RESULTS"
exit $code


