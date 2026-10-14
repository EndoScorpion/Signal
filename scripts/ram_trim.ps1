Add-Type -MemberDefinition '[DllImport("psapi.dll")] public static extern bool EmptyWorkingSet(IntPtr h);' -Name W -Namespace N
$b = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
Get-Process | ForEach-Object { try { [N.W]::EmptyWorkingSet($_.Handle) | Out-Null } catch {} }
$a = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
"before $b MB, after $a MB"
