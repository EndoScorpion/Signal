# signal_notify_relay.ps1 — Watch MT4 notify queue + forward to ntfy / SMS / Claude
# Run once in background: powershell -WindowStyle Hidden -File signal_notify_relay.ps1
#
# MT4 writes to:  %APPDATA%\MetaQuotes\Terminal\<ID>\MQL4\Files\signal_notify_queue.txt
# This script tails that file and forwards each new line to the channels you configure.
#
# === Configuration ===  (edit these or pass as env vars before launching)
# --- ntfy.sh push (free, no account; install ntfy app on Android/iOS) ---
# $env:NTFY_TOPIC = "signal-ea-abc123"          # pick any unique string
# $env:NTFY_SERVER = "https://ntfy.sh"           # or self-hosted
# $env:NTFY_TOKEN  = ""                          # only if topic is protected
#
# --- Twilio SMS ---
# $env:TWILIO_SID   = "ACxxx"
# $env:TWILIO_TOKEN = "your_auth_token"
# $env:TWILIO_FROM  = "+15551234567"
# $env:TWILIO_TO    = "+15559876543"
#
# --- Textbelt free SMS (1 free/day; no account) ---
# $env:TEXTBELT_TO  = "+15559876543"
# $env:TEXTBELT_KEY = "textbelt"   # free tier; pay for more
#
# --- Claude project thread (hearthbot webhook) ---
# $env:CLAUDE_WEBHOOK_URL = "https://hearthbot.anthropic.com/..."
# $env:CLAUDE_WEBHOOK_KEY = "..."
#
# --- MT4 queue file path (auto-detected if blank) ---
# $env:MT4_QUEUE_FILE = "C:\Users\...\MQL4\Files\signal_notify_queue.txt"
#
# Usage:
#   Start: powershell -WindowStyle Hidden -File signal_notify_relay.ps1
#   Stop:  Get-Process powershell | ... (or kill via Task Manager)
#   Test:  .\signal_notify_relay.ps1 -Test
param(
    [switch]$Test,
    [string]$MT4QueueFile = $env:MT4_QUEUE_FILE
)

# Topic from local secret file (never in git or env vars visible to CI)
$NtfyTopicFile = if($env:NTFY_TOPIC_FILE) {$env:NTFY_TOPIC_FILE} else {
    # Default: look in Signal/data/ relative to this script, then laptop data/ fallback
    $candidates = @(
        (Join-Path (Split-Path $ScriptDir -Parent) "data\ntfy_topic.txt"),
        "$env:USERPROFILE\data\ntfy_topic.txt",
        "$env:USERPROFILE\Documents\Signal\data\ntfy_topic.txt"
    )
    ($candidates | Where-Object {Test-Path $_} | Select-Object -First 1)
}
$NtfyTopic = if ($NtfyTopicFile -and (Test-Path $NtfyTopicFile)) {
    (Get-Content $NtfyTopicFile -Raw).Trim()
} else { $env:NTFY_TOPIC }  # env var fallback (never log this value)
$NtfyServer = if($env:NTFY_SERVER) {$env:NTFY_SERVER} else {"https://ntfy.sh"}
$NtfyToken   = $env:NTFY_TOKEN
$TwilioSid   = $env:TWILIO_SID;   $TwilioToken = $env:TWILIO_TOKEN
$TwilioFrom  = $env:TWILIO_FROM;  $TwilioTo    = $env:TWILIO_TO
$TxtbeltTo   = $env:TEXTBELT_TO;  $TxtbeltKey  = if($env:TEXTBELT_KEY) {$env:TEXTBELT_KEY} else {"textbelt"}
$ClaudeUrl   = $env:CLAUDE_WEBHOOK_URL; $ClaudeKey = $env:CLAUDE_WEBHOOK_KEY

# --- Auto-detect MT4 queue file ---
if (-not $MT4QueueFile) {
    $mqRoot = "$env:APPDATA\MetaQuotes\Terminal"
    if (Test-Path $mqRoot) {
        $qfiles = Get-ChildItem "$mqRoot\*\MQL4\Files\signal_notify_queue.txt" -ErrorAction SilentlyContinue
        if ($qfiles) { $MT4QueueFile = $qfiles[0].FullName }
    }
    if (-not $MT4QueueFile) {
        # Common alternate path (some MT4 installs)
        $alt = "$env:USERPROFILE\AppData\Roaming\MetaQuotes\Terminal\Common\Files\signal_notify_queue.txt"
        if (Test-Path $alt) { $MT4QueueFile = $alt }
    }
    if (-not $MT4QueueFile) {
        Write-Warning "Could not auto-detect MT4 queue file. Set env:MT4_QUEUE_FILE manually."
        Write-Host "Searching in: $mqRoot"
        exit 1
    }
    Write-Host "Auto-detected queue: $MT4QueueFile"
}

