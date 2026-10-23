@echo off
:: RAMWatchdog — runs every 5 min via schtasks, no window
:: Checks free RAM; if <2GB kills MT4 + writes alert to from_cli.json
:: Also runs FXT cleanup on every execution

setlocal

:: ---- RAM CHECK ----
for /f "tokens=2 delims==" %%M in ('wmic OS get FreePhysicalMemory /value ^| find "="') do set FREE_KB=%%M
set /a FREE_MB=%FREE_KB% / 1024

set RELAY_DIR=C:\Users\endos\Signal\relay
set FXT_GLOB=C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal

:: ---- FXT CLEANUP (always) ----
for /d %%T in ("%FXT_GLOB%\*") do (
  del /F /Q "%%T\tester\history\*.fxt" 2>nul
)

:: ---- LOW RAM ACTION ----
if %FREE_MB% LSS 2048 (
  :: Kill MT4 silently
  taskkill /F /IM terminal64.exe /T >nul 2>&1
  taskkill /F /IM terminal.exe /T >nul 2>&1
  :: Write alert to from_cli.json
  echo {"alert":"LOW_RAM","free_mb":%FREE_MB%,"mt4_killed":true,"ts":"%DATE% %TIME%"} > "%RELAY_DIR%\from_cli.json"
) else (
  :: Write status (no alert)
  echo {"alert":"OK","free_mb":%FREE_MB%,"ts":"%DATE% %TIME%"} > "%RELAY_DIR%\from_cli.json"
)

endlocal
