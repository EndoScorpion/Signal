CLAUDE BOOT USB - README
========================

1. Boot from this USB into Kali or Xubuntu Live.
2. Open a terminal.
3. Navigate to this folder:
     cd /media/<user>/VENTOY/claude_boot/
   or wherever the USB is mounted.
4. Run the appropriate script:
     Kali:   sudo bash kali_claude.sh
     Ubuntu: bash ubuntu_claude.sh
5. The script will install Node.js + Claude Code CLI and launch Claude.
6. Log in with your Anthropic account when prompted.

Notes:
- Requires internet connection on first run (installs Node.js + npm package).
- Claude config/history is not persisted across live reboots.
- For persistent config, run from an installed OS or a persistent partition.
