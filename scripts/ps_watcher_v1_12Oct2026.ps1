# Watcher: runs any .ps1 that Claude drops in Signal\inbox, saves output to Signal\outbox\<name>.txt, then moves script to inbox\done.
# Start once (admin PowerShell), leave window open. Ctrl+C to stop.
$in='C:\Users\endos\Signal\inbox'; $outd='C:\Users\endos\Signal\outbox'
New-Item -ItemType Directory -Force $in,$outd,"$in\done" | Out-Null
Write-Host "Watching $in ... (Ctrl+C to stop)" -ForegroundColor Green
while ($true) {
  Get-ChildItem $in -Filter *.ps1 -File | ForEach-Object {
    Write-Host "Running $($_.Name)" -ForegroundColor Cyan
    $o = Join-Path $outd ($_.BaseName + '.txt')
    & powershell -ExecutionPolicy Bypass -File $_.FullName *>&1 | Tee-Object -FilePath $o
    Move-Item $_.FullName "$in\done\$($_.Name)" -Force
    "DONE $(Get-Date)" | Add-Content $o
  }
  Start-Sleep 5
}
