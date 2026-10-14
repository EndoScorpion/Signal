$p = (Read-Host 'Full folder path').Trim('"').Trim()
if ($p -and (Test-Path -LiteralPath $p -PathType Container)) {
  Set-Location -LiteralPath $p
  Write-Host "Starting Claude in $p" -ForegroundColor Green
  claude
} else { Write-Host "Folder not found: $p" -ForegroundColor Red }
