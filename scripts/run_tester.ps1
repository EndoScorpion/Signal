# run_tester.ps1 - safe MT4 backtest launcher
# Safeguards: (1) abort if C: free <8 GB, (2) enforce Model=1, (3) delete *_0.fxt/*_2.fxt after run

param(
    [string]$IniFile = "",
    [string]$TesterDir = "C:\Users\endos\Desktop\mt4_tester2"
)

# (1) Abort if C: free < 8 GB
$freeGB = [math]::Round((Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB, 2)
if ($freeGB -lt 8) {
    Write-Host "ABORT: C: only $freeGB GB free (need >=8 GB). Free space first." -ForegroundColor Red
    exit 1
}
Write-Host "C: free: $freeGB GB — OK"

# (2) Enforce Model=1 in INI if provided
if ($IniFile -and (Test-Path $IniFile)) {
    $content = Get-Content $IniFile -Raw
    if ($content -match 'Model\s*=\s*[^1]') {
        $content = $content -replace 'Model\s*=\s*\d+', 'Model=1'
        Set-Content $IniFile $content -NoNewline
        Write-Host "Patched $IniFile: Model=1 enforced"
    } elseif ($content -notmatch 'Model\s*=') {
        Add-Content $IniFile "`nModel=1"
        Write-Host "Added Model=1 to $IniFile"
    } else {
        Write-Host "Model=1 already set in $IniFile"
    }
}

# Run MT4 tester (user launches MT4 separately; this script manages pre/post)
Write-Host "Ready. Launch MT4 tester manually or call with -IniFile to patch config."
Write-Host "After your test run, call this script with -Cleanup to purge tick files."

# (3) Delete *_0.fxt and *_2.fxt after run (pass -Cleanup flag)
if ($args -contains '-Cleanup' -or $IniFile -eq '-Cleanup') {
    $fxtPaths = @(
        "$TesterDir\tester",
        "$env:APPDATA\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\Tester"
    )
    $totalFreed = 0
    foreach ($path in $fxtPaths) {
        if (Test-Path $path) {
            Get-ChildItem $path -Recurse -Include "*_0.fxt","*_2.fxt" -ErrorAction SilentlyContinue | ForEach-Object {
                $sz = $_.Length
                try {
                    Remove-Item $_.FullName -Force -ErrorAction Stop
                    $totalFreed += $sz
                    Write-Host "Deleted: $($_.FullName) ($([math]::Round($sz/1MB,1)) MB)"
                } catch {
                    Write-Host "Locked (skip): $($_.FullName)"
                }
            }
        }
    }
    Write-Host "FXT cleanup done. Freed: $([math]::Round($totalFreed/1MB,1)) MB"
}
