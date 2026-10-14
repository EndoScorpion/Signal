# Send a short status message to Nasif's phone through ntfy (https://ntfy.sh). Status text only, never secrets or credentials.
# Usage: . C:\Users\endos\Signal\scripts\phone_notify.ps1; Send-Phone "pass 1 done" [-Title "EA loop"] [-Priority default|high]
function Send-Phone([Parameter(Mandatory)][string]$Message, [string]$Title = 'EA loop', [string]$Priority = 'default', [int]$Max = 300) {
  $t = (Get-Content 'C:\Users\endos\Signal\data\ntfy_topic.txt' -ErrorAction SilentlyContinue | Select-Object -First 1)
  if (-not $t) { return }
  try { Invoke-RestMethod -Uri "https://ntfy.sh/$t" -Method Post -Body ($Message.Substring(0, [math]::Min($Max, $Message.Length))) -Headers @{ Title = $Title; Priority = $Priority } -TimeoutSec 15 | Out-Null } catch { }   # offline or blocked: ignore
}
