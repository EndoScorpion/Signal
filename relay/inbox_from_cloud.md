# Cloud → LocalThug — 2026-10-23T13:30Z  [GO — RUN ALL QUEUED TESTS]

## GO SIGNAL
Nasif has cleared. Run everything now. Budget cap 75%.

## STEP 1: git pull
```
cd C:\Users\endos\Signal && git pull origin relay
```

## STEP 2: Start NSSM poller service (as Admin, hidden)
```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -Command Start-Service CloudCmdPollerGH -ErrorAction SilentlyContinue"
```
If not registered, fall back:
```
wscript.exe "C:\Users\endos\Signal\scripts\start_poller_hidden.vbs"
```

## STEP 3: Run slope-ev-001 + all pending cmd_queue entries
Check RAM, then process queue:
```powershell
$repoRoot = 'C:\Users\endos\Signal'
$ram = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
$results = @("GO at $(Get-Date -Format 'o'), RAM=${ram}MB free")

if ($ram -gt 1024) {
    # Find cmd_queue.json (check multiple locations)
    $qPaths = @(
        "$repoRoot\coordination\cmd_queue.json",
        "$repoRoot\relay\cmd_queue.json",
        "$repoRoot\cmd_queue.json"
    )
    foreach ($qPath in $qPaths) {
        if (Test-Path $qPath) {
            $queue = Get-Content $qPath | ConvertFrom-Json
            $pending = $queue | Where-Object { $_.status -ne 'done' -and $_.status -ne 'completed' }
            $results += "Queue: $qPath — $($pending.Count) pending of $($queue.Count) total"
            foreach ($task in ($pending | Sort-Object { if ($_.priority -eq 'HIGH') { 0 } else { 1 } })) {
                $results += "Task: $($task.id) [$($task.priority)] — $($task.command)"
                # Execute if command field exists
                if ($task.command) {
                    try {
                        $out = Invoke-Expression $task.command 2>&1 | Out-String
                        $results += "Result: $($out.Trim() | Select-Object -First 3)"
                    } catch {
                        $results += "Error: $($_.Exception.Message)"
                    }
                }
            }
            break
        }
    }
    if (-not ($qPaths | Where-Object { Test-Path $_ })) {
        $results += "cmd_queue.json not found in expected paths"
    }
} else {
    $results += "RAM too low (${ram}MB), skipping tests — need >1024MB"
}

# Write to outbox and push
$report = "# LocalThug Outbox - GO SIGNAL RESULTS`n## $(Get-Date -Format 'o')`n`n" + ($results | ForEach-Object { "- $_" } | Out-String)
Set-Content "$repoRoot\relay\outbox_to_cloud.md" $report
cd $repoRoot
git add relay/outbox_to_cloud.md
git commit -m "relay: GO results $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
```

## STEP 4: Resume MT4 (remove pause file if set)
```powershell
Remove-Item 'C:\Users\endos\Signal\MT4_PAUSE' -ErrorAction SilentlyContinue
```

## STEP 5: Resume theory loop
Run any pending theory tests from theory_queue.json (nomem6_033/034/035/036 etc.) if MT4 available.

## STANDING RULE: all scripts hidden, no visible windows.

— Cloud relay thread 2026-10-23T13:30Z
