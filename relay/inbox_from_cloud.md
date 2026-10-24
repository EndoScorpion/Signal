# Cloud → LocalThug — 2026-10-24T05:00Z  [EA OFFSET SCAN]

## ACTION: Scan EA .mq4 source files for hardcoded EET offset values
powershell -WindowStyle Hidden -Command "
$out = 'C:\Users\endos\Signal\relay\outbox_to_cloud.md';
$ts = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mmZ');
"=== EA OFFSET SCAN $ts ===" | Add-Content $out;

# Search paths
$paths = @(
  'C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal',
  'C:\Users\endos\Signal',
  'C:\Users\endos\hst_out'
);

$patterns = @('+3','-3','+2','-2','UTCOffset','ServerOffset','GMTOffset','TimeHour','TimeCurrent');

foreach ($base in $paths) {
  if (-not (Test-Path $base)) { continue }
  $mq4files = Get-ChildItem -Path $base -Recurse -Filter '*.mq4' -ErrorAction SilentlyContinue;
  $setfiles = Get-ChildItem -Path $base -Recurse -Filter '*.set' -ErrorAction SilentlyContinue;
  foreach ($f in ($mq4files + $setfiles)) {
    $hits = Select-String -Path $f.FullName -Pattern 'UTCOffset|ServerOffset|GMTOffset|[+-]\s*3\b|[+-]\s*2\b|TimeHour|TimeCurrent' -ErrorAction SilentlyContinue;
    if ($hits) {
      "FILE: $($f.FullName)" | Add-Content $out;
      foreach ($h in $hits) { "  L$($h.LineNumber): $($h.Line.Trim())" | Add-Content $out }
    }
  }
}
"=== SCAN DONE ===" | Add-Content $out;
git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md;
git -C C:\Users\endos\Signal commit -m 'relay: ea_offset_scan_done';
git -C C:\Users\endos\Signal push origin relay;
"
