@echo off
:: 04_mt4_launcher.bat - Launch MT4 terminal
:: Checks common install paths; add your own if different.

set FOUND=0

for %%P in (
    "C:\Program Files (x86)\MetaTrader 4\terminal.exe"
    "C:\Program Files\MetaTrader 4\terminal.exe"
    "C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\*\terminal.exe"
    "C:\MT4\terminal.exe"
    "C:\Users\endos\Desktop\MT4\terminal.exe"
) do (
    if exist %%P (
        echo [OK] Launching MT4: %%P
        start "" %%P
        set FOUND=1
        goto :done
    )
)

:: Try searching via where
where terminal.exe >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo [OK] Launching MT4 from PATH...
    start "" terminal.exe
    set FOUND=1
    goto :done
)

:: Search in AppData MetaQuotes dirs
powershell -NonInteractive -Command "Get-ChildItem $env:APPDATA\MetaQuotes\Terminal -Recurse -Filter terminal.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName" > "%TEMP%\mt4path.txt" 2>nul
set /p MT4PATH=<"%TEMP%\mt4path.txt"
if defined MT4PATH if exist "%MT4PATH%" (
    echo [OK] Launching MT4: %MT4PATH%
    start "" "%MT4PATH%"
    set FOUND=1
    goto :done
)

:done
if %FOUND% == 0 (
    echo [ERROR] MT4 terminal.exe not found.
    echo         Add your install path to this script.
    pause
)
