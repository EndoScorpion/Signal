# Cloud → LocalThug — 2026-10-24T05:01Z  [GEN META.JSON SIDECARS]

## ACTION: Scan history folders, generate .meta.json for each CSV/HST
powershell -WindowStyle Hidden -Command "
$out = 'C:\Users\endos\Signal\relay\outbox_to_cloud.md';
$ts = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mmZ');
"=== META.JSON GEN $ts ===" | Add-Content $out;

$searchPaths = @(
  'C:\Users\endos\Signal\data',
  'C:\Users\endos\hst_out',
  'C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal'
);

foreach ($base in $searchPaths) {
  if (-not (Test-Path $base)) { continue }
  $files = Get-ChildItem -Path $base -Recurse -Include '*.csv','*.hst' -ErrorAction SilentlyContinue;
  foreach ($f in $files) {
    $metaPath = $f.FullName + '.meta.json';
    if (Test-Path $metaPath) { continue }  # skip if already exists
    
    # Infer source + timezone from filename
    $name = $f.Name.ToUpper();
    $src = 'unknown'; $tz = 'unknown'; $tzNote = '';
    if ($name -match 'FXOPEN|FXO') { $src='FXOpen'; $tz='EET (UTC+3 summer / UTC+2 winter)'; $tzNote='MT4 server EET; DST variable per bar date' }
    elseif ($name -match 'YAHOO|YF') { $src='Yahoo'; $tz='UTC+0'; $tzNote='exchange local; daily bars only' }
    elseif ($name -match 'STOOQ') { $src='Stooq'; $tz='UTC+0'; $tzNote='daily bars' }
    elseif ($name -match 'AV|ALPHAVANTAGE') { $src='AlphaVantage'; $tz='UTC+0'; $tzNote='inferred' }
    elseif ($f.Extension -eq '.hst') { $src='MT4 terminal'; $tz='EET (UTC+3 summer / UTC+2 winter)'; $tzNote='MT4 .hst always EET server time' }
    else { $src='unknown'; $tz='unknown'; $tzNote='manual verification needed' }
    
    $meta = [PSCustomObject]@{
      source=$src; timezone=$tz; dst_note=$tzNote;
      filename=$f.Name; created=$ts; verified_by='auto-scan'
    };
    $meta | ConvertTo-Json | Set-Content $metaPath;
    "created: $metaPath" | Add-Content $out;
  }
}
"=== META GEN DONE ===" | Add-Content $out;
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md;
git -C C:\Users\endos\Signal commit -m 'relay: meta_json_gen_done';
git -C C:\Users\endos\Signal push origin relay;
"
