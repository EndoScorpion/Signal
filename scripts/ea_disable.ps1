# Remote disable switch for EAs that read the control file (MR_RegimeSwitch_b62+ with UseControlFile=true). Works offline.
# Writes DISABLE=1 into the MetaTrader COMMON files folder (shared by all terminals on this PC). The EA blocks NEW entries on its next bar; open trades keep their stops
# (set CloseAllOnDisable=true in the EA if you also want it to flatten). No orders are placed by this script.
$d = Join-Path $env:APPDATA 'MetaQuotes\Terminal\Common\Files'; if (-not (Test-Path $d)) { New-Item -ItemType Directory $d -Force | Out-Null }
"DISABLE=1`r`n# set by ea_disable.ps1 at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content (Join-Path $d 'ea_control.txt') -Encoding ascii
Write-Host "EAs reading ea_control.txt will block new entries on their next bar. File: $d\ea_control.txt"
. 'C:\Users\endos\Signal\scripts\phone_notify.ps1'; Send-Phone 'EA remote disable written: EAs with UseControlFile will block new entries.' -Title 'EA kill switch' -Priority high
Start-Sleep -Seconds 5
