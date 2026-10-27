@echo off
:: Claude Rescue USB Creator - Xubuntu 22.04 LTS (lightweight)
:: Run as Administrator. Drive D = USB target.
:: Downloads Rufus portable + Xubuntu ISO, flashes D:, copies setup script.
:: Download URL: https://raw.githubusercontent.com/EndoScorpion/Signal/relay/usb_rescue/make_rescue_usb.bat

setlocal

set WORKDIR=%TEMP%\claude_usb_work
set RUFUS_URL=https://github.com/pbatard/rufus/releases/download/v4.5/rufus-4.5p.exe
set ISO_URL=https://mirror.nl.leaseweb.net/ubuntu-releases/xubuntu/22.04.3/xubuntu-22.04.3-desktop-amd64.iso
set RUFUS=%WORKDIR%\rufus.exe
set ISO=%WORKDIR%\xubuntu-22.04.3-desktop-amd64.iso
set SETUP_SRC=%~dp0ubuntu_claude_setup.sh

echo [1/5] Creating work directory...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "New-Item -ItemType Directory -Force -Path '%WORKDIR%' | Out-Null"

echo [2/5] Downloading Rufus portable (silent)...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; (New-Object Net.WebClient).DownloadFile('%RUFUS_URL%','%RUFUS%')"
if not exist "%RUFUS%" (
    echo ERROR: Rufus download failed. Check internet connection.
    pause & exit /b 1
)

echo [3/5] Downloading Xubuntu 22.04 LTS ISO (about 2.7GB, wait 10-20 min)...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; (New-Object Net.WebClient).DownloadFile('%ISO_URL%','%ISO%')"
if not exist "%ISO%" (
    echo ERROR: ISO download failed.
    pause & exit /b 1
)

echo [4/5] Copying ubuntu_claude_setup.sh to work area...
if exist "%SETUP_SRC%" (
    powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Copy-Item '%SETUP_SRC%' '%WORKDIR%\ubuntu_claude_setup.sh' -Force"
)

echo [5/5] Flashing drive D: with Rufus (UEFI+legacy BIOS, GPT/MBR auto)...
echo WARNING: ALL DATA ON DRIVE D: WILL BE ERASED.
echo Press Ctrl+C to cancel or any key to continue...
pause
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process -FilePath '%RUFUS%' -ArgumentList '/iso=%ISO% /drive=D /format /IgnoreBootErrors' -WindowStyle Hidden -Wait"

echo.
echo Done! Xubuntu USB ready on drive D.
echo Eject safely, reboot, press F12 for boot menu.
echo After booting: open terminal ^(Ctrl+Alt+T^) and run:  bash /cdrom/ubuntu_claude_setup.sh
echo.
pause
endlocal
