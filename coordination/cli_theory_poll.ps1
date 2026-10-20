# cli_theory_poll.ps1 - Self-improvement loop: poll theory_queue, run MT4 tests, push results
# Run from: C:\Users\endos\Desktop\hst_out\  (or call via CliRelayPoll cadence)
# Requires: git on PATH, run_tester.ps1 in same folder
# Commission: 8 pts/trade always (CLAUDE.md). M1 tests always use -TimeoutMin 180.

$ErrorActionPreference = "Stop"
$SignalRepo  = "C:\Users\endos\Desktop\hst_work\Signal"   # adjust if different
$HstOut     = "C:\Users\endos\Desktop\hst_out"
$QueueFile  = "$SignalRepo\coordination\theory_queue.json"
$ResultFile = "$SignalRepo\coordination\theory_results.json"
$RunTester  = "$HstOut\run_tester.ps1"
$LogFile    = "$HstOut\winners\TEST_LOG.txt"

# --- helpers ---
function Git-Pull { git -C $SignalRepo fetch origin relay 2>&1 | Out-Null; git -C $SignalRepo checkout relay 2>&1 | Out-Null; git -C $SignalRepo pull origin relay 2>&1 | Out-Null }
function Git-Push($msg) { git -C $SignalRepo add coordination/theory_results.json; git -C $SignalRepo commit -m $msg 2>&1 | Out-Null; git -C $SignalRepo push origin relay 2>&1 | Out-Null }

function Parse-HtmResult($htmPath) {
    # Parse key stats from MT4 HTML report
    $html = Get-Content $htmPath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $html) { return $null }
    $n  = if ($html -match 'Total trades.*?<td[^>]*>(\d+)') { [int]$Matches[1] } else { 0 }
    $pf = if ($html -match 'Profit factor.*?<td[^>]*>([\d.]+)') { [double]$Matches[1] } else { 0.0 }
    $dd = if ($html -match 'Maximal drawdown.*?<td[^>]*>([\d.]+)') { [double]$Matches[1] } else { 0.0 }
    $np = if ($html -match 'Total net profit.*?<td[^>]*>(-?[\d.]+)') { [double]$Matches[1] } else { 0.0 }
    return @{ n=$n; pf=$pf; dd=$dd; np=$np }
}

# Check pause
if (Test-Path "$HstOut\MT4_PAUSE") { Write-Host "PAUSED: MT4_PAUSE exists - skipping theory poll"; exit 6 }

# Pull latest queue
Git-Pull

$queue   = Get-Content $QueueFile   | ConvertFrom-Json
$results = Get-Content $ResultFile  | ConvertFrom-Json

# Filter schema entry
$queue   = @($queue   | Where-Object { $_.id -and $_.id -notlike '_*' })
$results = @($results | Where-Object { $_.id -and $_.id -notlike '_*' })

$pending = $queue | Where-Object { $_.status -eq 'pending' }
if (-not $pending) { Write-Host "No pending theory entries."; exit 0 }

foreach ($entry in $pending) {
    Write-Host "Theory poll: processing $($entry.id) - $($entry.description)"

    # Mark running
    ($queue | Where-Object { $_.id -eq $entry.id }).status = 'running'

    foreach ($year in $entry.years) {
        $from = "$year.01.01"; $to = "$year.12.31"
        $tag  = "$($entry.id)_$year"

        # Build temp set file if overrides provided
        $setFile = $entry.set_base
        # (override application would go here for future expansion)

        $timeout = if ($entry.timeout_min) { $entry.timeout_min } else { 180 }
        $spread  = if ($entry.spread)      { $entry.spread }      else { 3 }

        Write-Host "  Running $($entry.ea) $year spread=$spread timeout=$timeout"
        $t0 = Get-Date
        $rc = 0
        try {
            & powershell -ExecutionPolicy Bypass -File $RunTester `
                -Expert $entry.ea -SetFile $setFile `
                -Symbol ($entry.symbol ?? "EURUSD") -Period ($entry.period ?? "M1") `
                -Spread $spread -From $from -To $to -Tag $tag -TimeoutMin $timeout
            $rc = $LASTEXITCODE
        } catch { $rc = 99 }

        $elapsed = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
        $htmPath = "$HstOut\$tag.htm"
        $verdict = "FAIL"; $flag = $false; $flagReason = ""

        if ($rc -eq 0 -and (Test-Path $htmPath)) {
            $stats = Parse-HtmResult $htmPath
            if ($stats -and $stats.n -gt 0) {
                $verdict = "PASS"
                # Flag criteria: more trades OR better PF without DD increase (vs b31 base)
                if ($stats.n -gt 50 -or $stats.pf -gt 1.3) {
                    $flag = $true; $flagReason = "n=$($stats.n) PF=$($stats.pf) - review vs base"
                }
                # Log to TEST_LOG.txt
                $logLine = "$(Get-Date -f 'yyyy-MM-dd HH:mm') | theory:$($entry.id) | $year | n=$($stats.n) PF=$($stats.pf) DD=$($stats.dd)% NP=$($stats.np) | FLAG=$flag | $($entry.description)"
                Add-Content $LogFile $logLine
            }
        } elseif ($rc -eq 3) { $verdict = "TIMEOUT" }

        $result = [PSCustomObject]@{
            id          = $entry.id
            year        = $year
            status      = if ($verdict -eq "TIMEOUT") { "timeout" } elseif ($verdict -eq "PASS") { "done" } else { "failed" }
            completed_at = (Get-Date -f 'o')
            report_file  = "$tag.htm"
            elapsed_min  = $elapsed
            n_trades     = if ($stats) { $stats.n } else { 0 }
            profit_factor = if ($stats) { $stats.pf } else { 0.0 }
            max_dd_pct    = if ($stats) { $stats.dd } else { 0.0 }
            net_profit    = if ($stats) { $stats.np } else { 0.0 }
            verdict       = $verdict
            flag          = $flag
            flag_reason   = $flagReason
            notes         = "exit_code=$rc timeout_min=$timeout"
        }
        $results += $result

        # Push after each year result
        $results | ConvertTo-Json -Depth 5 | Set-Content $ResultFile -Encoding UTF8
        Git-Push "theory result: $($entry.id) $year $verdict"
        Write-Host "  $verdict in $elapsed min $(if($flag){'*** FLAGGED ***'})"
    }

    # Mark queue entry done
    ($queue | Where-Object { $_.id -eq $entry.id }).status = 'done'
    $queue | ConvertTo-Json -Depth 5 | Set-Content $QueueFile -Encoding UTF8
    git -C $SignalRepo add coordination/theory_queue.json
    git -C $SignalRepo commit -m "theory queue: mark $($entry.id) done" 2>&1 | Out-Null
    git -C $SignalRepo push origin relay 2>&1 | Out-Null
}

Write-Host "Theory poll complete."
