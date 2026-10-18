Signal GitHub Relay - Script Bundle
=====================================

All scripts are idempotent (safe to run multiple times).
Run as Administrator for service install steps.

QUICK START (run in order):
  1. 01_clone_signal.bat         - Clone/update Signal repo, checkout relay branch
  2. 02_install_nssm_service.bat - Install CloudCmdPollerGH Windows service
  3. 08_quick_test.bat           - Send a test command, verify it comes back

ALL SCRIPTS:
  00_INSTALL_ALL.bat             - Runs all steps in order (master installer)
  01_clone_signal.bat            - Clone/update Signal repo
  02_install_nssm_service.bat    - Install poller as Windows service via NSSM
  03_patch_claude_settings.ps1   - Patch Claude Code settings.json (allow tools, no VS Code needed)
  04_mt4_launcher.bat            - Launch MT4 terminal (searches common paths)
  05_dc_remote_launcher.bat      - Start Desktop Commander remote server
  06_create_shortcuts.bat        - Create Desktop shortcuts for common tasks
  07_poller_status.bat           - Show service status + recent logs
  08_quick_test.bat              - Send Get-Date test command via relay

SERVICE MANAGEMENT:
  Start:   sc start CloudCmdPollerGH
  Stop:    sc stop CloudCmdPollerGH
  Remove:  nssm remove CloudCmdPollerGH confirm
  Logs:    C:\Users\endos\Desktop\hst_out\cmd_poller_svc.log

PATHS:
  Repo:    C:\Users\endos\Desktop\hst_work\Signal
  Logs:    C:\Users\endos\Desktop\hst_out\
  NSSM:    C:\Users\endos\Desktop\hst_work\Signal\relay\nssm.exe
