# boot_ram_trim.ps1 - runs at startup, frees RAM before other processes load
[System.GC]::Collect()
# Empty working sets of background processes
Get-Process | Where-Object {$_.Name -match "chrome|msedge|SearchApp|SearchIndexer|OneDrive"} | ForEach-Object {
    try { $_.MinWorkingSet = 1; $_.MaxWorkingSet = 1 } catch {}
}
# Log
"$(Get-Date -Format o) RAM trim done. Free: $([math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)) GB" | Out-File "C:\Users\endos\Signal\logs\boot_ram_trim.log" -Append
