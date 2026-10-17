#Requires -Version 5.1
<#
.SYNOPSIS
    Patches the Claude Code CLI to use Node instead of Bun as its JS runtime.
    Fully reversible — bun.exe is backed up as bun.exe.bak.

.USAGE
    # Apply patch
    .\patch_bun_to_node.ps1

    # Undo patch (restore original bun.exe)
    .\patch_bun_to_node.ps1 -Undo
#>
param(
    [switch]$Undo
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── 1. Locate Claude Code install dir ────────────────────────────────────────
$candidates = @(
    "$env:APPDATA\npm\node_modules\@anthropic-ai\claude-code",
    "$env:LOCALAPPDATA\Programs\claude-code",
    "$env:LOCALAPPDATA\Programs\@anthropic-ai\claude-code",
    (& { try { (Get-Command claude -ErrorAction Stop).Source | Split-Path | Split-Path } catch {} })
) | Where-Object { $_ -and (Test-Path $_) }

if (-not $candidates) {
    Write-Error "Cannot locate Claude Code install dir. Run: (Get-Command claude).Source"
}
$installDir = $candidates[0]
Write-Host "Install dir: $installDir"

# ── 2. Find bundled bun.exe ───────────────────────────────────────────────────
$bunExe = Get-ChildItem -Path $installDir -Recurse -Filter 'bun.exe' -ErrorAction SilentlyContinue |
          Select-Object -First 1 -ExpandProperty FullName

if (-not $bunExe) {
    Write-Error "bun.exe not found under $installDir"
}
Write-Host "Found: $bunExe"
$bakPath = "$bunExe.bak"

# ── 3. Undo mode ─────────────────────────────────────────────────────────────
if ($Undo) {
    if (-not (Test-Path $bakPath)) {
        Write-Error "Backup not found at $bakPath — nothing to restore."
    }
    Copy-Item -Path $bakPath -Destination $bunExe -Force
    Write-Host "Restored original bun.exe from backup."
    & claude --version
    return
}

# ── 4. Already patched? ───────────────────────────────────────────────────────
if (Test-Path $bakPath) {
    Write-Host "Patch already applied (bun.exe.bak exists). Run with -Undo to revert."
    return
}

# ── 5. Find node.exe ─────────────────────────────────────────────────────────
$nodeExe = (Get-Command node -ErrorAction SilentlyContinue)?.Source
if (-not $nodeExe) {
    Write-Error "node.exe not found in PATH. Install Node first."
}
Write-Host "Node: $nodeExe  ($(& node --version))"

# ── 6. Backup original bun.exe ───────────────────────────────────────────────
Copy-Item -Path $bunExe -Destination $bakPath -Force
Write-Host "Backup saved: $bakPath"

# ── 7. Write shim: a tiny CMD launcher that forwards to node.exe ─────────────
#
#  Claude Code launches bun.exe <script> [args].
#  The shim receives those same args and passes them to node.exe unchanged.
#  We write a .cmd shim with the same name via cmd /c copy trick so it's a
#  real PE-less executable-equivalent on Windows.
#
#  Strategy: write a .cmd file next to the .exe, then replace bun.exe with a
#  tiny self-extracting .cmd-runner .exe — but the simplest approach on
#  Windows is a .cmd that is renamed to .exe.  CMD.exe will refuse to run
#  a .cmd renamed to .exe directly, so instead we write a PowerShell-compiled
#  tiny native wrapper EXE.

$shimSource = @"
using System;
using System.Diagnostics;
using System.IO;

class BunShim {
    static int Main(string[] args) {
        var node = @"$($nodeExe.Replace('\','\\'))";
        var psi = new ProcessStartInfo(node) {
            UseShellExecute = false
        };
        foreach (var a in args) psi.ArgumentList.Add(a);
        var p = Process.Start(psi)!;
        p.WaitForExit();
        return p.ExitCode;
    }
}
"@

$shimCs  = "$env:TEMP\bun_shim.cs"
$shimExe = "$env:TEMP\bun_shim.exe"
Set-Content -Path $shimCs -Value $shimSource -Encoding UTF8

# Compile with the .NET SDK csc or the Roslyn compiler shipped with VS / .NET
$csc = (Get-Command csc.exe -ErrorAction SilentlyContinue)?.Source
if (-not $csc) {
    # Try dotnet script / Roslyn shipped inside .NET SDK
    $dotnet = (Get-Command dotnet -ErrorAction SilentlyContinue)?.Source
    if ($dotnet) {
        # Use dotnet-script approach: create a temp csproj
        $proj = "$env:TEMP\bunshim"
        New-Item -ItemType Directory -Path $proj -Force | Out-Null
        Set-Content "$proj\Program.cs" -Value $shimSource -Encoding UTF8
        Set-Content "$proj\bunshim.csproj" -Value @'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
    <SelfContained>false</SelfContained>
    <AssemblyName>bun</AssemblyName>
  </PropertyGroup>
</Project>
'@ -Encoding UTF8
        & dotnet publish "$proj\bunshim.csproj" -c Release -o "$proj\out" --nologo -v q 2>&1 | Out-Null
        $shimExe = "$proj\out\bun.exe"
    }
    else {
        Write-Error "No C# compiler (csc.exe) or dotnet SDK found. Cannot build shim."
    }
}
else {
    & $csc /out:$shimExe /target:exe $shimCs 2>&1 | Out-Null
}

if (-not (Test-Path $shimExe)) {
    Write-Error "Shim compile failed."
}

Copy-Item -Path $shimExe -Destination $bunExe -Force
Write-Host "Shim installed at: $bunExe"

# ── 8. Verify ────────────────────────────────────────────────────────────────
Write-Host "`nVerifying claude --version ..."
& claude --version
Write-Host "`nDone. To undo: .\patch_bun_to_node.ps1 -Undo"
