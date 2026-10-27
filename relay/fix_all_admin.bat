@echo off
echo === Signal Laptop Fix-All ===
echo Running Defender exclusions...
powershell -ExecutionPolicy Bypass -Command "Add-MpPreference -ExclusionProcess 'node.exe'; Add-MpPreference -ExclusionPath 'C:\Users\endos\Signal'; Add-MpPreference -ExclusionPath '%APPDATA%\npm'; Add-MpPreference -ExclusionPath '%LOCALAPPDATA%\npx'; Write-Host 'Defender: done'"
echo.
echo Re-registering Cloud_DC_Watchdog...
schtasks /Delete /TN Cloud_DC_Watchdog /F 2>nul
schtasks /Create /TN Cloud_DC_Watchdog /TR "wscript.exe C:\Users\endos\Signal\relay\run_hidden.vbs C:\Users\endos\Signal\relay\dc_watchdog.ps1" /SC MINUTE /MO 15 /RL HIGHEST /F
echo Watchdog: done
echo.
echo Re-registering RelayAutoSync...
schtasks /Delete /TN RelayAutoSync /F 2>nul
schtasks /Create /TN RelayAutoSync /TR "wscript.exe C:\Users\endos\Signal\relay\run_hidden.vbs C:\Users\endos\Signal\relay\relay_autosync.ps1" /SC MINUTE /MO 5 /RL HIGHEST /F
echo RelayAutoSync: done
echo.
echo === ALL DONE - window stays open ===
cmd /k
