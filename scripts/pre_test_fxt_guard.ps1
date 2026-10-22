# pre_test_fxt_guard.ps1 — clear stale .fxt files before MT4 test
# Run hidden before any MT4 backtest to avoid history corruption
$fxtDirs = @(
    'C:\Program Files (x86)\FXOpen MT4\history',
    'C:\Program Files\FXOpen MT4\history',
    "$env:APPDATA\MetaQuotes\Terminal"
)
$removed = 0
foreach ($dir in $fxtDirs) {
    if (Test-Path $dir) {
        $files = Get-ChildItem -Path $dir -Recurse -Filter '*.fxt' -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
        foreach ($f in $files) {
            Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
            $removed++
        }
    }
}
$repoRoot = 'C:\Users\endos\Signal'
$outbox = "$repoRoot\relay\outbox_to_cloud.md"
$existing = if (Test-Path $outbox) { Get-Content $outbox -Raw } else { '' }
$append = "`n`n## FXT Guard $(Get-Date -Format 'o')`nRemoved $removed stale .fxt files (>7 days old). Ready for MT4 test."
Set-Content $outbox ($existing + $append)
Set-Location $repoRoot
git add relay/outbox_to_cloud.md
git commit -m "relay: fxt guard cleared $removed files $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
