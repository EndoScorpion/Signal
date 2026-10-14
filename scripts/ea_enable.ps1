# Clears the remote disable (writes DISABLE=0). Works offline. No orders are placed.
$d = Join-Path $env:APPDATA 'MetaQuotes\Terminal\Common\Files'; if (-not (Test-Path $d)) { New-Item -ItemType Directory $d -Force | Out-Null }
"DISABLE=0`r`n# cleared by ea_enable.ps1 at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content (Join-Path $d 'ea_control.txt') -Encoding ascii
Write-Host 'Remote disable cleared: EAs will allow new entries again on their next bar.'
. 'C:\Users\endos\Signal\scripts\phone_notify.ps1'; Send-Phone 'EA remote disable cleared.' -Title 'EA kill switch'
Start-Sleep -Seconds 5
