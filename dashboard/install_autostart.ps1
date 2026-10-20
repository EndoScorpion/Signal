# Registers a logon task that runs the launcher hidden. Run once: powershell -ExecutionPolicy Bypass -File install_autostart.ps1
$l = Join-Path $PSScriptRoot "launch_dashboard.ps1"
schtasks /Create /F /TN "SignalDashboard" /SC ONLOGON /RL LIMITED /TR "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$l`""
schtasks /Run /TN "SignalDashboard"
