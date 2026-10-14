$o = Get-CimInstance Win32_OperatingSystem
"freeMB=" + [int]($o.FreePhysicalMemory / 1024)
"MT4_PAUSE exists: " + (Test-Path C:\Users\endos\Desktop\hst_out\MT4_PAUSE)
Get-Process terminal,metatester,metaeditor,python -ErrorAction SilentlyContinue | ForEach-Object { "{0} {1} {2}MB cpu={3}" -f $_.Name, $_.Id, [int]($_.WS/1MB), [int]$_.CPU }
"--- evolve_log tail"
Get-Content C:\Users\endos\Signal\data\evolve_log.txt -Tail 8
"--- ER study"
if (Test-Path C:\Users\endos\Signal\agent_readonly\er_m1_result.txt) { "RESULT READY" } else { "no result yet" }
Get-Content C:\Users\endos\Signal\agent_readonly\er_m1_stderr.txt -Tail 3 -ErrorAction SilentlyContinue
"--- latest results"
Get-ChildItem C:\Users\endos\Desktop\mt4_tester2 -Recurse -Filter *.htm -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | ForEach-Object { $_.LastWriteTime.ToString('MM-dd HH:mm') + ' ' + $_.Name }
