@echo off
:: CLEAN_FXT.bat — delete all *.fxt from MT4 tester history to free disk
:: Run as admin (self-elevates)

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  powershell -Command "Start-Process '%~f0' -Verb RunAs"
  exit /b
)

echo Deleting *.fxt files from MT4 tester history...
set COUNT=0
for /d %%T in ("C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\*") do (
  for %%F in ("%%T\tester\history\*.fxt") do (
    del /F /Q "%%F" 2>nul
    set /a COUNT+=1
  )
)
echo Done. Files removed.
pause
