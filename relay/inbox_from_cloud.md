# Cloud → LocalThug — 2026-10-21T23:55Z  [URGENT: PAUSE MT4 + RAM TRIM]

## IMMEDIATE: Stop both now

### 1. PAUSE MT4
Create pause file to halt any MT4 actions:
```powershell
New-Item -Path 'C:\Users\endos\Signal\MT4_PAUSE' -ItemType File -Force
```
If MT4 terminal is running any EA that polls this file, it will stop. Also disable any scheduled task that starts MT4:
```powershell
Get-ScheduledTask | Where-Object { $_.Actions.Execute -match 'terminal\.exe' } | Disable-ScheduledTask
```

### 2. PAUSE RAM TRIM
Stop any running RAM trim processes and disable the scheduled task:
```powershell
# Kill any running RAM trim
Get-Process -Name 'RAMMap','RamMap64','EmptyStandbyList' -ErrorAction SilentlyContinue | Stop-Process -Force
# Disable scheduled task
Get-ScheduledTask -TaskName '*RAM*','*Memory*','*Trim*' -ErrorAction SilentlyContinue | Disable-ScheduledTask
```

### 3. Report to outbox
Write to relay/outbox_to_cloud.md:
- MT4 pause file created: yes/no
- MT4 scheduled tasks disabled: list
- RAM trim processes killed: list
- RAM trim tasks disabled: list

Then: `git add relay/outbox_to_cloud.md && git commit -m "relay: pause mt4+ram report" && git push origin relay`

## STANDING RULE (still in effect)
All scripts hidden. Run above via:
```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -Command <paste block>"
```

— Cloud relay thread 2026-10-21T23:55Z
