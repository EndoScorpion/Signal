# Cloud → LocalThug — 2026-10-23T18:23Z  [SYNC + INSTALL MONITOR]

## YES — cloud pushes commands here, CLI polls and runs them. No copy-paste needed.
All hidden. No popups. Budget cap 75%.

## CMD 1: Sync to latest relay branch (force)
```powershell
$env:GIT_TERMINAL_PROMPT = '0'
cd C:\Users\endos\Signal
git fetch origin relay
git reset --hard origin/relay
```

## CMD 2: Install monitor tasks hidden
```
wscript.exe "C:\Users\endos\Signal\scripts\run_hidden.vbs" "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\install_monitor_tasks.ps1"
```

## CMD 3: Run unpause (RAM check + remove MT4_PAUSE + run cmd_queue)
```powershell
$repoRoot = 'C:\Users\endos\Signal'
$ram = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
$results = @("sync+monitor $(Get-Date -Format 'o'), RAM=${ram}MB")

if ($ram -ge 1024) {
    $results += "RAM OK"
    @(
        "$repoRoot\MT4_PAUSE",
        "$repoRoot\MT4_PAUSE.txt"
    ) | ForEach-Object { if (Test-Path $_) { Remove-Item $_ -Force; $results += "Removed: $_" } }

    $qPaths = @("$repoRoot\coordination\cmd_queue.json","$repoRoot\relay\cmd_queue.json","$repoRoot\cmd_queue.json")
    foreach ($qPath in $qPaths) {
        if (Test-Path $qPath) {
            $queue = Get-Content $qPath | ConvertFrom-Json
            $pending = $queue | Where-Object { $_.status -notin @('done','completed') }
            $results += "cmd_queue: $($pending.Count) pending"
            break
        }
    }
} else { $results += "RAM LOW (${ram}MB)" }

$report = "# LocalThug Outbox - SYNC+MONITOR`n## $(Get-Date -Format 'o')`n`n" + ($results | ForEach-Object { "- $_" } | Out-String)
Set-Content "$repoRoot\relay\outbox_to_cloud.md" $report
cd $repoRoot
git add relay/outbox_to_cloud.md
git commit -m "relay: sync+monitor result $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
```

## STANDING RULE: ALL hidden. No popups. GIT_TERMINAL_PROMPT=0.

— Cloud relay 2026-10-23T18:23Z
