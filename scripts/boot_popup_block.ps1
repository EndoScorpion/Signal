# boot_popup_block.ps1 - runs at startup, watches for titleless flash windows and closes them
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    public const uint WM_CLOSE = 0x0010;
}
"@
$closed = 0
$end = (Get-Date).AddMinutes(5)  # watch for 5 min after boot
while ((Get-Date) -lt $end) {
    Get-Process -Name "powershell","cmd" -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowHandle -ne [IntPtr]::Zero -and
        [WinAPI]::GetWindowTextLength($_.MainWindowHandle) -eq 0 -and
        [WinAPI]::IsWindowVisible($_.MainWindowHandle)
    } | ForEach-Object {
        [WinAPI]::PostMessage($_.MainWindowHandle, [WinAPI]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
        $closed++
    }
    Start-Sleep -Milliseconds 500
}
"$(Get-Date -Format o) Popup blocker finished. Closed $closed windows." | Out-File "C:\Users\endos\Signal\logs\popup_block.log" -Append
