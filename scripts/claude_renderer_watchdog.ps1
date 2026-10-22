# Claude Desktop renderer watchdog
# Kills electron_renderer if it exceeds 280MB - Claude restarts it automatically
$limitMB = 280
$logFile = "C:\Users\endos\Signal\scripts\claude_watchdog.log"

$renderers = Get-Process -Name "Claude" -ErrorAction SilentlyContinue
if (-not $renderers) { exit 0 }

# Find electron renderer processes (child of Claude with high memory)
$allProcs = Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match '^Claude$' -and $_.WorkingSet64 -gt ($limitMB * 1MB)
}

foreach ($proc in $allProcs) {
    $mb = [math]::Round($proc.WorkingSet64 / 1MB)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$ts  Killed Claude PID $($proc.Id) at ${mb}MB (limit ${limitMB}MB)"
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}

# Also trim system RAM if free < 1.2GB
$os = Get-CimInstance Win32_OperatingSystem
$freeGB = $os.FreePhysicalMemory / 1MB
if ($freeGB -lt 1.2) {
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    Add-Content -Path $logFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  RAM trim triggered (free: $([math]::Round($freeGB,2))GB)"
}
