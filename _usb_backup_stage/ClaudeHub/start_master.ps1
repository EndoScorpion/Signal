# start_master.ps1 - opens the ClaudeHub master session (NOT as admin, so paste and drag-drop work).
# Restarts Claude if it exits; type CLOSE to really quit.
param([switch]$Resume)   # -Resume continues the last master conversation; default starts fresh

Set-Location $PSScriptRoot
$Host.UI.RawUI.WindowTitle = 'ClaudeHub MASTER *** DO NOT CLOSE ***'

$free = [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
Write-Host "  ClaudeHub MASTER  ·  $free MB RAM free" -ForegroundColor Green
if ($free -lt 600) { Write-Host '  Warning: under 600 MB free. Close something first if you can.' -ForegroundColor Yellow }

$first = $true
while ($true) {
  if ($first -and -not $Resume) { claude -n master } else { claude --continue }
  $first = $false
  Write-Host ''
  Write-Host '  Claude exited. Press Enter to restart, or type CLOSE to quit.' -ForegroundColor Yellow
  if ((Read-Host '  >').Trim().ToUpper() -eq 'CLOSE') { break }
}
