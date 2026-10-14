# popup_view.ps1 - shows one dark report page in its own Chrome app window and closes it after N seconds.
# Buttons on the page call this script's tiny localhost listener: /set?s=30|60|120 (also saves default), /keep, /close.
param([string]$Page,[string]$Tag,[int]$Seconds=60,[int]$Port=8790)
$Out='C:\Users\endos\Desktop\hst_out'; $prof="$env:TEMP\mt4_report_view_$Tag"
$l=New-Object Net.HttpListener; $l.Prefixes.Add("http://localhost:$Port/")
try { $l.Start() } catch { $l=$null }
$url="file:///$($Page -replace '\\','/')?port=$Port&s=$Seconds"
Start-Process 'C:\Program Files\Google\Chrome\Application\chrome.exe' -ArgumentList "--user-data-dir=$prof","--new-window","--window-size=1400,800","--window-position=40,40","--app=$url"
$end=(Get-Date).AddSeconds($Seconds); $keep=$false
while($keep -or (Get-Date) -lt $end){
  if($l){ $ar=$l.BeginGetContext($null,$null); if($ar.AsyncWaitHandle.WaitOne(1000)){ $cx=$l.EndGetContext($ar); $q=$cx.Request.Url
      if($q.AbsolutePath -eq '/set'){ $s=[int]$cx.Request.QueryString['s']; if($s -gt 0){ $end=(Get-Date).AddSeconds($s); $keep=$false; Set-Content "$Out\popup_seconds.txt" $s } }
      elseif($q.AbsolutePath -eq '/keep'){ $keep=$true } elseif($q.AbsolutePath -eq '/close'){ $keep=$false; $end=Get-Date }
      $cx.Response.AddHeader('Access-Control-Allow-Origin','*'); $b=[Text.Encoding]::ASCII.GetBytes('ok'); $cx.Response.OutputStream.Write($b,0,2); $cx.Response.Close() } }
  else { Start-Sleep 1 }
  if($keep -and -not (Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | ?{ $_.CommandLine -like "*mt4_report_view_$Tag*" })){ break }
}
if($l){ $l.Stop() }
Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | ?{ $_.CommandLine -like "*mt4_report_view_$Tag*" } | %{ Stop-Process -Id $_.ProcessId -Force -EA 0 }
