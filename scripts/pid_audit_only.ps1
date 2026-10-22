# PID_AUDIT.ps1 — READ ONLY, no kills. Run as Admin.
# Outputs a table mapping each node/powershell/cmd PID to its command line.
# Review output, then manually kill orphans shown at the bottom.

$keepPatterns = @(
    "CloudCmdPollerGH","cmd_poller_relay","relay","dc_clone_server",
    "DcCloneServer","desktop-commander","wonderwhy-er","watchdog",
    "Cloud_DC_Watchdog","signal-board"
)

$procs = Get-CimInstance Win32_Process -Filter "Name='node.exe' OR Name='powershell.exe' OR Name='cmd.exe'" |
    ForEach-Object {
        $mb = try { [math]::Round((Get-Process -Id $_.ProcessId -EA Stop).WorkingSet64/1MB,1) } catch { 0 }
        $cmd = "$($_.CommandLine)"
        $keep = ($keepPatterns | Where-Object { $cmd -match $_ }).Count -gt 0
        [PSCustomObject]@{ PID=$_.ProcessId; Name=$_.Name; MB=$mb; Keep=$keep; Cmd=$cmd.Substring(0,[math]::Min(150,$cmd.Length)) }
    }

$procs | Sort-Object Keep,MB -Descending | Format-Table PID,Name,MB,Keep,Cmd -AutoSize
Write-Host "`nOrphan PIDs (Keep=False) — review before killing:"
$orphanPids = ($procs | Where-Object { -not $_.Keep } | Select-Object -ExpandProperty PID) -join ","
Write-Host "Stop-Process -Id @($orphanPids) -Force"
