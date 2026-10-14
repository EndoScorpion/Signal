# Signal dashboard launcher: one instance, always on top, reopens if closed, refreshes board_data.js from agent_board.json.
param([string]$Board = "$PSScriptRoot\..\data\agent_board.json", [int]$W = 380, [int]$H = 560)
$mutex = New-Object System.Threading.Mutex($false, "Global\SignalDashboardLauncher")
if (-not $mutex.WaitOne(0)) { exit }   # max 1 instance
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W { [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f); }
"@
$html = Join-Path $PSScriptRoot "signal_dashboard.html"
$data = Join-Path $PSScriptRoot "board_data.js"
$profile = Join-Path $env:LOCALAPPDATA "SignalDashboard"
$browser = @("$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
             "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
function Sync { if (Test-Path $Board) { try { $j = Get-Content $Board -Raw; $null = $j | ConvertFrom-Json
    Set-Content -Path $data -Value ("window.BOARD = " + $j + ";") -Encoding UTF8 } catch {} } }  # bad JSON keeps last good file
while ($true) {
  Sync
  $p = Start-Process $browser -PassThru -ArgumentList "--app=file:///$($html -replace '\\','/')", "--user-data-dir=$profile",
       "--window-size=$W,$H", "--window-position=20,20", "--no-first-run"
  $hwnd = [IntPtr]::Zero
  for ($i = 0; $i -lt 40 -and $hwnd -eq [IntPtr]::Zero; $i++) { Start-Sleep -Milliseconds 250
    $hwnd = (Get-Process | Where-Object { $_.MainWindowTitle -eq "Signal Status" } | Select-Object -First 1).MainWindowHandle }
  if ($hwnd) { [W]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0003) | Out-Null }   # HWND_TOPMOST, keep size/pos
  # Watch by window title (Edge/Chrome hand off to a child process); reopen when it disappears.
  do { Start-Sleep -Seconds 15; Sync
       $alive = Get-Process | Where-Object { $_.MainWindowTitle -eq "Signal Status" } } while ($alive)
  Start-Sleep -Seconds 3
}
