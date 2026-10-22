# pre_test_fxt_guard.ps1
# Run BEFORE any MT4 backtest. Wipes all .fxt files so they regenerate cleanly.
# Prevents bloat if a previous test was cut off mid-run.
$ErrorActionPreference = "SilentlyContinue"
$paths = @(
    "C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\Tester",
    "C:\Users\endos\Desktop\mt4_tester",
    "C:\Users\endos\Desktop\mt4_tester2"
)
$deleted = 0; $freedMB = 0
foreach ($p in $paths) {
    if (-not (Test-Path $p)) { continue }
    Get-ChildItem $p -Recurse -Filter "*.fxt" -ErrorAction SilentlyContinue | ForEach-Object {
        $freedMB += [math]::Round($_.Length/1MB, 2)
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        $deleted++
    }
}
Add-Content "C:\Users\endos\Signal\relay\fxt_cleanup.log" "$(Get-Date -Format u) PRE-TEST deleted=$deleted freed=${freedMB}MB"
Write-Host "Pre-test FXT guard: deleted $deleted files, freed ${freedMB} MB"
