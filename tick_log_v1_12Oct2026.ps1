# tick_log_v1_12Oct2026.ps1
# Scans MT4 strategy tester .htm reports and appends one row per NEW report to tick_log.csv:
# bars in test, ticks modelled, modelling quality, model, period, trades, PF, net profit.
# Usage: powershell -ExecutionPolicy Bypass -File .\tick_log_v1_12Oct2026.ps1
param(
  [string[]]$Paths = @('C:\Users\endos\Signal\data','C:\Users\endos\MT4_Backtest\tester\reports'),
  [string]$Log = 'C:\Users\endos\Signal\tick_log.csv'
)
function Grab($t, $pattern) { $m = [regex]::Match($t, $pattern); if ($m.Success) { $m.Groups[1].Value.Trim() } else { '' } }

$seen = @{}
if (Test-Path $Log) { Import-Csv $Log | ForEach-Object { $seen["$($_.file)|$($_.modified)"] = 1 } }

$rows = @()
foreach ($p in $Paths) {
  if (-not (Test-Path $p)) { continue }
  Get-ChildItem $p -Recurse -File -Include *.htm,*.html | ForEach-Object {
    $key = "$($_.FullName)|$($_.LastWriteTime.ToString('d MMM yyyy HH:mm:ss'))"
    if ($seen.ContainsKey($key)) { return }
    $raw = Get-Content -LiteralPath $_.FullName -Raw
    $t = ($raw -replace '<[^>]+>', ' ' -replace '&nbsp;', ' ' -replace '\s+', ' ')
    if ($t -notmatch 'Bars in test') {
      $raw = Get-Content -LiteralPath $_.FullName -Raw -Encoding Unicode
      $t = ($raw -replace '<[^>]+>', ' ' -replace '&nbsp;', ' ' -replace '\s+', ' ')
    }
    $rows += [pscustomobject]@{
      logged_at = (Get-Date -Format 'd MMM yyyy HH:mm')
      file      = $_.FullName
      modified  = $_.LastWriteTime.ToString('d MMM yyyy HH:mm:ss')
      symbol    = Grab $t 'Symbol\s+(\S+)'
      period    = Grab $t 'Period\s+(.+?)\s+Model'
      model     = Grab $t 'Model\s+(Every tick(?: \([^)]*\))?|Control points|Open prices only)'
      bars      = Grab $t 'Bars in test\s+(\d+)'
      ticks     = (Grab $t 'Ticks modelled\s+([\d ]+?)\s+(?:Modelling|Modeling)') -replace ' ', ''
      quality   = Grab $t 'Model?ling quality\s+([\d.]+%)'
      trades    = Grab $t 'Total trades\s+(\d+)'
      pf        = Grab $t 'Profit factor\s+([\d.]+)'
      net       = (Grab $t 'Total net profit\s+(-?[\d ]+\.\d+)') -replace ' ', ''
    }
  }
}
if ($rows.Count -eq 0) { Write-Host 'No new reports found.'; return }
if (Test-Path $Log) { $rows | Export-Csv $Log -NoTypeInformation -Append } else { $rows | Export-Csv $Log -NoTypeInformation }
$rows | Format-Table symbol, period, model, bars, ticks, quality, trades, pf, net -AutoSize
Write-Host "Logged $($rows.Count) new report(s) to $Log" -ForegroundColor Green
