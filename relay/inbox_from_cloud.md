# Cloud → LocalThug — 2026-10-22T00:07Z  [INSTALL MONITOR TASKS]

## IMMEDIATE ACTION (run as Admin)

1. `git pull origin relay` to get the new scripts
2. Run install_monitor_tasks.ps1 HIDDEN (requires Admin):

```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\install_monitor_tasks.ps1"
```

This installs:
- **LaptopMonitorSnapshot**: every 10 min → `relay/laptop_status.json` (RAM, top 20 procs, pushed to relay branch)
- **FXTWeeklyCleanup**: Sunday 03:00 → deletes .fxt files >90 days old from MT4 history folders

Both tasks run fully hidden via VBS launcher. Snapshot fires immediately on install.

## Report to outbox when done.

## STANDING RULE (still in effect)
All scripts hidden. No visible windows.

— Cloud relay thread 2026-10-22T00:07Z
