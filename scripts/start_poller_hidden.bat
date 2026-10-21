@echo off
:: start_poller_hidden.bat — launches poller via VBS so no CMD window stays visible
:: Can also be called directly; CMD window flashes briefly then closes.
wscript.exe "%~dp0start_poller_hidden.vbs"
