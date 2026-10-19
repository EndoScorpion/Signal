# 09_install_dc_remote_service.ps1
# Installs DC Remote (@wonderwhy-er/desktop-commander remote) as NSSM service DCRemoteService
# Run as Administrator from any directory

$NSSM = "C:\Users\endos\Desktop\hst_work\Signal\relay\tools\nssm.exe"
$SERVICE = "DCRemoteService"
$APP_DIR = "C:\Users\endos\Desktop\hst_work\Signal"

Write-Host "=== DC Remote NSSM Service Installer ===" -ForegroundColor Cyan

if (-not (Test-Path $NSSM)) {
    Write-Host "ERROR: nssm.exe not found at $NSSM" -ForegroundColor Red
    exit 1
}

# Stop + delete existing service (idempotent)
$existing = & $NSSM status $SERVICE 2>&1
if ($LASTEXITCODE -eq 0 -or ($existing -notmatch "not installed")) {
    Write-Host "Stopping and removing existing $SERVICE..." -ForegroundColor Yellow
    & $NSSM stop $SERVICE 2>&1 | Out-Null
    & $NSSM remove $SERVICE confirm 2>&1 | Out-Null
    Start-Sleep -Seconds 2
}

Write-Host "Installing $SERVICE..." -ForegroundColor Green

# Install using cmd.exe /c npx ... so npx (a cmd wrapper) resolves correctly
& $NSSM install $SERVICE "C:\Windows\System32\cmd.exe"
& $NSSM set $SERVICE AppParameters "/c npx @wonderwhy-er/desktop-commander@latest remote"
& $NSSM set $SERVICE AppDirectory $APP_DIR
& $NSSM set $SERVICE DisplayName "DC Remote Service (Desktop Commander)"
& $NSSM set $SERVICE Description "Runs desktop-commander remote for Claude Code cloud sessions"
& $NSSM set $SERVICE Start SERVICE_AUTO_START
& $NSSM set $SERVICE AppStdout "$APP_DIR\relay\logs\dc_remote_stdout.log"
& $NSSM set $SERVICE AppStderr "$APP_DIR\relay\logs\dc_remote_stderr.log"
& $NSSM set $SERVICE AppRotateFiles 1
& $NSSM set $SERVICE AppRotateBytes 10485760

# Ensure log dir exists
New-Item -ItemType Directory -Force -Path "$APP_DIR\relay\logs" | Out-Null

Write-Host "Starting $SERVICE..." -ForegroundColor Green
& $NSSM start $SERVICE

Start-Sleep -Seconds 3
$status = & $NSSM status $SERVICE 2>&1
Write-Host "Status: $status" -ForegroundColor Cyan

if ($status -match "SERVICE_RUNNING") {
    Write-Host "SUCCESS: $SERVICE is running." -ForegroundColor Green
} else {
    Write-Host "WARNING: Service may not be running. Check logs at $APP_DIR\relay\logs\" -ForegroundColor Yellow
}
