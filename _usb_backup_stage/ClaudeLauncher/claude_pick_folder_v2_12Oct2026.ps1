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
