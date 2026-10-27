# relay_auto_read.ps1 - Reads to_cli.json, executes commands, writes from_cli.json
# Loop script launched hidden at logon via VBS. No popups. No visible windows.

$RepoDir  = "C:\Users\endos\Signal"
$ToCli    = "$RepoDir\relay\to_cli.json"
$FromCli  = "$RepoDir\relay\from_cli.json"
$LogFile  = "C:\Users\endos\Desktop\hst_out\relay_auto_read.log"

function Write-Log($msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    try { Add-Content -Path $LogFile -Value "[$ts] $msg" -Encoding UTF8 } catch {}
}

Write-Log "relay_auto_read started"

while ($true) {
    try {
        # Pull latest relay branch
        $pull = & git -C $RepoDir pull origin relay --rebase --autostash 2>&1
        if ($LASTEXITCODE -ne 0) { Write-Log "pull failed: $pull"; Start-Sleep -Seconds 30; continue }

        if (-not (Test-Path $ToCli)) { Start-Sleep -Seconds 30; continue }

        $toCliObj = Get-Content $ToCli -Raw -Encoding UTF8 | ConvertFrom-Json
        $cmds = @($toCliObj.commands)
        if ($cmds.Count -eq 0) { Start-Sleep -Seconds 30; continue }

        # Load existing results to find already-processed IDs
        $results = @()
        if (Test-Path $FromCli) {
            try {
                $existing = Get-Content $FromCli -Raw -Encoding UTF8 | ConvertFrom-Json
                $results = @($existing.results)
            } catch { $results = @() }
        }
        $doneIds = @($results | ForEach-Object { $_.id })

        $newResults = @()
        foreach ($cmd in $cmds) {
            if ($doneIds -contains $cmd.id) { continue }
            Write-Log "Exec id=$($cmd.id) label=$($cmd.label)"

            $output = ""; $exitCode = -1
            try {
                $tmpOut = "$env:TEMP\rar_out_$($cmd.id).txt"
                $tmpErr = "$env:TEMP\rar_err_$($cmd.id).txt"
                $proc = Start-Process "cmd.exe" `
                    -ArgumentList "/c $($cmd.command)" `
                    -RedirectStandardOutput $tmpOut `
                    -RedirectStandardError  $tmpErr `
                    -Wait -PassThru -NoNewWindow -WindowStyle Hidden
                $exitCode = $proc.ExitCode
                $out = if (Test-Path $tmpOut) { (Get-Content $tmpOut -Raw -Encoding UTF8).TrimEnd() } else { "" }
                $err = if (Test-Path $tmpErr) { (Get-Content $tmpErr -Raw -Encoding UTF8).TrimEnd() } else { "" }
                Remove-Item $tmpOut,$tmpErr -Force -ErrorAction SilentlyContinue
                $combined = ($out + $(if ($err) { "`nSTDERR: $err" } else { "" })).TrimEnd()
                $output = if ($combined.Length -gt 500) { $combined.Substring(0,500) + "..." } else { $combined }
            } catch {
                $output = "ERROR: $($_.Exception.Message)"; $exitCode = 1
            }

            $newResults += [PSCustomObject]@{
                id        = $cmd.id
                label     = if ($cmd.label) { $cmd.label } else { $cmd.id }
                output    = $output
                exit_code = $exitCode
                ts        = (Get-Date).ToString("o")
            }
            Write-Log "Done id=$($cmd.id) exit=$exitCode out_len=$($output.Length)"
        }

        if ($newResults.Count -gt 0) {
            # Merge with existing, keep last 50
            $all = @($results) + @($newResults)
            if ($all.Count -gt 50) { $all = $all[($all.Count-50)..($all.Count-1)] }
            $outObj = [PSCustomObject]@{ results = $all; updated = (Get-Date).ToString("o") }
            $outObj | ConvertTo-Json -Depth 5 | Set-Content $FromCli -Encoding UTF8

            & git -C $RepoDir add relay/from_cli.json
            & git -C $RepoDir commit -m "relay: auto_read results $(Get-Date -Format 'HH:mm:ss')" 2>&1 | Out-Null
            $push = & git -C $RepoDir push origin HEAD:relay 2>&1
            if ($LASTEXITCODE -ne 0) { Write-Log "push failed: $push" }
            else { Write-Log "Pushed $($newResults.Count) result(s) to from_cli.json" }
        }
    } catch {
        Write-Log "ERROR: $_"
    }

    Start-Sleep -Seconds 30
}
