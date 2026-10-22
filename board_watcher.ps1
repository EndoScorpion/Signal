# board_watcher.ps1 — watches board.json for new messages to LocalThug/all
# Logs new messages. Runs silent as background service via schtask.

$boardPath = "C:\Users\endos\board.json"
$logPath   = "C:\Users\endos\Signal\board_watcher.log"
$lastCount = 0

function Log($msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    "$ts $msg" | Add-Content $logPath
}

Log "board_watcher started"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = Split-Path $boardPath
$watcher.Filter = Split-Path $boardPath -Leaf
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite
$watcher.EnableRaisingEvents = $true

Log "watching $boardPath"

while ($true) {
    $changed = $watcher.WaitForChanged([System.IO.WatcherChangeTypes]::Changed, 10000)
    if ($changed.TimedOut) { continue }

    Start-Sleep -Milliseconds 300
    try {
        $board = Get-Content $boardPath -Raw | ConvertFrom-Json
        $count = $board.Count
        if ($count -le $lastCount) { continue }

        $newMsgs = $board | Select-Object -Skip $lastCount
        $lastCount = $count

        foreach ($msg in $newMsgs) {
            if ($msg.to -in @("all","LocalThug","localth")) {
                Log "NEW from=$($msg.from) to=$($msg.to) msg=$($msg.msg)"
            }
        }
    } catch {
        Log "ERROR: $_"
    }
}
