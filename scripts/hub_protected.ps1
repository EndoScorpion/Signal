# hub_protected.ps1 — endos-29 master hub launcher with exit guard
# Run as Admin. Wrap-restarts Claude Code; requires typed confirmation to close.

param(
    [switch]$New   # pass -New to start a fresh session instead of --continue
)

$ErrorActionPreference = 'SilentlyContinue'

function Set-HubColors {
    $Host.UI.RawUI.BackgroundColor = 'Black'
    $Host.UI.RawUI.ForegroundColor = 'Green'
    $Host.UI.RawUI.WindowTitle     = 'endos-29 HUB [master] *** DO NOT CLOSE ***'
    Clear-Host
}

function Show-Banner {
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║   endos-29  ·  MASTER HUB  ·  Signal EA  ║" -ForegroundColor Green
    Write-Host "  ║   FXOpen EURUSD ECN  ·  8pt commission   ║" -ForegroundColor DarkGreen
    Write-Host "  ║   Close guard ON  ·  type EXIT to quit   ║" -ForegroundColor DarkGreen
    Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
}

Set-HubColors
Show-Banner

$restarts = 0
while ($true) {
    if ($New -or $restarts -eq 0 -and -not (claude --version 2>$null)) {
        Write-Host "  [hub] Starting new Claude Code session..." -ForegroundColor DarkGreen
        claude
    } else {
        Write-Host "  [hub] Resuming last session (restart #$restarts)..." -ForegroundColor DarkGreen
        claude --continue
    }

    # Claude exited — ask before actually closing
    Set-HubColors
    Show-Banner
    Write-Host "  [hub] Claude Code exited." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Type  CLOSE  and press Enter to shut down the master hub." -ForegroundColor Red
    Write-Host "  Press Enter alone to restart it now." -ForegroundColor Green
    Write-Host ""
    $answer = Read-Host "  >"

    if ($answer.Trim().ToUpper() -eq 'CLOSE') {
        Write-Host "  [hub] Master hub closed. Goodbye." -ForegroundColor Red
        Start-Sleep 2
        break
    }

    $restarts++
    Set-HubColors
    Show-Banner
    Write-Host "  [hub] Restarting... (restart #$restarts)" -ForegroundColor Green
    Start-Sleep 1
}
