# Desktop shortcut target: trim RAM (apps stay open, nothing is closed) and show the test gate. Works offline.
powershell -NoProfile -File 'C:\Users\endos\Signal\scripts\ram_trim.ps1'
powershell -NoProfile -File 'C:\Users\endos\Signal\scripts\ram_gate.ps1'
Start-Sleep -Seconds 8
