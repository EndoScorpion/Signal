# fxt_cleanup.ps1 — delete .fxt files older than 30 days. Runs weekly via Task Scheduler, hidden.
$ErrorActionPreference = "SilentlyContinue"
$cutoff = (Get-Date).AddDays(-30)
$paths = @(
    "C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\Tester",
    "C:\Users\endos\Desktop\mt4_tester",
    "C:\Users\endos\Desktop\mt4_tester2"
)
$deleted = 0; $freedMB = 0
foreach ($p in $paths) {
    if (-not (Test-Path $p)) { continue }
    Get-ChildItem $p -Recurse -Filter "*.fxt" -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } |
        ForEach-Object { $freedMB += [math]::Round($_.Length/1MB,2); Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue; $deleted++ }
}
# Log result
Add-Content "C:\Users\endos\Signal\relay\fxt_cleanup.log" "$(Get-Date -Format u) deleted=$deleted freed=${freedMB}MB"
