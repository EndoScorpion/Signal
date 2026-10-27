$logPath = "C:\Users\endos\Signal\ps_log.txt"
$relayPath = "C:\Users\endos\Signal\relay\from_cli.json"
$ts = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
$id = "ps-log-push-$ts"

try {
    if (Test-Path $logPath) {
        $lines = Get-Content $logPath -Tail 50 -ErrorAction Stop
        $content = $lines -join "`n"
    } else {
        $content = ""
    }
    $msg = @{
        from   = "LocalThug"
        ts     = $ts
        id     = $id
        action = "ps_log"
        data   = $content
    } | ConvertTo-Json -Compress
    $msg | Set-Content $relayPath -Encoding UTF8 -NoNewline
} catch { }
