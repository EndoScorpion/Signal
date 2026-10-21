# Watchdog Startup Fix — 2026-10-21

## Problem

`Windows Script Host: Execution failed. (Not enough memory resources available.)`

Watchdog fires too early at boot before RAM is fully available.

## Fix: Add startup delay

In the watchdog `.ps1` or `.vbs` startup script, add a 30-second delay at the top:

### PowerShell (`Cloud_DC_Watchdog.ps1` or similar):

```powershell
# Add at the very top, before anything else:
Start-Sleep -Seconds 30

# ... rest of script follows ...
```

### VBScript (`.vbs` in Startup folder):

```vbscript
' Add at the very top:
WScript.Sleep 30000

' ... rest of script follows ...
```

### Task Scheduler (preferred — no script edit needed):

In Task Scheduler → Cloud_DC_Watchdog → Triggers:
- Add delay: "Delay task for: 30 seconds" under the "At startup" trigger settings
- Or change trigger from "At startup" to "At logon + delay 30 seconds"

## Apply

1. Open Task Scheduler
2. Find `Cloud_DC_Watchdog`
3. Edit trigger → check "Delay task for" → set 30 seconds
4. Save

No script file edit needed if using Task Scheduler delay setting.

## Notes

- 30s is conservative; 15s may be enough on this machine
- If still failing, increase to 60s
- Alternative: set task to retry on failure (Settings tab → "If task fails, restart every: 1 minute, up to 3 times")
