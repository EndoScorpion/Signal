Stop-Process -Name chrome,PhoneExperienceHost -Force -ErrorAction SilentlyContinue
Start-Sleep 3
"Free RAM KB: " + (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
"MT4 running: " + [bool](Get-Process terminal -ErrorAction SilentlyContinue)
& powershell -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\run_g5_all_v2_12Oct2026.ps1
