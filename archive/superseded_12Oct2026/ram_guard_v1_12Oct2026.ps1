# Auto RAM protect: every 15s, if free RAM < $min KB, close memory hogs (never terminal/claude/powershell/metaeditor). Stop: create Signal\ram_guard.stop
$min=700000; $log='C:\Users\endos\Signal\data\ram_guard_log_12Oct2026.txt'; $stop='C:\Users\endos\Signal\ram_guard.stop'
$kill='chrome','PhoneExperienceHost','msedge','OneDrive','Teams','ms-teams','Spotify','Discord','Dropbox','YourPhone','GameBar','Widgets'
"START $(Get-Date)" | Out-File $log -Append -Encoding utf8
while(-not (Test-Path $stop)){
  $f=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
  if($f -lt $min){
    $n=@(Get-Process -Name $kill -ErrorAction SilentlyContinue)
    if($n.Count){ $n | Stop-Process -Force -ErrorAction SilentlyContinue; "$(Get-Date) free=$f KB closed: $(($n.Name | Sort -Unique) -join ',')" | Out-File $log -Append -Encoding utf8 }
    else { "$(Get-Date) free=$f KB nothing to close" | Out-File $log -Append -Encoding utf8 }
  }
  Start-Sleep 15
}
"STOP $(Get-Date)" | Out-File $log -Append -Encoding utf8