# --- Send functions ---
function Send-Ntfy($subj, $body) {
    if (-not $NtfyTopic) { return }
    try {
        $headers = @{"Title"="$subj"; "Content-Type"="text/plain"}
        if ($NtfyToken) { $headers["Authorization"] = "Bearer $NtfyToken" }
        Invoke-RestMethod -Method POST -Uri "$NtfyServer/$NtfyTopic" -Headers $headers -Body $body -TimeoutSec 10
        Write-Host "  [ntfy] sent"
    } catch { Write-Warning "ntfy failed: $_" }
}

function Send-TwilioSMS($subj, $body) {
    if (-not $TwilioSid -or -not $TwilioTo) { return }
    try {
        $url = "https://api.twilio.com/2010-04-01/Accounts/$TwilioSid/Messages.json"
        $msg = "[MasterEA] $subj`n$body"
        $data = "From=$TwilioFrom&To=$TwilioTo&Body=" + [Uri]::EscapeDataString($msg)
        $cred = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${TwilioSid}:${TwilioToken}"))
        Invoke-RestMethod -Method POST -Uri $url -Headers @{"Authorization"="Basic $cred"} `
                          -ContentType "application/x-www-form-urlencoded" -Body $data -TimeoutSec 10
        Write-Host "  [SMS/Twilio] sent"
    } catch { Write-Warning "Twilio SMS failed: $_" }
}

function Send-TextbeltSMS($subj, $body) {
    if (-not $TxtbeltTo) { return }
    try {
        $msg = "[MasterEA] $subj: " + ($body -replace "`n"," ")
        $data = @{phone=$TxtbeltTo; message=$msg; key=$TxtbeltKey}
        Invoke-RestMethod -Method POST -Uri "https://textbelt.com/text" -Body $data -TimeoutSec 10
        Write-Host "  [SMS/textbelt] sent"
    } catch { Write-Warning "Textbelt SMS failed: $_" }
}

function Send-ClaudeWebhook($subj, $body) {
    if (-not $ClaudeUrl) { return }
    try {
        $payload = @{subject=$subj; body=$body; source="MasterEA"; ts=(Get-Date -Format o)} | ConvertTo-Json
        $headers = @{"Content-Type"="application/json"}
        if ($ClaudeKey) { $headers["Authorization"] = "Bearer $ClaudeKey" }
        Invoke-RestMethod -Method POST -Uri $ClaudeUrl -Headers $headers -Body $payload -TimeoutSec 10
        Write-Host "  [Claude webhook] sent"
    } catch { Write-Warning "Claude webhook failed: $_" }
}

function Dispatch($line) {
    # Format: timestamp|subject|body
    $parts = $line -split '\|', 3
    if ($parts.Count -lt 2) { return }
    $subj = $parts[1]; $body = if ($parts.Count -gt 2) { $parts[2] } else { "" }
    Write-Host "$(Get-Date -Format HH:mm:ss) NOTIFY: $subj"
    Send-Ntfy         $subj $body
    Send-TwilioSMS    $subj $body
    Send-TextbeltSMS  $subj $body
    Send-ClaudeWebhook $subj $body
}

# --- Test mode ---
if ($Test) {
    Write-Host "=== TEST MODE ==="
    $testLine = "$(Get-Date -Format 'yyyy.MM.dd HH:mm')|[MasterEA] TEST|This is a test notification from signal_notify_relay.ps1"
    Dispatch $testLine
    Write-Host "Test dispatch complete."
    exit 0
}

# --- Watch loop ---
Write-Host "signal_notify_relay.ps1 started"
Write-Host "Queue: $MT4QueueFile"
Write-Host "ntfy:  $(if($NtfyTopic){"$NtfyServer/$NtfyTopic"}else{'disabled'})"
Write-Host "SMS:   $(if($TwilioTo){'Twilio enabled'}elseif($TxtbeltTo){'textbelt enabled'}else{'disabled'})"
Write-Host "Claude:$(if($ClaudeUrl){'webhook enabled'}else{'disabled'})"
Write-Host ""

# Ensure directory exists
$qDir = Split-Path $MT4QueueFile -Parent
New-Item -ItemType Directory -Force -Path $qDir | Out-Null
if (-not (Test-Path $MT4QueueFile)) { New-Item -ItemType File -Force -Path $MT4QueueFile | Out-Null }

$lastSize = (Get-Item $MT4QueueFile).Length
$lastLines = (Get-Content $MT4QueueFile -ErrorAction SilentlyContinue).Count
if (-not $lastLines) { $lastLines = 0 }

Write-Host "Watching... (Ctrl+C to stop)"
while ($true) {
    Start-Sleep -Milliseconds 2000
    try {
        $lines = Get-Content $MT4QueueFile -ErrorAction SilentlyContinue
        if (-not $lines) { $lines = @() }
        $count = $lines.Count
        if ($count -gt $lastLines) {
            for ($i = $lastLines; $i -lt $count; $i++) {
                if ($lines[$i].Trim() -ne "") { Dispatch $lines[$i] }
            }
            $lastLines = $count
        }
    } catch { Write-Warning "Read error: $_"; Start-Sleep -Seconds 5 }
}
