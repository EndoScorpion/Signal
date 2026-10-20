# cmd_poller.ps1 — GitHub-relay poller (5s loop)
# Cloud Claude pushes cmd_queue.json to EndoScorpion/Signal relay branch via GitHub API
# This script: git pull, execute pending, git push results, repeat every 5s

$RepoDir     = "C:\Users\endos\Desktop\hst_work\Signal"
$QueueFile   = "$RepoDir\relay\cmd_queue.json"
$ResultsFile = "$RepoDir\relay\cmd_results.json"
$LogFile     = "C:\Users\endos\Desktop\hst_out\cmd_poller.log"

function Write-Log($msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $LogFile -Value "[$ts] $msg" -Encoding UTF8
}

Write-Log "Poller started (GitHub relay, 5s loop)"

while ($true) {
    try {
        # Pull latest from relay branch
        $pull = & git -C $RepoDir pull origin relay --rebase --autostash 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "git pull failed: $pull"
            Start-Sleep -Seconds 5; continue
        }

        if (-not (Test-Path $QueueFile)) { Start-Sleep -Seconds 5; continue }

        $queue = Get-Content $QueueFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $pending = @($queue | Where-Object { $_.status -eq "pending" })

        if ($pending.Count -eq 0) { Start-Sleep -Seconds 5; continue }

        $results = @()
        if (Test-Path $ResultsFile) {
            try { $results = @(Get-Content $ResultsFile -Raw -Encoding UTF8 | ConvertFrom-Json) }
            catch { $results = @() }
        }

        foreach ($item in $pending) {
            Write-Log "Exec id=$($item.id) shell=$($item.shell)"
            $stdout = ""; $stderr = ""; $exitCode = -1

            try {
                if ($item.shell -eq "cmd") {
                    $proc = Start-Process "cmd.exe" -ArgumentList "/c $($item.command)" `
                        -RedirectStandardOutput "$env:TEMP\co_$($item.id).txt" `
                        -RedirectStandardError  "$env:TEMP\ce_$($item.id).txt" `
                        -Wait -PassThru -NoNewWindow
                    $exitCode = $proc.ExitCode
                    if (Test-Path "$env:TEMP\co_$($item.id).txt") { $stdout = Get-Content "$env:TEMP\co_$($item.id).txt" -Raw; Remove-Item "$env:TEMP\co_$($item.id).txt" -Force }
                    if (Test-Path "$env:TEMP\ce_$($item.id).txt") { $stderr = Get-Content "$env:TEMP\ce_$($item.id).txt" -Raw; Remove-Item "$env:TEMP\ce_$($item.id).txt" -Force }
                } else {
                    $stdout = Invoke-Expression $item.command 2>&1 | Out-String
                    $exitCode = if ($?) { 0 } else { 1 }
                }
            } catch {
                $stderr = $_.Exception.Message; $exitCode = 1
            }

            $results += [PSCustomObject]@{
                id           = $item.id
                stdout       = $stdout.TrimEnd()
                stderr       = $stderr.TrimEnd()
                exit_code    = $exitCode
                completed_at = (Get-Date).ToString("o")
            }

            foreach ($q in $queue) { if ($q.id -eq $item.id) { $q.status = "done" } }
            Write-Log "Done id=$($item.id) exit=$exitCode"
        }

        $queue   | ConvertTo-Json -Depth 5 | Set-Content $QueueFile   -Encoding UTF8
        $results | ConvertTo-Json -Depth 5 | Set-Content $ResultsFile -Encoding UTF8

        # Push results back
        & git -C $RepoDir add relay/cmd_queue.json relay/cmd_results.json
        & git -C $RepoDir commit -m "relay: results $(Get-Date -Format 'HH:mm:ss')" 2>&1 | Out-Null
        $push = & git -C $RepoDir push origin relay 2>&1
        if ($LASTEXITCODE -ne 0) { Write-Log "git push failed: $push" }

    } catch {
        Write-Log "ERROR: $_"
    }

    Start-Sleep -Seconds 5
}