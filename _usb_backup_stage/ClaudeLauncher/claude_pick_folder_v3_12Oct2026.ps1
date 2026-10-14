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
  $picked = [string]$d.FileName
  $folder = $null
  if ($picked -and (Test-Path -LiteralPath $picked -PathType Container)) { $folder = $picked }
  elseif ($picked) { $folder = [System.IO.Path]::GetDirectoryName($picked) }
  if ([string]::IsNullOrWhiteSpace($folder) -or -not (Test-Path -LiteralPath $folder -PathType Container)) {
    Write-Host "Could not work out the folder (got: '$picked'). Close this window and try again." -ForegroundColor Red
  } else {
    Set-Location -LiteralPath $folder
    Write-Host "Starting Claude in $folder" -ForegroundColor Green
    claude
  }
} else { Write-Host 'No folder chosen.' }
