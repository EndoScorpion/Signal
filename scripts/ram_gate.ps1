$f = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
if ($f -ge 1024) { "OPEN: $f MB free, tests can start" } else { "CLOSED: $f MB free, need $(1024 - $f) MB more" }
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 8 Name, Id, @{N='MB'; E={[math]::Round($_.WorkingSet64 / 1MB)}} | Format-Table -AutoSize
