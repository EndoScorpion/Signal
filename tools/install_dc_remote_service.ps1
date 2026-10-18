#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Installs Desktop Commander Remote as a persistent Windows service via NSSM.
    Service name: DCRemoteService
    Survives lock, logoff, and reboot — no user session required.

.USAGE
    # Install / reinstall
    .\install_dc_remote_service.ps1

    # Remove service
    .\install_dc_remote_service.ps1 -Uninstall
#>
param(
    [switch]$Uninstall
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ServiceName = 'DCRemoteService'

# ── 1. Find or install NSSM ────────────────────────────────────────────────────
function Get-NssmPath {
    $fromPath = (Get-Command nssm.exe -ErrorAction SilentlyContinue)?.Source
    if ($fromPath) { return $fromPath }

    # Try chocolatey install
    $choco = (Get-Command choco -ErrorAction SilentlyContinue)?.Source
    if ($choco) {
        Write-Host "Installing NSSM via Chocolatey..."
        & $choco install nssm -y --no-progress | Out-Null
        $fromPath = (Get-Command nssm.exe -ErrorAction SilentlyContinue)?.Source
        if ($fromPath) { return $fromPath }
    }

    # Manual download fallback — nssm 2.24
    $nssmDir  = "$env:ProgramFiles\nssm"
    $nssmExe  = "$nssmDir\nssm.exe"
    if (Test-Path $nssmExe) { return $nssmExe }

    Write-Host "Downloading NSSM 2.24..."
    $zip  = "$env:TEMP\nssm.zip"
    $wc   = New-Object System.Net.WebClient
    $wc.DownloadFile('https://nssm.cc/release/nssm-2.24.zip', $zip)
    Expand-Archive -Path $zip -DestinationPath "$env:TEMP\nssm_extract" -Force
    $arch = if ([Environment]::Is64BitOperatingSystem) { 'win64' } else { 'win32' }
    $src  = (Get-ChildItem "$env:TEMP\nssm_extract" -Recurse -Filter "nssm.exe" |
             Where-Object { $_.FullName -like "*$arch*" } |
             Select-Object -First 1).FullName
    New-Item -ItemType Directory -Path $nssmDir -Force | Out-Null
    Copy-Item $src $nssmExe -Force
    return $nssmExe
}

$nssm = Get-NssmPath
Write-Host "NSSM: $nssm"

# ── 2. Uninstall mode ──────────────────────────────────────────────────────────
if ($Uninstall) {
    Write-Host "Stopping and removing $ServiceName..."
    & $nssm stop   $ServiceName 2>$null
    & $nssm remove $ServiceName confirm 2>$null
    Write-Host "Done."
    return
}

# ── 3. Find node.exe ──────────────────────────────────────────────────────────
$node = (Get-Command node -ErrorAction Stop).Source
Write-Host "Node: $node  ($(& node --version))"

# ── 4. Find the desktop-commander entry point ─────────────────────────────────
# Resolve via node so we get the exact file, not a cmd shim
$dcMain = (& node -e "try{process.stdout.write(require.resolve('@wonderwhy-er/desktop-commander'))}catch(e){}" 2>$null)
if (-not $dcMain) {
    # Fallback: locate via npx --no-install path resolution
    $dcMain = (& node -e @"
const p = require('path');
const r = require.resolve.bind(require);
try {
  // Try global node_modules
  const gp = require('child_process').execSync('npm root -g').toString().trim();
  process.stdout.write(r(p.join(gp, '@wonderwhy-er/desktop-commander')));
} catch(e) { process.stdout.write(''); }
"@ 2>$null)
}

if ($dcMain) {
    Write-Host "DC entry: $dcMain"
    $appExe  = $node
    $appArgs = "`"$dcMain`" remote"
} else {
    # No pre-installed package — use npx each launch (slightly slower cold start)
    Write-Host "Package not found globally; service will use npx (slower cold start)"
    $npmExe  = (Get-Command npm -ErrorAction Stop).Source
    # NSSM can't run .cmd files directly; wrap via cmd.exe
    $appExe  = "$env:SystemRoot\System32\cmd.exe"
    $appArgs = "/c npx @wonderwhy-er/desktop-commander remote"
}

# ── 5. Log directory ──────────────────────────────────────────────────────────
$logDir = "$env:LOCALAPPDATA\DCRemoteService\logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

# ── 6. Remove stale service if it exists ──────────────────────────────────────
$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing $ServiceName service..."
    & $nssm stop   $ServiceName 2>$null
    Start-Sleep -Seconds 2
    & $nssm remove $ServiceName confirm
}

# ── 7. Install service ────────────────────────────────────────────────────────
Write-Host "Installing $ServiceName..."
& $nssm install $ServiceName $appExe $appArgs

# Service settings
& $nssm set $ServiceName DisplayName  "Desktop Commander Remote"
& $nssm set $ServiceName Description  "Relays Desktop Commander MCP over WebSocket for remote Claude sessions"
& $nssm set $ServiceName Start        SERVICE_AUTO_START
& $nssm set $ServiceName AppStdout    "$logDir\stdout.log"
& $nssm set $ServiceName AppStderr    "$logDir\stderr.log"
& $nssm set $ServiceName AppRotateFiles 1
& $nssm set $ServiceName AppRotateOnline 1
& $nssm set $ServiceName AppRotateBytes 5242880   # 5 MB rotate

# Ensure PATH is inherited so node/npx are reachable by SYSTEM account
$nodeBin = Split-Path $node
& $nssm set $ServiceName AppEnvironmentExtra "PATH=$nodeBin;$env:PATH"

# Restart delay: 5 s on crash, up to 3 attempts then 60 s pause
& $nssm set $ServiceName AppExit Default Restart
& $nssm set $ServiceName AppRestartDelay 5000

# ── 8. Start and verify ───────────────────────────────────────────────────────
Write-Host "Starting $ServiceName..."
& $nssm start $ServiceName
Start-Sleep -Seconds 3

$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -eq 'Running') {
    Write-Host "`n$ServiceName is RUNNING. Logs: $logDir"
    Write-Host "To remove: .\install_dc_remote_service.ps1 -Uninstall"
} else {
    Write-Warning "$ServiceName did not start cleanly. Check: $logDir\stderr.log"
    Get-Content "$logDir\stderr.log" -Tail 20 -ErrorAction SilentlyContinue
}
