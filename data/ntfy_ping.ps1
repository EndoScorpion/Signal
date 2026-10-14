$t=(Get-Content "C:\Users\endos\Signal\data\ntfy_topic.txt" -Raw).Trim()
Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$t" -Body "Alert test $(Get-Date -Format HH:mm) ET. Stops 22:00." -Headers @{Title='[MasterEA] 15-min test'} | Out-Null
