# patch_settings.ps1 - Add missing allow entries to Claude Code settings.json
# Idempotent: skips entries already present. Never removes existing entries.
# Run as: powershell -ExecutionPolicy Bypass -File patch_settings.ps1

$SettingsPath = "$env:USERPROFILE\.claude\settings.json"

$ToAdd = @(
    "mcp__remote-devices__*",
    "mcp__hearthbot__*",
    "Bash(git*)",
    "Bash(node*)",
    "Bash(npm*)",
    "Bash(npx*)",
    "Bash(python*)",
    "Bash(schtasks*)",
    "Bash(sc *)"
)

if (-not (Test-Path $SettingsPath)) {
    Write-Host "[ERROR] Not found: $SettingsPath"
    Write-Host "        Run Claude Code at least once to create it, then re-run this script."
    exit 1
}

try {
    $raw = Get-Content $SettingsPath -Raw -Encoding UTF8
    $s = $raw | ConvertFrom-Json -AsHashtable
} catch {
    Write-Host "[ERROR] Could not parse settings.json: $_"
    exit 1
}

# Ensure path exists
if (-not $s.ContainsKey('permissions'))        { $s['permissions'] = @{} }
if (-not $s.permissions.ContainsKey('allow'))  { $s.permissions['allow'] = @() }

$existing = [System.Collections.Generic.List[string]]($s.permissions.allow)
$added = 0
foreach ($entry in $ToAdd) {
    if ($existing -notcontains $entry) {
        $existing.Add($entry)
        Write-Host "  + $entry"
        $added++
    } else {
        Write-Host "  = $entry  (already present)"
    }
}

$s.permissions.allow = $existing.ToArray()

# Write back, preserving other keys
$s | ConvertTo-Json -Depth 20 | Set-Content $SettingsPath -Encoding UTF8

Write-Host ""
Write-Host "[OK] settings.json updated (+$added new entries). Path: $SettingsPath"
if ($added -gt 0) {
    Write-Host "     Restart Claude Code for changes to take effect."
}
