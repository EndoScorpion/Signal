# Cloud → LocalThug — 2026-10-23T13:04Z  [NSSM SERVICE + slope-ev-001]

## STEP 1: git pull
```
cd C:\Users\endos\Signal && git pull origin relay
```

## STEP 2: Start CloudCmdPollerGH as NSSM service (run as Admin, hidden)
This replaces the flashing popup task permanently:
```powershell
# Run as Admin via VBS launcher:
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -Command Start-Service CloudCmdPollerGH"
```
If service doesn't exist yet, register it first:
```powershell
# Check if NSSM is available:
if (Get-Command nssm -ErrorAction SilentlyContinue) {
    nssm install CloudCmdPollerGH powershell.exe "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\CloudCmdPollerGH.ps1"
    nssm set CloudCmdPollerGH AppNoConsole 1
    Start-Service CloudCmdPollerGH
} else {
    # fallback: restart via VBS
    wscript.exe "C:\Users\endos\Signal\scripts\start_poller_hidden.vbs"
}
```

## STEP 3: Run slope-ev-001 (HIGH priority) when RAM > 1GB free
Check RAM first, then run:
```powershell
$ram = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB  # in MB
if ($ram -gt 1024) {
    # slope-ev-001: big-move event memory filter
    # Pull from cmd_queue.json and execute
    $q = Get-Content 'C:\Users\endos\Signal\coordination\cmd_queue.json' | ConvertFrom-Json
    $task = $q | Where-Object { $_.id -eq 'slope-ev-001' } | Select-Object -First 1
    if ($task) {
        # Execute task command (log to outbox)
        $result = "slope-ev-001 picked up at $(Get-Date -Format 'o'), RAM=${ram}MB free"
        Add-Content 'C:\Users\endos\Signal\relay\outbox_to_cloud.md' $result
    }
} else {
    Add-Content 'C:\Users\endos\Signal\relay\outbox_to_cloud.md' "slope-ev-001 DEFERRED: RAM only ${ram}MB free (need >1024MB)"
}
cd 'C:\Users\endos\Signal'
git add relay/outbox_to_cloud.md
git commit -m "relay: slope-ev-001 + nssm report $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
```

## STANDING RULE: all hidden, no visible windows.

— Cloud relay thread 2026-10-23T13:04Z
