@echo off
schtasks /Delete /TN ClaudeRAMTrimLoop /F 2>nul
schtasks /Create /TN ClaudeRAMTrimLoop /TR "wscript.exe \"C:\Users\endos\Signal\relay\run_hidden.vbs\" \"C:\Users\endos\Signal\relay\ram_trim_boot.ps1\"" /SC ONLOGON /RL HIGHEST /F
schtasks /Delete /TN RelayAutoSync /F 2>nul
schtasks /Create /TN RelayAutoSync /TR "wscript.exe \"C:\Users\endos\Signal\relay\run_hidden.vbs\" \"C:\Users\endos\Signal\relay\relay_sync.ps1\"" /SC ONLOGON /RL HIGHEST /F
schtasks /Delete /TN Cloud_DC_Watchdog /F 2>nul
schtasks /Create /TN Cloud_DC_Watchdog /TR "wscript.exe \"C:\Users\endos\Signal\relay\run_hidden.vbs\" \"C:\Users\endos\Signal\relay\dc_watchdog.ps1\"" /SC ONLOGON /RL HIGHEST /F
echo rereg_done > "%USERPROFILE%\Signal\relay\rereg_done.txt"
