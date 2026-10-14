$o = Get-CimInstance Win32_OperatingSystem
"freeMB=" + [int]($o.FreePhysicalMemory / 1024)
Get-ChildItem C:\Users\endos -Recurse -Filter EURUSD1.hst -ErrorAction SilentlyContinue | Select-Object FullName, @{n='MB';e={[int]($_.Length/1MB)}}, LastWriteTime | Format-Table -AutoSize | Out-String -Width 200
(Get-Command python -ErrorAction SilentlyContinue).Source
