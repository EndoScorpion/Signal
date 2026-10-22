# RAM + disk state checker — auto-cleans .fxt when disk low, posts state to board.json

$boardPath = "C:\Users\endos\board.json"
$fxtLimit  = 500  # MB — delete all .fxt if total exceeds this
$diskLimit = 20   # GB — delete all .fxt if C: free drops below this

# FXT auto-cleanup
$diskFreeGB = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
$fxtFiles   = Get-ChildItem "C:\Users\endos" -Recurse -Filter "*.fxt" -ErrorAction SilentlyContinue
$fxtTotalMB = [math]::Round(($fxtFiles | Measure-Object Length -Sum).Sum / 1MB, 1)
$fxtMsg     = ""

if ($diskFreeGB -lt $diskLimit -or $fxtTotalMB -gt $fxtLimit) {
    $fxtFiles | Remove-Item -Force -ErrorAction SilentlyContinue
    $diskFreeGBafter = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
    $fxtMsg = " | FXT cleaned ${fxtTotalMB}MB -> C: now ${diskFreeGBafter}GB free"
}

$freeMB = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024)

if ($freeMB -ge 1000) {
    $state = "GREEN"
    $action = "safe to start MT4"
} elseif ($freeMB -ge 600) {
    $state = "YELLOW"
    $action = "trim RAM before MT4"
} elseif ($freeMB -ge 400) {
    $state = "ORANGE"
    $action = "close browser tabs, run trim"
} elseif ($freeMB -ge 200) {
    $state = "RED"
    $action = "close non-essential apps now"
} else {
    $state = "CRITICAL"
    $action = "stop MT4, close everything"
}

# RAM trim (always, except skip if MT4 tester running)
$mt4Running = Get-Process -Name "terminal","metaeditor" -ErrorAction SilentlyContinue
if (-not $mt4Running) {
    Get-Process | ForEach-Object { try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }
    [GC]::Collect()
    $freeMB = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024)
}

$ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$msg = "RAM: ${freeMB}MB free - $state - $action${fxtMsg}"

$board = Get-Content $boardPath -Raw | ConvertFrom-Json
$entry = [PSCustomObject]@{ from="ram-check"; to="all"; msg=$msg; ts=$ts }
$board += $entry
$board | ConvertTo-Json -Depth 3 | Set-Content $boardPath -Encoding UTF8

Write-Host $msg
