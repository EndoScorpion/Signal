# weekly_history_update.ps1 - weekly EURUSD history refresh (merge, sync, audit, backup, refresh metrics).
# Run when MT4 is fully closed:  powershell -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\weekly_history_update.ps1
# Download step: needs the FXOpen login. This script NEVER stores or reads a plain password. Two safe options:
#   A) You run QuotesDownloader yourself (GUI or CLI) and drop the zips into C:\Users\endos\Signal\data\quotes_download, then run this script.
#   B) One-time, you run in your own PowerShell:  Get-Credential | Export-Clixml C:\Users\endos\Signal\scripts\fxopen_cred.xml
#      (encrypted for your Windows account only). If that file exists this script downloads M1 bid+ask itself.
param([switch]$SkipDownload)
$ErrorActionPreference = "Stop"
$Out = "C:\Users\endos\Desktop\hst_out"; $Sig = "C:\Users\endos\Signal"; $Log = "$Sig\data\weekly_history_log.txt"
function Log($m){ $l = "{0:yyyy-MM-dd HH:mm} {1}" -f (Get-Date), $m; Add-Content $Log $l; Write-Host $l }
if ((Test-Path "$Out\MT4_PAUSE") -or (Test-Path "C:\Users\endos\MT4_Backtest\PAUSE")) { Log "PAUSED (pause file exists) - nothing started"; exit 6 }
if (Get-Process terminal, metatester, metaeditor -ErrorAction SilentlyContinue) { Log "MT4/MetaEditor is running - close it first (history files must not be open). Nothing changed."; exit 3 }
$free = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
if ($free -lt 1.0) { Log ("free RAM {0:N2} GB < 1.0 GB - stopping" -f $free); exit 4 }

$m1 = "C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server\EURUSD1.hst"
$lastTxt = & python -I -c "import struct,datetime;f=open(r'$m1','rb');f.seek(-60,2);t=struct.unpack('<q',f.read(8))[0];print(datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d'))"
Log "last merged M1 bar: $lastTxt"

if (-not $SkipDownload -and (Test-Path "$Sig\scripts\fxopen_cred.xml")) {
  $cred = Import-Clixml "$Sig\scripts\fxopen_cred.xml"; $from = ([datetime]$lastTxt).AddDays(-2).ToString("yyyy-MM-dd"); $to = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")
  $dest = "$Sig\data\quotes_download\weekly_{0:yyyyMMdd}" -f (Get-Date); New-Item -ItemType Directory -Force $dest | Out-Null
  Log "downloading EURUSD M1 $from -> $to (arguments follow the downloader's own --help; confirm once by hand before trusting)"
  & "$Sig\QuotesDownloder.3\QuotesDownloader.exe" --username $cred.UserName --password ($cred.GetNetworkCredential().Password) --symbol EURUSD --periodicity M1 --datefrom $from --dateto $to --output $dest 2>&1 | Select-Object -Last 3 | % { Log "downloader: $_" }
} else { Log "download skipped (no credential file or -SkipDownload): using whatever zips are already in data\quotes_download" }

Log "merging with csv_to_hst.py (also syncs mt4_tester + live terminal copies)"
& python -I "$Sig\data\csv_to_hst.py" 2>&1 | Select-Object -Last 6 | % { Log "merge: $_" }
Log "gap audit of the merged M1"
& python -I "$Sig\data\history_audit.py" 2>&1 | Select-Object -First 25 | % { Log "audit: $_" }
if ($LASTEXITCODE -eq 2) { Log "AUDIT WARNING: thin year or stale last bar - review before testing" }

$bk = "D:\hst_backup_{0:ddMMMyyyy}" -f (Get-Date)
if (Test-Path D:\) {
  robocopy "C:\Users\endos\MT4_Backtest\history\FXOpenEU-ECN Live Server" $bk EURUSD*.hst symbols.raw /R:1 /W:1 /NP /NFL /NDL | Out-Null
  Get-ChildItem D:\ -Directory -Filter "hst_backup_*" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 3 | % { Log "keeping max 3 backups: old backup left for you to remove: $($_.FullName)" }
  Log "backup -> $bk (confirm D: is your flash drive)"
} else { Log "D: not found - backup skipped" }

Log "refreshing M15 metrics for the analysis scripts"
& python -I "$Sig\data\analyze_hst.py" 2>&1 | Select-Object -Last 2 | % { Log "metrics: $_" }
Log "weekly history update done"
