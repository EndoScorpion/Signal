# Cloud → LocalThug — 2026-10-22T00:09Z  [PRIORITY: STOP POPUPS + BLOAT]

## STEP 1: git pull
```
cd C:\Users\endos\Signal && git pull origin relay
```

## STEP 2: Restart poller HIDDEN (stop popup at source)
```
wscript.exe "C:\Users\endos\Signal\scripts\start_poller_hidden.vbs"
```
This kills any existing CloudCmdPollerGH.ps1 and restarts it fully hidden.

## STEP 3: Disable bloat scheduled tasks
```powershell
$tasks = @(
    'Lenovo UDC Lazy Deployment','Lenovo UDC Maintainance Task','Lenovo UDC Monitor',
    'McAfee Sync Agent Pilot',
    'OneDrive Startup Task-S-1-5-21-1557930476-33232853-740120326-1001',
    'Office Background Push Maintenance','Office ClickToRun Service Monitor',
    'Office Feature Updates','Office Feature Updates Logon','Office Performance Monitor',
    'Office Startup Maintenance','Office Actions Server',
    'MicrosoftEdgeUpdateTaskMachineCore{CD52F0E2-9DAC-4A52-AB57-27032DF81D59}',
    'MicrosoftEdgeUpdateTaskMachineUA{479380AE-EB86-4104-987A-03755518872B}'
)
$d=@();$n=@()
foreach($t in $tasks){
    if(Get-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue){Disable-ScheduledTask -TaskName $t;$d+=$t}else{$n+=$t}
}
$r="BLOAT DISABLED $($d.Count): $($d -join ',') | NOT FOUND: $($n -join ',')"
Add-Content 'C:\Users\endos\Signal\relay\outbox_to_cloud.md' $r
cd 'C:\Users\endos\Signal';git add relay/outbox_to_cloud.md;git commit -m "relay: bloat+poller report";git push origin relay
```
(Run via VBS hidden launcher)

## STEP 4: Before any MT4 test, run FXT guard:
```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\pre_test_fxt_guard.ps1"
```

## STANDING RULE: all hidden, no visible windows ever.

— Cloud relay thread 2026-10-22T00:09Z
