# compress_encrypt.ps1 — Auto-compress + AES-256 encrypt Signal project files
# Recommended format: 7-Zip .7z (AES-256, encrypted filenames, best compression)
# Fallback if 7-Zip not installed: PowerShell .zip + AES-256 .enc (no external tools)
#
# Usage:
#   Encrypt:      .\compress_encrypt.ps1 -Password "yourPassphrase42!"
#   Decrypt:      .\compress_encrypt.ps1 -Mode decrypt -Password "yourPassphrase42!" [-InFile backup.7z.enc]
#   List backups: .\compress_encrypt.ps1 -Mode list
#   Make SFX exe: .\compress_encrypt.ps1 -SFX    (7-Zip must be installed; no password for SFX)
#   Auto-schedule daily: .\compress_encrypt.ps1 -Password "..." -AutoSchedule
#
# Security: AES-256-CBC, PBKDF2-SHA256 100,000 iterations, 32-byte random salt
# For real security use a passphrase 20+ chars: "correct-horse-battery-staple-42!"
# Store it in Bitwarden / 1Password — AES-256 has no backdoor.

param(
    [ValidateSet("encrypt","decrypt","list")]
    [string]$Mode = "encrypt",
    [string]$Password     = "",
    [string]$InFile       = "",
    [string]$OutDir       = "",
    [switch]$SFX,            # create self-extracting .exe (7-Zip only, no password)
    [switch]$AutoSchedule,
    [switch]$KeepPlaintext
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path $MyInvocation.MyCommand.Path -Parent
$ProjectRoot = Split-Path $ScriptDir -Parent
if ($OutDir -eq "") { $OutDir = Join-Path $ScriptDir "encrypted_backups" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$IncludePaths = @(
    "backups", "data", "results", "dashboard", "app_addons",
    "cost_model.json", "universe.txt", "PLAN.md"
) | ForEach-Object { Join-Path $ProjectRoot $_ } | Where-Object { Test-Path $_ }

$stamp = Get-Date -Format "yyyyMMdd-HHmm"

#--- Detect 7-Zip
$7z = $null
foreach ($p in @("C:\Program Files\7-Zip\7z.exe",
                  "C:\Program Files (x86)\7-Zip\7z.exe",
                  (Get-Command "7z.exe" -ErrorAction SilentlyContinue)?.Source)) {
    if ($p -and (Test-Path $p)) { $7z = $p; break }
}

#==================================================================
# ENCRYPT MODE
#==================================================================
if ($Mode -eq "encrypt") {

    if ($Password -eq "" -and -not $SFX) {
        $sec  = Read-Host "Passphrase" -AsSecureString
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
        $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if ($Password -ne "" -and $Password.Length -lt 12) {
        Write-Warning "Short passphrase — use 20+ chars for real security."
    }

    # --- Path A: 7-Zip available → .7z with AES-256 encrypted headers (best)
    if ($7z) {
        $archPath = Join-Path $OutDir "signal_backup_$stamp.7z"
        Write-Host "Using 7-Zip: $7z"
        Write-Host "Creating encrypted .7z archive -> $archPath"

        $args = @("a", $archPath) + $IncludePaths + @(
            "-t7z",          # 7z format
            "-m0=lzma2",     # LZMA2 compression
            "-mx=5",         # compression level 5 (fast+good)
            "-mmt=on"        # multi-thread
        )
        if ($SFX) {
            # Self-extracting exe — no password (AV may flag; user accepts)
            $archPath = Join-Path $OutDir "signal_backup_$stamp.exe"
            $args = @("a", $archPath, "-sfx7z.sfx") + $IncludePaths + @("-t7z","-m0=lzma2","-mx=5")
            Write-Host "SFX mode: creating self-extracting .exe (no password)"
        } else {
            # AES-256 with encrypted filenames (-mhe=on hides file list too)
            $args += @("-p$Password", "-mhe=on")
        }
        & $7z @args | Out-Null
        $sizeMB = [math]::Round((Get-Item $archPath).Length / 1MB, 2)
        Write-Host "Done: $archPath (${sizeMB} MB)"
        if ($SFX) { Write-Host "Run the .exe to extract (no password needed)." }
        else       { Write-Host "Open with 7-Zip, enter passphrase to extract." }
    }

    # --- Path B: No 7-Zip → PowerShell ZIP + AES-256 .enc file
    else {
        Write-Host "7-Zip not found. Using PowerShell ZIP + AES-256 encryption."
        $zipPath = Join-Path $env:TEMP "signal_backup_$stamp.zip"
        $encPath = Join-Path $OutDir  "signal_backup_$stamp.zip.enc"

        Write-Host "Compressing -> $zipPath"
        Compress-Archive -Path $IncludePaths -DestinationPath $zipPath -CompressionLevel Optimal -Force
        $zipMB = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
        Write-Host "  Compressed: ${zipMB} MB"

        Write-Host "Encrypting (AES-256-CBC, PBKDF2-SHA256 x100000) -> $encPath"
        Encrypt-AES $zipPath $encPath $Password
        if (-not $KeepPlaintext) { Remove-Item $zipPath -Force }

        $encMB = [math]::Round((Get-Item $encPath).Length / 1MB, 2)
        Write-Host "Done: $encPath (${encMB} MB)"
        Write-Host "Decrypt: run this script -Mode decrypt -InFile '$encPath'"
    }

    # --- Auto-schedule daily task
    if ($AutoSchedule) {
        $encPass = ConvertTo-SecureString $Password -AsPlainText -Force | ConvertFrom-SecureString
        Set-Content (Join-Path $ScriptDir "backup_key.dpapi") $encPass
        $sp = $MyInvocation.MyCommand.Path
        $arg = "-NonInteractive -ExecutionPolicy Bypass -File `"$sp`" -Mode encrypt " +
               "-Password (ConvertTo-SecureString (Get-Content `"$ScriptDir\backup_key.dpapi`") " +
               "| ConvertFrom-SecureString)"
        $action  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
        $trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
        Register-ScheduledTask -TaskName "SignalAutoBackup" -Action $action `
                               -Trigger $trigger -RunLevel Highest -Force | Out-Null
        Write-Host "Scheduled task 'SignalAutoBackup' set for 02:00 daily."
        Write-Host "Passphrase stored DPAPI-encrypted (this Windows user only): backup_key.dpapi"
    }
}

#==================================================================
# DECRYPT MODE
#==================================================================
elseif ($Mode -eq "decrypt") {

    if ($InFile -eq "") {
        $files = Get-ChildItem $OutDir -Filter "*.enc","*.7z" -ErrorAction SilentlyContinue |
                 Sort-Object LastWriteTime -Descending
        if (-not $files) { Write-Error "No backup files in $OutDir"; exit 1 }
        $InFile = $files[0].FullName
        Write-Host "Auto-selected: $InFile"
    }

    if ($InFile -like "*.7z") {
        if (-not $7z) { Write-Error "7-Zip required to decrypt .7z files. Install from https://7-zip.org" }
        if ($Password -eq "") {
            $sec  = Read-Host "Passphrase" -AsSecureString
            $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
            $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
            [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
        $outD = Join-Path $OutDir "restored_$stamp"
        New-Item -ItemType Directory -Force -Path $outD | Out-Null
        & $7z e $InFile "-o$outD" "-p$Password" -y | Out-Null
        Write-Host "Extracted to: $outD"
    } else {
        # .enc file — PowerShell AES
        if ($Password -eq "") {
            $sec  = Read-Host "Passphrase" -AsSecureString
            $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
            $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
            [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
        $outZip = [IO.Path]::ChangeExtension($InFile, ".zip")
        Decrypt-AES $InFile $outZip $Password
        Write-Host "Decrypted to: $outZip  — use Expand-Archive to restore."
    }
}

#==================================================================
# LIST MODE
#==================================================================
elseif ($Mode -eq "list") {
    if (Test-Path $OutDir) {
        Get-ChildItem $OutDir -Include "*.7z","*.enc","*.exe" -Recurse |
        Sort-Object LastWriteTime -Descending |
        Format-Table Name, @{L="MB";E={[math]::Round($_.Length/1MB,2)}}, LastWriteTime
    } else { Write-Host "No backup directory at $OutDir" }
}

#==================================================================
# AES-256 HELPERS (fallback path — no 7-Zip)
#==================================================================
function Encrypt-AES($src, $dst, $pass) {
    $salt = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($salt)
    $kd  = [Security.Cryptography.Rfc2898DeriveBytes]::new(
               $pass, $salt, 100000,
               [Security.Cryptography.HashAlgorithmName]::SHA256)
    $aes = [Security.Cryptography.Aes]::Create()
    $aes.Key = $kd.GetBytes(32); $aes.IV = $kd.GetBytes(16)
    $aes.Mode = "CBC"; $aes.Padding = "PKCS7"
    $fsI = [IO.File]::OpenRead($src); $fsO = [IO.File]::Create($dst)
    # Header: "SLCE" + v1 + iterations(4) + salt(32)
    $fsO.Write([Text.Encoding]::ASCII.GetBytes("SLCE"), 0, 4)
    $fsO.WriteByte(1)
    $fsO.Write([BitConverter]::GetBytes([int]100000), 0, 4)
    $fsO.Write($salt, 0, 32)
    $cs = [Security.Cryptography.CryptoStream]::new($fsO, $aes.CreateEncryptor(), "Write")
    $fsI.CopyTo($cs); $cs.FlushFinalBlock()
    $cs.Dispose(); $fsI.Dispose(); $fsO.Dispose(); $aes.Dispose()
}

function Decrypt-AES($src, $dst, $pass) {
    $fsI = [IO.File]::OpenRead($src)
    $mag = New-Object byte[] 4; $fsI.Read($mag,0,4)|Out-Null
    if ([Text.Encoding]::ASCII.GetString($mag) -ne "SLCE") { throw "Not a Signal .enc file" }
    $fsI.ReadByte() | Out-Null  # version
    $ib = New-Object byte[] 4; $fsI.Read($ib,0,4)|Out-Null
    $iter = [BitConverter]::ToInt32($ib,0)
    $salt = New-Object byte[] 32; $fsI.Read($salt,0,32)|Out-Null
    $kd  = [Security.Cryptography.Rfc2898DeriveBytes]::new(
               $pass, $salt, $iter,
               [Security.Cryptography.HashAlgorithmName]::SHA256)
    $aes = [Security.Cryptography.Aes]::Create()
    $aes.Key = $kd.GetBytes(32); $aes.IV = $kd.GetBytes(16)
    $aes.Mode = "CBC"; $aes.Padding = "PKCS7"
    $fsO = [IO.File]::Create($dst)
    $cs  = [Security.Cryptography.CryptoStream]::new($fsI, $aes.CreateDecryptor(), "Read")
    $cs.CopyTo($fsO)
    $cs.Dispose(); $fsI.Dispose(); $fsO.Dispose(); $aes.Dispose()
}
