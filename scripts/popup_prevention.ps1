# popup_prevention.ps1 — kill visible console popups, enforce hidden mode on pollers
# Run at startup (hidden) and on-demand. No interaction, no output windows.

# 1. Close any visible non-essential console windows
Get-Process | Where-Object {
    $_.MainWindowHandle -ne 0 -and
    $_.MainWindowTitle -ne "" -and
    $_.Name -notin @("explorer","claude","WindowsTerminal","chrome","Code")
} | ForEach-Object {
    $_.CloseMainWindow() | Out-Null
}

# 2. Diagnose: log any process with a visible window
$visible = Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne "" } |
    Select-Object Id, Name, MainWindowTitle
$logPath = "C:\Users\endos\Signal\Logs\popup_block.log"
$ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
if ($visible) {
    "$ts VISIBLE: $(($visible | ForEach-Object {"[$($_.Name)/$($_.Id)] $($_.MainWindowTitle)"}) -join ', ')" |
        Add-Content $logPath
}

# 3. Re-register all pollers with -WindowStyle Hidden if any are running visibly
$pollers = @(
    @{Name="RelayAutoSync";     Script="C:\Users\endos\Signal\relay\cmd_poller.ps1"},
    @{Name="CloudCmdPollerGH";  Script="C:\Users\endos\Signal\scripts\CloudCmdPollerGH.ps1"},
    @{Name="Cloud_DC_Watchdog"; Script="C:\Users\endos\Signal\scripts\dc_watchdog.ps1"}
)
foreach ($p in $pollers) {
    $task = Get-ScheduledTask -TaskName $p.Name -ErrorAction SilentlyContinue
    if ($task -and (Test-Path $p.Script)) {
        $action = New-ScheduledTaskAction -Execute "powershell.exe" `
            -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$($p.Script)`""
        Set-ScheduledTask -TaskName $p.Name -Action $action -ErrorAction SilentlyContinue | Out-Null
    }
}

"$ts POPUP_PREV: done" | Add-Content $logPath
