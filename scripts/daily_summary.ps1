# Once-a-day summary: short ntfy alert to the phone + full text file saved locally and pushed to the phone's Downloads when adb sees it.
# Read-only on all results. Works offline (the alert is skipped, the file is still written). Log: data\daily_summary_log.txt
. 'C:\Users\endos\Signal\scripts\phone_notify.ps1'
$sig = 'C:\Users\endos\Signal'; $d = Get-Date -Format yyyyMMdd; $f = "$sig\data\daily_summary_$d.txt"
Set-Location $sig
$text = python -E -P data\daily_summary.py 2>&1
$lines = @($text); $lines | Set-Content $f -Encoding utf8
Send-Phone ($lines -join "`n") -Title 'EA daily summary' -Max 3800   # full text over ntfy: reaches the phone anywhere with internet
$adb = "$sig\adb_tools\platform-tools\adb.exe"; $pushed = 'no'
if (Test-Path $adb) { $dev = (& $adb devices) -match "`tdevice$"; if ($dev) { & $adb push $f "/sdcard/Download/ea_daily_summary_$d.txt" | Out-Null; $pushed = 'yes' } }
Add-Content "$sig\data\daily_summary_log.txt" ("{0} summary written, file pushed to phone: {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm'), $pushed)
Get-ChildItem "$sig\data\daily_summary_*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 14 | ForEach-Object { }   # old summaries are kept, not deleted
