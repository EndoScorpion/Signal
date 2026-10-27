@echo off
:: Claude Rescue USB Creator - Run as Administrator
:: Flashes drive D: with Ubuntu 22.04 Server + Claude CLI auto-setup
:: Requirements: Drive D: inserted, admin rights, internet

setlocal
set WORKDIR=%TEMP%\claude_usb_work
set RUFUS_URL=https://github.com/pbatard/rufus/releases/download/v4.5/rufus-4.5p.exe
set ISO_URL=https://releases.ubuntu.com/22.04/ubuntu-22.04.5-live-server-amd64.iso
set RUFUS=%WORKDIR%\rufus.exe
set ISO=%WORKDIR%\ubuntu-22.04.5-live-server-amd64.iso
set SETUP_SRC=%~dp0ubuntu_claude_setup.sh

echo [1/5] Creating work directory...
if not exist "%WORKDIR%" mkdir "%WORKDIR%"

echo [2/5] Downloading Rufus portable (silent)...
powershell -WindowStyle Hidden -Command "& { Invoke-WebRequest -Uri '%RUFUS_URL%' -OutFile '%RUFUS%' -UseBasicParsing }"
if not exist "%RUFUS%" (
    echo ERROR: Rufus download failed. Check internet connection.
    pause
    exit /b 1
)

echo [3/5] Downloading Ubuntu 22.04 Server ISO (~1.5GB, please wait ~5-10 min)...
powershell -WindowStyle Hidden -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%ISO_URL%' -OutFile '%ISO%' -UseBasicParsing }"
if not exist "%ISO%" (
    echo ERROR: ISO download failed.
    pause
    exit /b 1
)

echo [4/5] Copying setup script to USB work area...
if exist "%SETUP_SRC%" (
    copy /Y "%SETUP_SRC%" "%WORKDIR%\ubuntu_claude_setup.sh" >nul
)

echo [5/5] Flashing drive D: with Rufus (this will ERASE drive D:)...
echo WARNING: All data on drive D: will be destroyed.
echo Press Ctrl+C now to cancel, or any key to continue...
pause

:: Rufus portable CLI: /iso=<path> /drive=<letter> /format /write (no GUI prompt)
:: Note: Rufus 4.x uses /iso /drive flags; runs silently with /IgnoreBootErrors
"%RUFUS%" /iso="%ISO%" /drive=D /format /IgnoreBootErrors

echo.
echo Done! Drive D: is now a bootable Ubuntu USB.
echo.
echo NEXT STEPS:
echo   1. Safely eject drive D:
echo   2. Reboot laptop, press F12 for boot menu
echo   3. Select USB drive
echo   4. Follow README.txt for post-boot Claude setup
echo.
pause
