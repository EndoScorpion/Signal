New-Item C:\Users\endos\Signal\ram_guard.stop -Force | Out-Null; Start-Sleep 20; Remove-Item C:\Users\endos\Signal\ram_guard.stop -Force -ErrorAction SilentlyContinue
Start-Process powershell -WindowStyle Hidden -ArgumentList '-ExecutionPolicy','Bypass','-File','C:\Users\endos\Signal\scripts\ram_guard_v2_12Oct2026.ps1'
"ram guard v2 started"
