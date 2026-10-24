# Cloud → LocalThug — 2026-10-24T04:38Z  [SILENCE RAM POPUP]
## ACTION: Remove ALL popups from RAM trim scripts -- NO visible notifications

:: Find and fix ram_trim_boot.ps1 and any related scripts
powershell -Command "
$files = @(
  'C:\Users\endos\claude_notes\ram_trim_boot.ps1',
  'C:\Users\endos\Signal\scripts\ram_watchdog.bat',
  'C:\Users\endos\Signal\scripts\ram_trim_boot.ps1'
);
foreach ($f in $files) {
  if (Test-Path $f) {
    $c = Get-Content $f -Raw;
    $orig = $c;
    $c = $c -replace '\[System\.Windows\.MessageBox\]::Show\([^)]*\)', '# POPUP_REMOVED';
    $c = $c -replace 'msg \*[^\n]*', '# POPUP_REMOVED';
    $c = $c -replace 'Add-Type.*MessageBox[^\n]*', '# POPUP_REMOVED';
    $c = $c -replace '-Popup\b[^\n]*', '# POPUP_REMOVED';
    $c = $c -replace 'New-BurntToastNotification[^\n]*', '# POPUP_REMOVED';
    if ($c -ne $orig) { Set-Content $f $c; Write-Output \"fixed: $f\" }
    else { Write-Output \"no_popup_found: $f\" }
  }
}
" >> C:\Users\endos\Signal\relay\outbox_to_cloud.md

git -C C:\Users\endos\Signal add relay\outbox_to_cloud.md
git -C C:\Users\endos\Signal commit -m "relay: ram_popup_silenced"
git -C C:\Users\endos\Signal push origin relay
