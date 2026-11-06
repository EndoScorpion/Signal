# share.ps1 — Upload a file to signal-status/shared/ via GitHub API, return raw URL
# Usage: .\share.ps1 -FilePath "path\to\file"
# Usage: .\share.ps1 -FilePath "path\to\file" -Token "ghp_xxx"  (override token)
# Reads token from $env:GITHUB_TOKEN or $env:GH_TOKEN or C:\Users\endos\.claude\.gh_token

param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [string]$Token = "",
    [string]$Repo = "endoscorpion/signal-status",
    [string]$Branch = "main"
)

# Resolve token
if (-not $Token) {
    $Token = $env:GITHUB_TOKEN
    if (-not $Token) { $Token = $env:GH_TOKEN }
    if (-not $Token) {
        $keyFile = "$env:USERPROFILE\.claude\.gh_token"
        if (Test-Path $keyFile) { $Token = (Get-Content $keyFile -Raw).Trim() }
    }
}
if (-not $Token) {
    Write-Error "No GitHub token found. Set GITHUB_TOKEN env var or put token in $env:USERPROFILE\.claude\.gh_token"
    exit 1
}

# Read and encode file
if (-not (Test-Path $FilePath)) { Write-Error "File not found: $FilePath"; exit 1 }
$fileName = [System.IO.Path]::GetFileName($FilePath)
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $FilePath))
$b64 = [Convert]::ToBase64String($bytes)

# Build remote path with timestamp prefix to avoid collisions
$ts = (Get-Date -Format "yyyyMMdd_HHmmss")
$remotePath = "shared/${ts}_${fileName}"

# Check if file exists (need SHA to update)
$headers = @{
    "Authorization" = "token $Token"
    "Accept"        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}
$apiBase = "https://api.github.com/repos/$Repo/contents/$remotePath"

$sha = $null
try {
    $existing = Invoke-RestMethod -Uri $apiBase -Headers $headers -Method Get -ErrorAction Stop
    $sha = $existing.sha
} catch {}

# Build payload
$payload = @{ message = "share: $fileName"; content = $b64; branch = $Branch }
if ($sha) { $payload.sha = $sha }
$body = $payload | ConvertTo-Json

# Upload
try {
    $result = Invoke-RestMethod -Uri $apiBase -Headers $headers -Method Put -Body $body -ContentType "application/json"
    $rawUrl = "https://raw.githubusercontent.com/$Repo/$Branch/$remotePath"
    Write-Host ""
    Write-Host "Uploaded: $fileName" -ForegroundColor Green
    Write-Host "Raw URL : $rawUrl" -ForegroundColor Cyan
    Write-Host ""
    # Also copy URL to clipboard if available
    try { $rawUrl | Set-Clipboard; Write-Host "(URL copied to clipboard)" -ForegroundColor Gray } catch {}
    return $rawUrl
} catch {
    Write-Error "Upload failed: $_"
    exit 1
}
