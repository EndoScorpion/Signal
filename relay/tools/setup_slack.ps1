# setup_slack.ps1 — run once to create local slack_config.json
# Usage: powershell -ExecutionPolicy Bypass -File relay\tools\setup_slack.ps1

$ConfigPath = "$PSScriptRoot\slack_config.json"

Write-Host "=== Slack Bridge Setup ===" -ForegroundColor Cyan
Write-Host "Paste values when prompted. Input is hidden. Press Enter after each."
Write-Host ""

$botToken = Read-Host "Bot User OAuth Token (xoxb-...)" -AsSecureString
$botTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($botToken))

$webhookUrl = Read-Host "Outbound Webhook URL (https://hooks.slack.com/...)" -AsSecureString
$webhookUrlPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($webhookUrl))

$claudeWebhook = Read-Host "Claude Code Webhook URL (https://api.anthropic.com/integrations/...)" -AsSecureString
$claudeWebhookPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($claudeWebhook))

$config = @{
    bot_token             = $botTokenPlain
    channel_id            = "C0CAN7WC0MS"
    trigger_keyword       = "!claude"
    cli_keyword           = "!cli"
    claude_webhook_url    = $claudeWebhookPlain
    slack_outbound_webhook = $webhookUrlPlain
}

$config | ConvertTo-Json -Depth 3 | Set-Content -Path $ConfigPath -Encoding UTF8
Write-Host ""
Write-Host "Config saved to: $ConfigPath" -ForegroundColor Green
Write-Host "Run: python relay\tools\slack_bridge.py"
