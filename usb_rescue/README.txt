CLAUDE RESCUE USB - QUICK GUIDE (Xubuntu 22.04 LTS)
=====================================================
USB: Drive D:  |  Windows 11 Home x64  |  UEFI + Legacy BIOS

DOWNLOAD:
  https://raw.githubusercontent.com/EndoScorpion/Signal/relay/usb_rescue/make_rescue_usb.bat

STEP 1 - FLASH THE USB (Windows)
---------------------------------
1. Insert USB drive (Drive D:)
2. Right-click make_rescue_usb.bat -> "Run as administrator"
3. All prompts run hidden/minimized; confirm the erase warning
4. Wait ~15-20 min (downloads ~2.7GB ISO + flashes)
5. Eject USB safely when done

STEP 2 - BOOT FROM USB (Lenovo)
---------------------------------
1. Shut down laptop
2. Insert USB
3. Power on, immediately press F12 (boot menu) or F2 (BIOS)
4. Select USB from list
5. Choose "Try Xubuntu without installing"

STEP 3 - FIRST BOOT SETUP
---------------------------
Open terminal (Ctrl+Alt+T) and run:
  bash /cdrom/ubuntu_claude_setup.sh

Installs: Node 20, claude-code CLI, Firefox, Tampermonkey, Claude Field Colors, git, python3

STEP 4 - USE CLAUDE
--------------------
  Type: claude
  Enter API key on first run

  To activate Field Colors in Firefox:
    Drag ~/.tampermonkey_scripts/claude_field_colors.user.js into Firefox
    Tampermonkey will intercept and offer to install it.

NOTES
-----
- Xubuntu runs live from USB; nothing written to Windows HDD
- API key stored in ~/.claude/ on USB only
- Defender cannot touch Linux processes

FILES
-----
  make_rescue_usb.bat       <- Run on Windows to build the USB
  ubuntu_claude_setup.sh    <- Run on Xubuntu for Claude + Firefox setup
  README.txt                <- This file
