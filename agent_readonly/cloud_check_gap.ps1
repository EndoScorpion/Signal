$d = 'C:\Users\endos\Signal\agent_readonly'
if (Get-Process -Id 4700 -ErrorAction SilentlyContinue) { 'audit1 RUNNING' } else { 'audit1 not running' }
if (Test-Path "$d\gap_audit_result.txt") { 'RESULT READY'; Get-Content "$d\gap_audit_result.txt" } else { 'no result yet' }
Get-Content "$d\gap_stderr.txt" -Tail 3 -ErrorAction SilentlyContinue
$o = Get-CimInstance Win32_OperatingSystem; 'freeMB=' + [int]($o.FreePhysicalMemory/1024)
