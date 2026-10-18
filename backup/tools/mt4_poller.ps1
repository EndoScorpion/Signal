<#
.SYNOPSIS
    MT4 task queue poller for Signal repo.

.DESCRIPTION
    Loops on a configurable interval, pulls the Signal repo, reads
    tasks\safe_run_queue.md for pending [ ] tasks, runs run_tester.ps1
    for each one, marks tasks [x], commits and pushes results, and logs
    everything to results\mt4_poller_log.md.

.USAGE
    # Interactive
    .\mt4_poller.ps1

    # Dry run (no MT4, no git push)
    .\mt4_poller.ps1 -DryRun

    # Custom interval and repo path
    .\mt4_poller.ps1 -IntervalMinutes 10 -RepoPath "D:\Signal"

    # Run as a Scheduled Task — see mt4_poller_setup.md
#>

param(
    [string]  $RepoPath        = "C:\Users\endos\Desktop\Signal",
    [int]     $IntervalMinutes = 5,
    [switch]  $DryRun          = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$QueueFile  = Join-Path $RepoPath "tasks\safe_run_queue.md"
$LogFile    = Join-Path $RepoPath "results\mt4_poller_log.md"
$ActiveTask = Join-Path $RepoPath "tools\active_task.txt"
$Tester     = Join-Path $RepoPath "tools\run_tester.ps1"

function Write-Log {
    param([string]$TaskId, [string]$Status, [string]$Note = "")
    $ts   = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "| $ts | $TaskId | $Status | $Note |"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

function Get-RamOkay {
    $os    = Get-CimInstance Win32_OperatingSystem
    $pct   = ($os.FreePhysicalMemory / $os.TotalVisibleMemorySize) * 100
    return ($pct -ge 15), [math]::Round($pct, 1)
}

function Invoke-GitPull {
    Push-Location $RepoPath
    try {
        $out = git pull origin main 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "git pull failed, resetting to origin/main..."
            git fetch origin main 2>&1 | Out-Null
            git reset --hard origin/main 2>&1 | Out-Null
        }
    } finally {
        Pop-Location
    }
}

function Get-PendingTasks {
    if (-not (Test-Path $QueueFile)) { return @() }
    $lines = Get-Content $QueueFile
    $tasks = @()
    foreach ($line in $lines) {
        if ($line -match '^\s*-\s*\[ \]\s+(\S+):\s*(.*)$') {
            $tasks += [PSCustomObject]@{ Id = $Matches[1]; Desc = $Matches[2]; Line = $line }
        }
    }
    return $tasks
}

function Mark-TaskDone {
    param([string]$TaskId)
    $content = Get-Content $QueueFile -Raw
    $old     = "- [ ] ${TaskId}:"
    $new     = "- [x] ${TaskId}:"
    if ($content.Contains($old)) {
        $content = $content.Replace($old, $new)
        Set-Content -Path $QueueFile -Value $content -NoNewline
    }
}

function Invoke-GitCommitPush {
    param([string]$TaskId)
    Push-Location $RepoPath
    try {
        git add "tasks\safe_run_queue.md" "results\" 2>&1 | Out-Null
        git commit -m "poller: mark $TaskId done [skip ci]" 2>&1 | Out-Null
        if (-not $DryRun) {
            $out = git push origin main 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Push failed: $out"
                Write-Log $TaskId "PUSH_FAIL" "$out"
            }
        }
    } finally {
        Pop-Location
    }
}

# Ensure log header exists
if (-not (Test-Path $LogFile)) {
    $dir = Split-Path $LogFile
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
    Set-Content $LogFile "| Timestamp           | Task ID | Status    | Note |`n|---------------------|---------|-----------|------|"
}

Write-Host "MT4 Poller started. Interval=${IntervalMinutes}m  DryRun=$DryRun  Repo=$RepoPath"

while ($true) {
    $cycleStart = Get-Date

    # RAM check
    $ramOk, $ramPct = Get-RamOkay
    if (-not $ramOk) {
        Write-Log "SYSTEM" "RAM_LOW" "Available RAM ${ramPct}% < 15%"
        Start-Sleep -Seconds ($IntervalMinutes * 60)
        continue
    }

    # Pull latest
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] git pull..."
    if ($DryRun) {
        Write-Host "  DryRun: would git pull origin main"
    } else {
        Invoke-GitPull
    }

    # Process pending tasks
    $tasks = Get-PendingTasks
    if ($tasks.Count -eq 0) {
        Write-Host "  No pending tasks."
    }

    foreach ($task in $tasks) {
        Write-Host "  Task $($task.Id): $($task.Desc)"

        if ($DryRun) {
            Write-Host "  DryRun: would run $Tester -TaskId $($task.Id)"
            Write-Log $task.Id "DRY_RUN" $task.Desc
            continue
        }

        # Write active task file so run_tester.ps1 can also read it
        Set-Content -Path $ActiveTask -Value $task.Id

        try {
            & $Tester -TaskId $task.Id
            $exitCode = $LASTEXITCODE
        } catch {
            $exitCode = 1
            Write-Log $task.Id "ERROR" $_.Exception.Message
        }

        $status = if ($exitCode -eq 0) { "PASS" } else { "FAIL" }
        Write-Log $task.Id $status "exit=$exitCode"

        Mark-TaskDone $task.Id
        Invoke-GitCommitPush $task.Id
    }

    # Sleep until next cycle
    $elapsed = ((Get-Date) - $cycleStart).TotalSeconds
    $wait    = [math]::Max(0, ($IntervalMinutes * 60) - $elapsed)
    Write-Host "  Sleeping ${wait}s..."
    Start-Sleep -Seconds $wait
}
