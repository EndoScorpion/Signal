@echo off
REM Emergency git pull - silent, no relay dependency
REM Run this to manually sync relay branch to laptop
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command "cd 'C:\Users\endos\Signal'; git fetch origin relay; git checkout relay; git pull origin relay" >nul 2>&1
echo Done. Relay branch pulled to C:\Users\endos\Signal
