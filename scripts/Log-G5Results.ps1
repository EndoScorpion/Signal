# Read-only: parses g5_summary*.txt into one CSV (rebuilt each time, safe to rerun) and prints a comparison.
# Output: C:\Users\endos\Signal\data\g5_results_history.csv
$data = 'C:\Users\endos\Signal\data'
$rows = foreach ($f in Get-ChildItem $data -Filter 'g?_summary*.txt' | Sort-Object Name) {
  $seen = @{}; $cur = $null
  foreach ($l in Get-Content -LiteralPath $f.FullName) {
    if ($l -match '^=== (\w+) ===') {
      if ($cur) { $cur }
      $n = $Matches[1]; $seen[$n] = 1 + [int]$seen[$n]
      $cur = [ordered]@{ File = $f.Name; Variant = $n; Pass = $seen[$n]; Trades = $null; WinRate = $null; Wins = $null; Losses = $null; NetPnL = $null; PF = $null; MaxDD = $null; Gate = $null }
    }
    elseif ($cur) {
      if     ($l -match 'Total trades\s*:\s*(\d+)')                        { $cur.Trades = [int]$Matches[1] }
      elseif ($l -match 'Win rate\s*:\s*([\d.]+)%\s*\((\d+)W / (\d+)L\)')  { $cur.WinRate = [double]$Matches[1]; $cur.Wins = [int]$Matches[2]; $cur.Losses = [int]$Matches[3] }
      elseif ($l -match 'Net PnL\s*:\s*\$\s*(-?[\d.]+)')                   { $cur.NetPnL = [double]$Matches[1] }
      elseif ($l -match 'PF estimate\s*:\s*([\d.]+)')                      { $cur.PF = [double]$Matches[1] }
      elseif ($l -match 'Max closed-DD\s*:\s*\$\s*([\d.]+)')               { $cur.MaxDD = [double]$Matches[1] }
      elseif ($l -match 'OOS GATE:\s*(\w+)')                               { $cur.Gate = $Matches[1] }
    }
  }
  if ($cur) { $cur }
}
$all = $rows | ForEach-Object { [pscustomobject]$_ }
$all | Export-Csv "$data\g5_results_history.csv" -NoTypeInformation
$all | Format-Table -AutoSize
$best = $all | Where-Object { $_.Trades } | Sort-Object PF -Descending | Select-Object -First 1
if ($best) { "Best PF: $($best.Variant) (PF $($best.PF), WR $($best.WinRate)%, net `$$($best.NetPnL), DD `$$($best.MaxDD), $($best.Trades) trades)" }
"Note: identical numbers across variants/passes (e.g. g5a=g5b) mean the variants may not differ in behavior - check before trusting."
