# Auto RAM protect v2. Tier1 (<1000MB free): TRIM working sets of Claude desktop + Chrome/Edge (apps stay open, RAM released, pages back on demand).
# Tier2 (<700MB): close background hogs (never Claude, MT4, PowerShell, MetaEditor). Tier3 (<450MB): close Chrome/Edge too (last resort).
# Stop: create Signal\ram_guard.stop
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("psapi.dll")] public static extern bool EmptyWorkingSet(IntPtr h);'
$log='C:\Users\endos\Signal\data\ram_guard_log_12Oct2026.txt'; $stop='C:\Users\endos\Signal\ram_guard.stop'
$trim='claude','chrome','msedge','Claude'; $hogs='PhoneExperienceHost','OneDrive','Teams','ms-teams','Spotify','Discord','Dropbox','YourPhone','GameBar','Widgets'
"START v2 $(Get-Date)" | Out-File $log -Append -Encoding utf8
while(-not (Test-Path $stop)){
  $f=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
  if($f -lt 1000000){
    $c=0; foreach($p in Get-Process -Name $trim -ErrorAction SilentlyContinue){ try{ if([W.P]::EmptyWorkingSet($p.Handle)){$c++} }catch{} }
    $f2=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
    "$(Get-Date) free=$f KB -> trimmed $c procs -> free=$f2 KB" | Out-File $log -Append -Encoding utf8; $f=$f2
  }
  if($f -lt 700000){ $n=@(Get-Process -Name $hogs -ErrorAction SilentlyContinue); if($n.Count){ $n|Stop-Process -Force -ErrorAction SilentlyContinue; "$(Get-Date) tier2 closed: $(($n.Name|Sort -Unique) -join ',')" | Out-File $log -Append -Encoding utf8; $f=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory } }
  if($f -lt 450000){ $n=@(Get-Process -Name chrome,msedge -ErrorAction SilentlyContinue); if($n.Count){ $n|Stop-Process -Force -ErrorAction SilentlyContinue; "$(Get-Date) tier3 closed browsers (free=$f KB)" | Out-File $log -Append -Encoding utf8 } }
  Start-Sleep 15
}
"STOP $(Get-Date)" | Out-File $log -Append -Encoding utf8
