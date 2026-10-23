# git_auth_hidden.ps1 — configure git credential store hidden, no popups
# Run via: wscript.exe run_hidden.vbs "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File git_auth_hidden.ps1"

$repoRoot = 'C:\Users\endos\Signal'
$results = @("git_auth_hidden start $(Get-Date -Format 'o')")

try {
    cd $repoRoot

    # Use credential store (persists token, no popup prompts)
    git config credential.helper store
    $results += "credential.helper=store set"

    # Disable any credential GUI helpers that spawn popups
    git config --global credential.modalPrompt false 2>$null
    git config --global core.askPass '' 2>$null

    # Test auth: fetch relay branch silently
    $env:GIT_TERMINAL_PROMPT = '0'
    $fetchOut = git fetch origin relay 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $results += "git fetch OK"
    } else {
        $results += "git fetch result: $($fetchOut.Trim() | Select-Object -First 2)"
    }

    # Verify push works
    $testFile = "$repoRoot\relay\.auth_test"
    Set-Content $testFile "auth_test $(Get-Date -Format 'o')"
    git add relay/.auth_test
    $commitOut = git commit -m "relay: auth test $(Get-Date -Format 'yyyyMMddTHHmmss')" 2>&1 | Out-String
    $pushOut = git push origin relay 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $results += "git push OK — auth confirmed"
    } else {
        $results += "git push: $($pushOut.Trim() | Select-Object -First 2)"
    }
    Remove-Item $testFile -ErrorAction SilentlyContinue

} catch {
    $results += "Error: $($_.Exception.Message)"
}

# Report to outbox
$report = "# LocalThug Outbox - GIT AUTH`n## $(Get-Date -Format 'o')`n`n" + ($results | ForEach-Object { "- $_" } | Out-String)
Set-Content "$repoRoot\relay\outbox_to_cloud.md" $report
cd $repoRoot
git add relay/outbox_to_cloud.md
git commit -m "relay: git auth result $(Get-Date -Format 'yyyyMMddTHHmmss')"
git push origin relay
