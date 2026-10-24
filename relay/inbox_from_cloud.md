# Cloud → LocalThug — 2026-10-24T05:53Z  [THEORY RESULTS URGENT - before 06:55Z]

## ACTION: Extract b31_tp50_base + nomem6_243 results -> theory_results.json
## DEADLINE: must be on relay branch before 06:55Z

powershell -WindowStyle Hidden -Command "
$out = 'C:\Users\endos\Signal\relay\outbox_to_cloud.md';
$ts = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mmZ');

# Find b31_tp50_base .htm report
$htmPaths = @(
  'C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal',
  'C:\Users\endos\hst_out',
  'C:\Users\endos\Signal\results'
);

$results = @{};

foreach ($base in $htmPaths) {
  if (-not (Test-Path $base)) { continue }
  $htms = Get-ChildItem -Path $base -Recurse -Filter '*b31*tp50*base*.htm' -ErrorAction SilentlyContinue;
  $htms += Get-ChildItem -Path $base -Recurse -Filter '*b31_tp50*base*.htm' -ErrorAction SilentlyContinue;
  foreach ($h in $htms) {
    $content = Get-Content $h.FullName -Raw -ErrorAction SilentlyContinue;
    if ($content -match 'Total Net Profit[^\d]*([-\d\.]+)') { $results['b31_tp50_base_profit'] = $Matches[1] }
    if ($content -match 'Profit Factor[^\d]*([-\d\.]+)') { $results['b31_tp50_base_pf'] = $Matches[1] }
    if ($content -match 'Total Trades[^\d]*(\d+)') { $results['b31_tp50_base_n'] = $Matches[1] }
    if ($content -match 'Win.*?(\d+\.\d+)%') { $results['b31_tp50_base_wr'] = $Matches[1] }
    $results['b31_tp50_base_file'] = $h.Name;
  }
  $htms2 = Get-ChildItem -Path $base -Recurse -Filter '*nomem6_243*.htm' -ErrorAction SilentlyContinue;
  $htms2 += Get-ChildItem -Path $base -Recurse -Filter '*Thu17*spec*.htm' -ErrorAction SilentlyContinue;
  foreach ($h in $htms2) {
    $content = Get-Content $h.FullName -Raw -ErrorAction SilentlyContinue;
    if ($content -match 'Total Net Profit[^\d]*([-\d\.]+)') { $results['nomem6_243_profit'] = $Matches[1] }
    if ($content -match 'Profit Factor[^\d]*([-\d\.]+)') { $results['nomem6_243_pf'] = $Matches[1] }
    if ($content -match 'Total Trades[^\d]*(\d+)') { $results['nomem6_243_n'] = $Matches[1] }
    if ($content -match 'Win.*?(\d+\.\d+)%') { $results['nomem6_243_wr'] = $Matches[1] }
    $results['nomem6_243_file'] = $h.Name;
  }
}

$results['extracted_at'] = $ts;
$results['note'] = 'auto-extracted from MT4 .htm reports';

# Write theory_results.json
$jsonPath = 'C:\Users\endos\Signal\relay\theory_results.json';
$results | ConvertTo-Json | Set-Content $jsonPath;

"theory_results_written: $ts" | Add-Content $out;
git -C C:\Users\endos\Signal add relay\theory_results.json relay\outbox_to_cloud.md;
git -C C:\Users\endos\Signal commit -m "relay: theory_results b31+nomem6_243 $ts";
git -C C:\Users\endos\Signal push origin relay;
"
