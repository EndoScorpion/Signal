# ClaudeWatchdog - checks every 30s, relaunches CLI minimized if not running
while ($true) {
    $running = Get-Process -Name "node","claude" -ErrorAction SilentlyContinue
    if (-not $running) {
        $npmPath = "$env:APPDATA\npm\claude.cmd"
        if (Test-Path $npmPath) {
            Start-Process "cmd.exe" -ArgumentList "/c cd /d C:\Users\endos && claude" -WindowStyle Minimized
        } else {
            Start-Process "cmd.exe" -ArgumentList "/c cd /d C:\Users\endos && npx @anthropic-ai/claude-code@latest" -WindowStyle Minimized
        }
    }
    Start-Sleep -Seconds 30
}
