Claude CLI Boot USB — D:\claude_boot\
======================================

BOOT INSTRUCTIONS (Lenovo IdeaPad Slim 3 — press F12 at startup)
-----------------------------------------------------------------
1. Plug in the Ventoy USB drive
2. POWER OFF completely (not sleep/restart)
3. Power ON and IMMEDIATELY press F12 repeatedly (before Windows logo)
   - If F12 fails: try Fn+F12
   - If Fast Startup blocks F12: hold Shift + Restart in Windows
     then: Troubleshoot > Advanced > Use a Device > USB
4. Boot menu appears — select USB drive (shows as Ventoy or USB brand)
5. Ventoy menu — pick:
   - Kali Linux 2026.3  (already on USB)
   - Ubuntu 24.04 LTS   (see UBUNTU ISO section below)
6. Wait for live desktop to load
7. Open terminal (Ctrl+Alt+T or right-click desktop)
8. Run the autostart script:
   - Kali:   bash /cdrom/claude_boot/kali_claude.sh
   - Ubuntu: bash /cdrom/claude_boot/ubuntu_claude.sh

FILES IN THIS FOLDER
--------------------
kali_claude.sh    — installs Node.js + Claude CLI, reads key.txt, launches claude (Kali)
ubuntu_claude.sh  — same for Ubuntu
key.txt           — YOUR ANTHROPIC_API_KEY goes here (create this yourself, one line)
BOOT_KEY.txt      — quick F12 reminder card (print or keep on phone)
README.txt        — this file

FIRST-TIME SETUP
----------------
Create D:\claude_boot\key.txt containing only your ANTHROPIC_API_KEY:
  sk-ant-...

The scripts read it automatically on boot.

UBUNTU ISO
----------
Download Ubuntu 24.04 LTS from: https://ubuntu.com/download/desktop
Copy the .iso file to D:\ (root of Ventoy USB) — Ventoy auto-detects it.

NOTES
-----
- Ventoy USB at D: already has Kali 2026.3 — no extra steps for Kali.
- NO Windows boot files are modified. F12 is a hardware boot menu, 100% safe.
- Internet required on first boot to install Node.js + claude CLI (apt-get + npm).
- key.txt stays on the USB and is never uploaded anywhere.
