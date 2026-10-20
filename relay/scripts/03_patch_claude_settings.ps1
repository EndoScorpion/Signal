# 03_patch_claude_settings.ps1 - Patch Claude Code settings.json to allow relay tools
# Adds allowedTools entries so the poller/relay can run without permission prompts.
# Idempotent: merges into existing settings, does not overwrite.

$settingsPaths = @(
    "$env:APPDATA\Claude\settings.json",
    "$env:USERPROFILE\.claude\settings.json",
    "$env:APPDATA\Claude Code\settings.json"
)

$allowedTools = @(
    "Bash",
    "Read", "Write", "Edit", "Glob", "Grep",
    "mcp__github__*",
    "mcp__Remote_Desktop_Commander__*",
    "mcp__remote-devices__*"
)

function Patch-Settings($path) {
    $dir = Split-Path $path -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

    $settings = @{}
    if (Test-Path $path) {
        try { $settings = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable }
        catch { Write-Host "[WARN] Could not parse $path - creating fresh."; $settings = @{} }
    }

    if (-not $settings.ContainsKey('permissions')) { $settings['permissions'] = @{} }
    if (-not $settings.permissions.ContainsKey('allow')) { $settings.permissions['allow'] = @() }

    $existing = @($settings.permissions.allow)
    $added = 0
    foreach ($tool in $allowedTools) {
        if ($existing -notcontains $tool) {
            $existing += $tool
            $added++
        }
    }
    $settings.permissions.allow = $existing

    $settings | ConvertTo-Json -Depth 10 | Set-Content $path -Encoding UTF8
    Write-Host "[OK] Patched $path (+$added new entries)"
}

$patched = 0
foreach ($p in $settingsPaths) {
    $dir = Split-Path $p -Parent
    # Patch if file exists OR if parent dir exists (Claude is installed there)
    if ((Test-Path $p) -or (Test-Path $dir)) {
        Patch-Settings $p
        $patched++
    }
}

if ($patched -eq 0) {
    # Write to the most common path anyway
    Patch-Settings $settingsPaths[0]
    Write-Host "[INFO] Claude settings folder not found - wrote to default location."
    Write-Host "       If Claude Code is installed elsewhere, copy settings.json there."
}
