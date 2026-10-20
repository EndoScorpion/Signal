# Setup script for Slack Socket Mode bridge
# Run from: relay\tools\

$dir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check Node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found. Install from nodejs.org first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing @slack/bolt..." -ForegroundColor Cyan
cd $dir
npm install @slack/bolt

# Prompt for secrets
function ReadSecret($prompt) {
    $ss = Read-Host $prompt -AsSecureString
    [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($ss))
}

$botToken    = ReadSecret "Slack Bot Token (xoxb-...)"
$appToken    = ReadSecret "Slack App Token (xapp-...)"
$signing     = ReadSecret "Slack Signing Secret"
$ghToken     = ReadSecret "GitHub Relay Token (for relay branch)"
$authUser    = Read-Host  "Authorized Slack User ID (leave blank to allow all)"

$env_content = @"
SLACK_BOT_TOKEN=$botToken
SLACK_APP_TOKEN=$appToken
SLACK_SIGNING_SECRET=$signing
GITHUB_RELAY_TOKEN=$ghToken
GITHUB_REPO=EndoScorpion/Signal
GITHUB_BRANCH=relay
AUTHORIZED_SLACK_USER=$authUser
"@

$envFile = Join-Path $dir ".env"
$env_content | Out-File -FilePath $envFile -Encoding utf8 -NoNewline
Write-Host ".env written to $envFile" -ForegroundColor Green
Write-Host ""
Write-Host "To start the bridge:" -ForegroundColor Yellow
Write-Host "  node $dir\slack_bolt_bridge.js"
