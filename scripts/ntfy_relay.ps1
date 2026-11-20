# ntfy_relay.ps1 — vague-code relay via ntfy.sh with CF Worker fallback
# Usage: .\ntfy_relay.ps1 -Mode pub -Msg "WR 64% PF 2.9 n=341"
#        .\ntfy_relay.ps1 -Mode poll
# Env vars: RELAY_TOPIC (ntfy topic hash), CF_RELAY_URL, CF_RELAY_SECRET

param(
    [string]$Mode = "poll",
    [string]$Msg = "",
    [int]$PollInterval = 30,
    [int]$NtfyTimeout = 5
)

# Derive topic from env or hash of machine-specific seed
function Get-RelayTopic {
    if ($env:RELAY_TOPIC) { return $env:RELAY_TOPIC }
    $seed = "signal-relay-" + $env:COMPUTERNAME
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($seed))
    $full = ($bytes | ForEach-Object { $_.ToString("x2") }) -join ""
    return $full.Substring(0, 16)
}

$TOPIC = Get-RelayTopic
$NTFY_BASE = "https://ntfy.sh"
$CF_URL = $env:CF_RELAY_URL
$CF_SECRET = $env:CF_RELAY_SECRET

function Invoke-NtfyPublish($msg) {
    try {
        Invoke-RestMethod -Uri "$NTFY_BASE/$TOPIC" -Method POST -Body $msg `
            -TimeoutSec $NtfyTimeout -ErrorAction Stop | Out-Null
        return $true
    } catch {
        Write-Host "[ntfy] blocked or timeout: $_"
        return $false
    }
}

function Invoke-CFPublish($msg) {
    if (-not $CF_URL) { Write-Host "[cf] CF_RELAY_URL not set"; return $false }
    try {
        $headers = @{ "Authorization" = "Bearer $CF_SECRET" }
        $body = @{ msg = $msg; ts = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() } | ConvertTo-Json
        Invoke-RestMethod -Uri "$CF_URL/relay?key=$TOPIC" -Method PUT -Body $body `
            -Headers $headers -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop | Out-Null
        return $true
    } catch {
        Write-Host "[cf] error: $_"
        return $false
    }
}

function Invoke-RelayPublish($msg) {
    # Cascade: ntfy -> CF Worker
    if (-not (Invoke-NtfyPublish $msg)) {
        Write-Host "[relay] falling back to CF Worker"
        if (-not (Invoke-CFPublish $msg)) {
            Write-Host "[relay] all methods failed"
        }
    }
}

function Invoke-NtfyPoll {
    try {
        return Invoke-RestMethod -Uri "$NTFY_BASE/$TOPIC/json?poll=1" `
            -TimeoutSec $NtfyTimeout -ErrorAction Stop
    } catch {
        Write-Host "[ntfy] poll failed: $_"
        return $null
    }
}

function Invoke-CFPoll {
    if (-not $CF_URL) { return $null }
    try {
        $headers = @{ "Authorization" = "Bearer $CF_SECRET" }
        return Invoke-RestMethod -Uri "$CF_URL/relay?key=$TOPIC" -Method GET `
            -Headers $headers -TimeoutSec 10 -ErrorAction Stop
    } catch {
        Write-Host "[cf] poll error: $_"
        return $null
    }
}

if ($Mode -eq "pub") {
    if (-not $Msg) { Write-Host "Usage: -Mode pub -Msg <vague_code>"; exit 1 }
    Invoke-RelayPublish $Msg
} elseif ($Mode -eq "poll") {
    Write-Host "[relay] polling topic $TOPIC every ${PollInterval}s"
    while ($true) {
        $data = Invoke-NtfyPoll
        if (-not $data) { $data = Invoke-CFPoll }
        if ($data) { Write-Host "[recv] $data" }
        Start-Sleep -Seconds $PollInterval
    }
} elseif ($Mode -eq "test") {
    Write-Host "[test] topic=$TOPIC ntfy=$NTFY_BASE cf=$CF_URL"
    Invoke-RelayPublish "STATUS:TEST ts=$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"
}
