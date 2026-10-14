# run_tester.ps1 - unattended MT4 Strategy Tester run (portable copy, never touches the live terminal)
# Usage (PowerShell):
#   powershell -ExecutionPolicy Bypass -File C:\Users\endos\Desktop\hst_out\run_tester.ps1 -Expert Strong2010b_claude_b7 -From 2019.01.01 -To 2019.12.31
param(
  [string]$Expert = "Strong2010b_claude_b7",
  [string]$SetFile = "",                 # file name inside mt4_tester\tester\ ; default <Expert>.set
  [string]$Symbol = "EURUSD",
  [string]$Period = "M15",
  [int]$Model = 0,                       # 0=every tick 1=control points 2=open prices
  [int]$Spread = 0,                      # 0 = current/last known spread
  [string]$From = "2019.01.01",
  [string]$To = "2019.12.31",
  [string]$Tag = "",
  [int]$TimeoutMin = 120
)
$ErrorActionPreference = "Stop"
$Live = "$env:APPDATA\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415"
# $P is chosen by the copy selector below (mt4_tester or mt4_tester2)
$Out  = "C:\Users\endos\Desktop\hst_out"
if (-not $SetFile) { $SetFile = "$Expert.set" }
if (-not $Tag) { $Tag = "{0}_{1}_{2}_{3}" -f $Expert, $Period, $From.Substring(0,4), $To.Substring(0,4) }

# 0. GLOBAL PAUSE (Nasif 2026-10-12): while hst_out\MT4_PAUSE exists, no session may start an MT4 tester. Delete the file to resume.
if (Test-Path "$Out\MT4_PAUSE") { Write-Output "PAUSED: hst_out\MT4_PAUSE exists - no MT4 started"; exit 6 }

# 1. refuse to start if the portable copy is already running a test
# copy selector: first free isolated tester copy wins; an exclusive lock file held for this script's lifetime prevents races
$P=$null; $lock=$null
foreach($cand in 'C:\Users\endos\Desktop\mt4_tester','C:\Users\endos\Desktop\mt4_tester2'){
  if(Get-Process terminal -EA 0 | ? { $_.Path -like "$cand\*" }){ continue }
  try { $lock=[IO.File]::Open("$cand\run.lock",'OpenOrCreate','ReadWrite','None'); $P=$cand; break } catch { $lock=$null } }
if (-not $P) { Write-Output "BUSY: both tester copies are running"; exit 2 }

# 2. sync latest compiled EA + Include/Libraries/Indicators from the live data folder (read-only on live side)
robocopy "$Live\MQL4" "$P\MQL4" /E /XD Logs /NFL /NDL /NJH /NJS /NP | Out-Null
$src = Join-Path $Live "tester\$SetFile"
if (Test-Path $src) { Copy-Item $src "$P\tester\$SetFile" -Force }
$s1="C:\Users\endos\Desktop\mt4_tester\tester\$SetFile"; if ($P -ne "C:\Users\endos\Desktop\mt4_tester" -and (Test-Path $s1)) { Copy-Item $s1 "$P\tester\$SetFile" -Force }  # sets live in copy 1
if (-not (Test-Path "$P\tester\$SetFile")) { throw "Set file not found: $P\tester\$SetFile" }

# 3. write config (MT4 uses Test* keys, not the MT5 Expert=/Symbol= keys)
$report = "reports\$Tag"
New-Item -ItemType Directory -Force "$P\reports" | Out-Null
$ini = @"
; common
Login=892151
Server=FXOpenEU-ECN Live Server
ExpertsEnable=true
NewsEnable=false
; tester (MT4 config is flat: no [sections])
TestExpert=$Expert
TestExpertParameters=$SetFile
TestSymbol=$Symbol
TestPeriod=$Period
TestModel=$Model
TestSpread=$Spread
TestOptimization=false
TestDateEnable=true
TestFromDate=$From
TestToDate=$To
TestReport=$report
TestReplaceReport=true
TestShutdownTerminal=true
TestVisualEnable=false
"@
$cfg = "$P\config\auto_$Tag.ini"
Set-Content -Path $cfg -Value $ini -Encoding ASCII
Copy-Item $cfg "$Out\tester_auto.ini" -Force

if (Test-Path "C:\Users\endos\MT4_Backtest\PAUSE") { Write-Output "PAUSED (MT4_Backtest\PAUSE exists) - not launching MT4"; exit 7 }
# 4. LAUNCH PORTABLE INSTANCE AND WAIT FOR IT TO SHUT ITSELF DOWN
$t0 = Get-Date
# launch minimized WITHOUT activation (ShowWindow 7 = SW_SHOWMINNOACTIVE) so the tester never steals keyboard focus (Nasif 2026-10-12)
$su = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ ShowWindow = [uint16]7 }
$cr = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = "`"$P\terminal.exe`" `"$cfg`" /portable"; CurrentDirectory = $P; ProcessStartupInformation = $su }   # MT4: ini path as plain first arg, NOT /config:
if ($cr.ReturnValue -ne 0) { Write-Output "LAUNCH FAILED code $($cr.ReturnValue)"; exit 5 }
$proc = Get-Process -Id $cr.ProcessId
Add-Type 'using System;using System.Runtime.InteropServices;public class MinW{[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int c);[DllImport("user32.dll")]public static extern bool IsIconic(IntPtr h);}' -EA 0
$deadline=(Get-Date).AddMinutes($TimeoutMin); while(-not $proc.HasExited -and (Get-Date) -lt $deadline){ Get-Process terminal -EA 0 | ? { $_.Path -like "$P\*" -and $_.MainWindowHandle -ne 0 } | % { if(-not [MinW]::IsIconic($_.MainWindowHandle)){ [MinW]::ShowWindow($_.MainWindowHandle,7) | Out-Null } }; Start-Sleep -Milliseconds 500 }
if (-not $proc.WaitForExit($TimeoutMin * 60000)) { Stop-Process -Id $proc.Id -Force; Write-Output "TIMEOUT after $TimeoutMin min"; exit 3 }

# 5. collect report
$htm = Get-ChildItem "$P\reports" -Filter "$Tag*.htm" -EA 0 | ? { $_.LastWriteTime -ge $t0 }
if (-not $htm) { Write-Output "NO REPORT - check $P\tester\logs"; exit 4 }
Copy-Item "$P\reports\$Tag*" $Out -Force
$min = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
Write-Output "OK $Tag in $min min -> $Out\$Tag.htm"







