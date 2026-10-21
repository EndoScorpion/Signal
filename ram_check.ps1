# RAM state checker — posts current free RAM and recommended action to board.json
# Safe: read-only system queries + board.json append only. Never kills processes.

$boardPath = "C:\Users\endos\board.json"

$freeMB = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024)

if ($freeMB -ge 1500) {
    $state = "GREEN"
    $action = "safe to open anything"
} elseif ($freeMB -ge 1000) {
    $state = "YELLOW"
    $action = "MT4 ok, keep browser minimal"
} elseif ($freeMB -ge 600) {
    $state = "ORANGE"
    $action = "close GOON tab if open, no new MT4"
} elseif ($freeMB -ge 400) {
    $state = "RED"
    $action = "close CLI and browser, MT4 only if already running"
} else {
    $state = "CRITICAL"
    $action = "stop MT4 test, close everything non-essential"
}

$ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$msg = "RAM: ${freeMB}MB free - $state - $action"

$board = Get-Content $boardPath -Raw | ConvertFrom-Json
$entry = [PSCustomObject]@{ from="ram-check"; to="all"; msg=$msg; ts=$ts }
$board += $entry
$board | ConvertTo-Json -Depth 3 | Set-Content $boardPath -Encoding UTF8

Write-Host $msg
