@echo off
:: Claude Rescue USB Creator - Ventoy multiboot + Xubuntu 22.04 LTS
:: Run as Administrator. Drive D = USB target.
:: Ventoy lets you copy multiple ISOs to the USB for a multiboot menu.
:: Download URL: https://raw.githubusercontent.com/EndoScorpion/Signal/relay/usb_rescue/make_rescue_usb.bat

setlocal

set WORKDIR=%TEMP%\claude_usb_work
set VENTOY_ZIP=%WORKDIR%\ventoy.zip
set VENTOY_DIR=%WORKDIR%\ventoy
set ISO_URL=https://mirror.nl.leaseweb.net/ubuntu-releases/xubuntu/22.04.3/xubuntu-22.04.3-desktop-amd64.iso
set ISO_FILE=%WORKDIR%\xubuntu-22.04.3-desktop-amd64.iso
set SETUP_SRC=%~dp0ubuntu_claude_setup.sh

echo [1/5] Creating work directory...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "New-Item -ItemType Directory -Force -Path '%WORKDIR%' | Out-Null"

echo [2/5] Downloading Ventoy (latest portable for Windows)...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; $rel=(Invoke-RestMethod 'https://api.github.com/repos/ventoy/Ventoy/releases/latest'); $asset=$rel.assets | Where-Object {$_.name -like '*windows*.zip'} | Select-Object -First 1; (New-Object Net.WebClient).DownloadFile($asset.browser_download_url,'%VENTOY_ZIP%')"
if not exist "%VENTOY_ZIP%" (
    echo ERROR: Ventoy download failed. Check internet connection.
    pause & exit /b 1
)

echo [3/5] Extracting and installing Ventoy to drive D: (ERASES drive D)...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Expand-Archive -Path '%VENTOY_ZIP%' -DestinationPath '%VENTOY_DIR%' -Force"
for /r "%VENTOY_DIR%" %%f in (Ventoy2Disk.exe) do set VENTOY2DISK=%%f
if not defined VENTOY2DISK (
    echo ERROR: Ventoy2Disk.exe not found after extraction.
    pause & exit /b 1
)
echo WARNING: ALL DATA ON DRIVE D: WILL BE ERASED.
echo Press Ctrl+C to cancel, or any key to continue...
pause
"%VENTOY2DISK%" /I D:
if errorlevel 1 (
    echo WARNING: Ventoy install returned error. Drive D: may still be bootable.
)

echo [4/5] Downloading Xubuntu 22.04 LTS ISO (~2.7GB, wait 10-20 min)...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; (New-Object Net.WebClient).DownloadFile('%ISO_URL%','%ISO_FILE%')"
if not exist "%ISO_FILE%" (
    echo ERROR: ISO download failed.
    pause & exit /b 1
)
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Copy-Item '%ISO_FILE%' 'D:\xubuntu-22.04.3-desktop-amd64.iso' -Force"

echo [5/5] Copying ubuntu_claude_setup.sh to USB...
if exist "%SETUP_SRC%" (
    powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Copy-Item '%SETUP_SRC%' 'D:\ubuntu_claude_setup.sh' -Force"
)

echo.
echo Done! Ventoy multiboot USB ready on drive D.
echo.
echo To add more ISOs (e.g. Windows 11):
echo   1. Download ISO: https://www.microsoft.com/software-download/windows11
echo   2. Copy the .iso file to drive D:\
echo   Ventoy will show all ISOs in a boot menu automatically.
echo.
echo Boot from D:, select Xubuntu, then run: bash /cdrom/ubuntu_claude_setup.sh
echo.
pause
endlocal
