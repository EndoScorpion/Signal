@echo off
setlocal
set BACKUP=C:\Users\endos\Desktop\claude_backup\%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set BACKUP=%BACKUP: =0%
mkdir "%BACKUP%" 2>nul

echo === BACKUP: processes ===
tasklist /FO CSV > "%BACKUP%\processes.csv"

echo === BACKUP: Claude Desktop config ===
if exist "%APPDATA%\Claude\claude_desktop_config.json" copy "%APPDATA%\Claude\claude_desktop_config.json" "%BACKUP%\claude_desktop_config.json.bak"

echo === BACKUP: page file registry ===
powershell -Command "Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' | Out-File '%BACKUP%\pagefile_reg.txt'"

echo === 1. Lock page file in registry ===
powershell -ExecutionPolicy Bypass -Command "$mm = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'; Set-ItemProperty -Path $mm -Name PagingFiles -Value 'C:\pagefile.sys 8192 16384'; Set-ItemProperty -Path $mm -Name AutomaticManagedPagefile -Value 0" && echo Page file locked OK

echo === 2. Drop rc_keep_alive.bat on Desktop ===
(
echo @echo off
echo :loop
echo tasklist /FI "IMAGENAME eq node.exe" ^| find /I "node.exe" ^>nul 2^>^&1
echo if errorlevel 1 (
echo   cd /d "C:\Users\endos\Signal"
echo   start /min "" cmd /c "npx @wonderwhy-er/desktop-commander@latest remote"
echo )
echo timeout /t 30 /nobreak ^>nul
echo goto loop
) > "C:\Users\endos\Desktop\rc_keep_alive.bat"
echo RC keep-alive written to Desktop

echo === 3. Kill nssm / stray node RAM hogs ===
for /f "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq nssm.exe" /NH 2^>nul ^| findstr /v "INFO"') do taskkill /PID %%p /F 2>nul
echo nssm kill attempted

echo === 4. Disable toast notifications ===
powershell -ExecutionPolicy Bypass -Command "Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications' -Name ToastEnabled -Value 0 -Type DWord -Force" && echo Toasts disabled

echo === 5. Write lean Claude Desktop config ===
powershell -ExecutionPolicy Bypass -Command "$cfg = '{\"mcpServers\":{\"desktop-commander\":{\"command\":\"npx\",\"args\":[\"-y\",\"@wonderwhy-er/desktop-commander@latest\"]}}}'; $path = $env:APPDATA + '\Claude'; if (!(Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }; $cfg | Out-File -FilePath ($path + '\claude_desktop_config.json') -Encoding utf8 -Force" && echo Claude Desktop config written

echo === 6. Confirm safe mode in boot menu ===
bcdedit /enum all | findstr /i "safeboot"
bcdedit /enum | findstr /i "description"
powershell -ExecutionPolicy Bypass -Command "$exists = (bcdedit /enum all | Select-String 'safeboot'); if (-not $exists) { bcdedit /copy '{current}' /d 'Safe Mode (Claude Recovery)' | Tee-Object -Variable newid; $id = ($newid -match '\{.*\}' | Out-Null); $matches[0]; bcdedit /set $matches[0] safeboot minimal } else { Write-Host 'Safe mode entry already exists' }"

echo.
echo === ALL DONE — backups at %BACKUP% ===
pause
