@echo off
:: DC Remote autostart — hidden window, runs at login
:: Place in: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
start "DCRemote" /min cmd /c "npx @wonderwhy-er/desktop-commander@latest remote >> %USERPROFILE%\dc_remote.log 2>&1"
