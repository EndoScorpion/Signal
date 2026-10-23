# already running guard
$already = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq '' } | Where-Object { (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine -match 'boot_popup_block' }
if ($already.Count -gt 1) { exit }

# boot_popup_block.ps1 - WMI event-driven popup killer, catches windows the instant they appear
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder buf, int max);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmd);
    public const uint WM_CLOSE = 0x0010;
    public const int SW_MINIMIZE = 6;
}
"@

$logPath = "C:\Users\endos\Signal\logs\popup_block.log"
# Window titles that are SAFE - never touch these
$keepPattern = 'Claude|hub|signal|MT4|MetaEditor|terminal|Administrator|TA Fix|Copilot|Stellaris|stellaris|Windows PowerShell|steam|Steam'
# Window titles that should be KILLED outright (empty/transient)
$killPattern  = '^$|^\s*$|^RESULT$|^result$|^Select$|pm2|Node\.js not found|unstartup|NewsGather|\\\\WindowsPowerShell\\\\|wscript\.exe|conhost\.exe'

function Check-And-Kill {
    $cutoff = (Get-Date).AddSeconds(-5)
    Get-Process -Name "powershell","cmd","wscript","cscript","conhost" -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero -and $_.StartTime -gt $cutoff } |
        ForEach-Object {
            $hwnd = $_.MainWindowHandle
            if (-not [WinAPI]::IsWindowVisible($hwnd)) { return }
            $len = [WinAPI]::GetWindowTextLength($hwnd)
            $title = ""
            if ($len -gt 0) {
                $sb = New-Object System.Text.StringBuilder ($len + 2)
                [WinAPI]::GetWindowText($hwnd, $sb, $sb.Capacity) | Out-Null
                $title = $sb.ToString().Trim()
            }
            $safe = $title -match $keepPattern
            $kill = $title -match $killPattern
            if ($safe) { return }
            if ($kill -or $len -eq 0) {
                # Empty/transient title - kill it
                [WinAPI]::PostMessage($hwnd, [WinAPI]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
                "$(Get-Date -Format 'HH:mm:ss') KILLED PID=$($_.Id) title='$title'" | Add-Content $logPath
            } else {
                # Has a title but not safe-listed (e.g. PDF/HTML tool popup) - minimize silently
                [WinAPI]::ShowWindow($hwnd, [WinAPI]::SW_MINIMIZE) | Out-Null
                "$(Get-Date -Format 'HH:mm:ss') MINIMIZED PID=$($_.Id) title='$title'" | Add-Content $logPath
            }
        }
}

"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') popup_block started (WMI+poll)" | Add-Content $logPath

# WMI event: fire when a new powershell.exe or cmd.exe process starts
$query = "SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_Process' AND (TargetInstance.Name='powershell.exe' OR TargetInstance.Name='cmd.exe' OR TargetInstance.Name='wscript.exe' OR TargetInstance.Name='node.exe')"
$watcher = New-Object System.Management.ManagementEventWatcher $query
$watcher.Options.Timeout = [System.TimeSpan]::FromSeconds(2)

while ($true) {
    try {
        $e = $watcher.WaitForNextEvent()
        # New process spawned - wait briefly for its window to appear, then kill if unwanted
        Start-Sleep -Milliseconds 100
        Check-And-Kill
        Start-Sleep -Milliseconds 300
        Check-And-Kill
    } catch [System.Management.ManagementException] {
        # Timeout - do a regular poll pass anyway
        Check-And-Kill
    } catch {
        "$(Get-Date -Format 'HH:mm:ss') ERR: $_" | Add-Content $logPath
        Start-Sleep -Seconds 2
    }
}






