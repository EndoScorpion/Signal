# install_claude_folder_picker_v2_12Oct2026.ps1
# Run once. Creates a launcher script and two Desktop shortcuts:
#   "Claude - Pick Folder"  -> Windows File Explorer-style dialog, then starts claude in the folder you choose
#   "Claude - Signal"       -> starts claude in C:\Users\endos\Signal
# Run: powershell -ExecutionPolicy Bypass -File .\install_claude_folder_picker_v2_12Oct2026.ps1

$dir = Join-Path $env:USERPROFILE 'ClaudeLauncher'
New-Item -ItemType Directory -Force $dir | Out-Null
$launcher = Join-Path $dir 'claude_pick_folder_v2_12Oct2026.ps1'

$body = @'
Add-Type -AssemblyName System.Windows.Forms
$start = Join-Path ([Environment]::GetFolderPath('Desktop')) '$'
if (-not (Test-Path -LiteralPath $start)) { $start = $env:USERPROFILE }
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Title = 'Open the folder you want, then click Open'
$d.InitialDirectory = $start
$d.ValidateNames = $false
$d.CheckFileExists = $false
$d.CheckPathExists = $true
$d.FileName = 'Select this folder'
if ($d.ShowDialog() -eq 'OK') {
  $dir = Split-Path -LiteralPath $d.FileName -Parent
  if (Test-Path -LiteralPath $d.FileName -PathType Container) { $dir = $d.FileName }
  Set-Location -LiteralPath $dir
  Write-Host "Starting Claude in $dir" -ForegroundColor Green
  claude
} else { Write-Host 'No folder chosen.' }
'@
Set-Content -LiteralPath $launcher -Value $body -Encoding UTF8

$ps = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
$w = New-Object -ComObject WScript.Shell
$desk = [Environment]::GetFolderPath('Desktop')

$s = $w.CreateShortcut((Join-Path $desk 'Claude - Pick Folder.lnk'))
$s.TargetPath = $ps
$s.Arguments = "-NoExit -ExecutionPolicy Bypass -STA -File `"$launcher`""
$s.WorkingDirectory = $env:USERPROFILE
$s.Save()

$s2 = $w.CreateShortcut((Join-Path $desk 'Claude - Signal.lnk'))
$s2.TargetPath = $ps
$s2.Arguments = '-NoExit -Command "Set-Location C:\Users\endos\Signal; claude"'
$s2.WorkingDirectory = 'C:\Users\endos\Signal'
$s2.Save()

# Third option: type or paste a full path (e.g. C:\Games\Sid Meier's Pirates or any $ projects folder)
$launcher2 = Join-Path $dir 'claude_type_path_v2_12Oct2026.ps1'
$body2 = @'
$p = (Read-Host 'Full folder path').Trim('"').Trim()
if ($p -and (Test-Path -LiteralPath $p -PathType Container)) {
  Set-Location -LiteralPath $p
  Write-Host "Starting Claude in $p" -ForegroundColor Green
  claude
} else { Write-Host "Folder not found: $p" -ForegroundColor Red }
'@
Set-Content -LiteralPath $launcher2 -Value $body2 -Encoding UTF8
$s3 = $w.CreateShortcut((Join-Path $desk 'Claude - Type Path.lnk'))
$s3.TargetPath = $ps
$s3.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$launcher2`""
$s3.WorkingDirectory = $env:USERPROFILE
$s3.Save()

Write-Host "Done. Launchers in: $dir" -ForegroundColor Green
Write-Host "Desktop shortcuts: 'Claude - Pick Folder' (Explorer popup), 'Claude - Type Path' (full path), 'Claude - Signal'" -ForegroundColor Green
