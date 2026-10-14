# Desktop shortcut target: pause = no new test starts; the running test finishes by itself. Works offline.
New-Item 'C:\Users\endos\Desktop\hst_out\MT4_PAUSE' -ItemType File -Force | Out-Null
Write-Host 'Paused. No new test will start; the one running now will finish. Use Resume Tests to continue.'
Start-Sleep -Seconds 5
