@echo off
echo ===== SIGNAL STABILIZE v2 =====
echo Run as Administrator

echo [1/7] Killing nssm and node...
taskkill /f /im nssm.exe 2>nul
taskkill /f /im node.exe 2>nul
echo Done.

echo [2/7] Disabling ALL Claude-created scheduled tasks...
schtasks /Change /TN "Cloud_DC_Watchdog" /Disable 2>nul
schtasks /Change /TN "DCRemoteService" /Disable 2>nul
schtasks /Change /TN "RamWatchdog" /Disable 2>nul
schtasks /Change /TN "RelayAutoSync" /Disable 2>nul
schtasks /Change /TN "ClaudePWAStartup" /Disable 2>nul
schtasks /Change /TN "ClaudeAutoRC" /Disable 2>nul
echo Done.

echo [3/7] Removing Claude startup registry entries...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "ClaudeRC" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "ClaudeAutoRC" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DCRemote" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "RamWatchdog" /f 2>nul
echo Done.

echo [4/7] Locking page file at 8192/16384 MB...
powershell -ExecutionPolicy Bypass -Command "Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' -Name PagingFiles -Value 'C:\pagefile.sys 8192 16384'"
echo Done.

echo [5/7] Disabling Windows notification popups...
powershell -ExecutionPolicy Bypass -Command "Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\PushNotifications' -Name ToastEnabled -Value 0 -Type DWord"
echo Done.

echo [6/7] Writing lean Claude Desktop config...
powershell -ExecutionPolicy Bypass -Command "$p=[System.Environment]::GetFolderPath('ApplicationData')+'\Claude\claude_desktop_config.json'; $c='{\"mcpServers\":{\"desktop-commander\":{\"command\":\"npx\",\"args\":[\"-y\",\"@wonderwhy-er/desktop-commander@latest\"]}}}'; Set-Content -Path $p -Value $c -Encoding UTF8; Write-Host 'Config written to' $p"

echo [7/7] Verifying page file...
powershell -ExecutionPolicy Bypass -Command "Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' | Select PagingFiles"

echo ===== ALL DONE =====
echo Tasks disabled, RAM hogs killed, page file locked, lean Desktop config written.
echo Reboot when ready to apply fully.
pause
