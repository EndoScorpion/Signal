param([Parameter(Mandatory=$true)][string]$Folder)
if (-not (Test-Path -LiteralPath $Folder -PathType Container)) { Write-Host "Folder not found: $Folder" -ForegroundColor Red; return }
Set-Location -LiteralPath $Folder
$name = Split-Path -Leaf $Folder
if ([string]::IsNullOrWhiteSpace($name)) { $name = $Folder }
$Host.UI.RawUI.WindowTitle = "Claude - $name"
Write-Host "Starting Claude in $Folder (Remote Control name: $name)" -ForegroundColor Green
claude --remote-control "$name"
