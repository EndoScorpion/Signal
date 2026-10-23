# Cloud → LocalThug — 2026-10-23T18:02Z  [GO + DC + GIT AUTH HIDDEN]

## NASIF APPROVALS: DC safe mode + minimized mode + all minimized git auth
All actions hidden. No visible windows. Git auth via credential store (no popup).

## STEP 0: Git auth hidden (FIRST — ensures all subsequent git ops work silently)
```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\git_auth_hidden.ps1"
```
This sets credential.helper=store, disables GUI prompts, tests fetch+push.

## STEP 1: git pull (get latest scripts)
```
cd C:\Users\endos\Signal && git pull origin relay
```

## STEP 2: Start NSSM poller service hidden
```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -Command Start-Service CloudCmdPollerGH -ErrorAction SilentlyContinue"
```
Fallback:
```
wscript.exe "C:\Users\endos\Signal\scripts\start_poller_hidden.vbs"
```

## STEP 3: Run popup_fix_v4
```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\popup_fix_v4.ps1"
```

## STEP 4: Restart DC safe mode hidden
```powershell
Get-Process -Name 'node','npx' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep 2
Start-ScheduledTask 'DcCloneServer' -ErrorAction SilentlyContinue
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" 'cmd /c npx @wonderwhy-er/desktop-commander@latest remote'
```

## STEP 5: Resume MT4
```powershell
Remove-Item 'C:\Users\endos\Signal\MT4_PAUSE' -ErrorAction SilentlyContinue
```

## STEP 6: Run slope-ev-001 + cmd_queue
```powershell
$repoRoot = 'C:\Users\endos\Signal'
$ram = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
$results = @("GO+DC at $(Get-Date -Format 'o'), RAM=${ram}MB free")

if ($ram -gt 1024) {
    $qPaths = @("$repoRoot\coordination\cmd_queue.json","$repoRoot\relay\cmd_queue.json","$repoRoot\cmd_queue.json")
    foreach ($qPath in $qPaths) {
        if (Test-Path $qPath) {
            $queue = Get-Content $qPath | ConvertFrom-Json
            $pending = $queue | Where-Object { $_.status -ne 'done' -and $_.status -ne 'completed' }
            $results += "Queue: $qPath - $($pending.Count) pending of $($queue.Count) total"
            foreach ($task in ($pending | Sort-Object { if ($_.priority -eq 'HIGH') { 0 } else { 1 } })) {
                $results += "Task: $($task.id) [$($task.priority)]"
                if ($task.command) {
                    try {
                        $out = Invoke-Expression $task.command 2>&1 | Out-String
                        $results += "Result: $(($out -split '`n')[0..2] -join ' ')"
                    } catch { $results += "Error: $($_.Exception.Message)" }
                }
            }
            break
        }
    }
} else { $results += "RAM too low (${ram}MB)" }

$report = "# LocalThug Outbox - GO+DC RESULTS`n## $(Get-Date -Format 'o')`n`n" + ($results | ForEach-Object { "- $_" } | Out-String)
Set-Content "$repoRoot\relay\outbox_to_cloud.md" $report
cd $repoRoot; git add relay/outbox_to_cloud.md
git commit -m "relay: GO+DC results $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
```

## STEP 7: Theory loop
nomem6_033/034/035/036 from theory_queue.json when MT4 ready.

## STANDING RULE: ALL hidden. No popups. GIT_TERMINAL_PROMPT=0.

— Cloud relay 2026-10-23T18:02Z
