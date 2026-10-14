@echo off
:: Double-click to open the ClaudeHub master. Uses Windows Terminal if installed (Ctrl+V paste works there).
where wt >nul 2>nul && (
  wt -d "%~dp0" powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0start_master.ps1" %*
) || (
  powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0start_master.ps1" %*
)
