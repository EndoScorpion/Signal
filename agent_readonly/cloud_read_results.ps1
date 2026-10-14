Get-ChildItem C:\Users\endos\Desktop\mt4_tester2 -Recurse -Filter 'LOOP_x_wr_base_clean__rc_th_g2_AtrCapPts_90__*.htm' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | ForEach-Object {
  $t = [IO.File]::ReadAllText($_.FullName) -replace '<[^>]+>', '|' -replace '\s+', ' '
  function G($label) { if ($t -match ([regex]::Escape($label) + '\s*\|+\s*([^|]+)')) { $Matches[1].Trim() } else { '?' } }
  "{0} | net={1} | PF={2} | trades={3} | win={4} | DD={5}" -f $_.Name.Replace('LOOP_x_wr_base_clean__rc_th_g2_AtrCapPts_90__',''), (G 'Total net profit'), (G 'Profit factor'), (G 'Total trades'), (G 'Profit trades (% of total)'), (G 'Maximal drawdown')
}
