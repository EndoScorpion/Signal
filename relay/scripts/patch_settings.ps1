# patch_settings.ps1 — patch DC Remote settings.json on Windows PowerShell 5.1
# Usage: powershell.exe -ExecutionPolicy Bypass -File "C:\Users\endos\Desktop\hst_work\Signal\relay\scripts\patch_settings.ps1"

$settingsPath = "C:\Users\endos\.desktop-commander\settings.json"
$backupPath   = "C:\Users\endos\.desktop-commander\settings.json.bak"

if (-not (Test-Path $settingsPath)) {
    Write-Host "settings.json not found at $settingsPath"
    exit 1
}

Copy-Item -Path $settingsPath -Destination $backupPath -Force

$raw = Get-Content -Path $settingsPath -Raw -Encoding UTF8
$obj = ConvertFrom-Json -InputObject $raw

# PS 5.1 compatible property update — walk PSObject NoteProperty members
function Set-JsonProp {
    param($obj, [string]$key, $value)
    $member = $obj.PSObject.Properties[$key]
    if ($member) {
        $member.Value = $value
    } else {
        $obj | Add-Member -MemberType NoteProperty -Name $key -Value $value
    }
}

# --- patches ---
Set-JsonProp $obj "blockedCommands"   @()
Set-JsonProp $obj "defaultShell"      "powershell.exe"
Set-JsonProp $obj "allowedDirectories" @(
    "C:\Users\endos\Desktop\hst_work",
    "C:\Users\endos\Desktop\hst_out",
    "C:\tools"
)

$patched = ConvertTo-Json -InputObject $obj -Depth 10
[System.IO.File]::WriteAllText($settingsPath, $patched, [System.Text.Encoding]::UTF8)

Write-Host "Patched: $settingsPath (backup: $backupPath)"
