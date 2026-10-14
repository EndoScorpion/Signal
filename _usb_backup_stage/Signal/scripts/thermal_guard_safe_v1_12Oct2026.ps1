# SAFE-MODE overheat protect: no power-plan or system-setting changes. Lowers MT4 priority; pauses MT4 when hot; resumes when cool.
# Stop: create Signal\thermal_guard.stop (MT4 is resumed on exit).
Add-Type -Namespace N -Name S -MemberDefinition '[DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr h); [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr h);'
$log='C:\Users\endos\Signal\data\thermal_guard_log_12Oct2026.txt'; $stop='C:\Users\endos\Signal\thermal_guard.stop'
$HOT=88; $COOL=76; $paused=$false; $hotLoad=0
function Temp { try{ $t=Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop; ($t | % { $_.CurrentTemperature/10-273.15 } | Measure -Max).Maximum }catch{ $null } }
"START safe thermal guard $(Get-Date)" | Out-File $log -Append -Encoding utf8
while(-not (Test-Path $stop)){
  $mt=@(Get-Process terminal -ErrorAction SilentlyContinue)
  foreach($p in $mt){ try{ if($p.PriorityClass -ne 'BelowNormal'){ $p.PriorityClass='BelowNormal' } }catch{} }
  $t=Temp; $load=(Get-CimInstance Win32_Processor | Measure LoadPercentage -Average).Average
  if($t -eq $null){ if($load -ge 95){$hotLoad++}else{$hotLoad=0}; $hot=($hotLoad -ge 20); $cool=$true }
  else { $hot=($t -ge $HOT); $cool=($t -le $COOL) }
  if($hot -and -not $paused -and $mt.Count){ foreach($p in $mt){ [N.S]::NtSuspendProcess($p.Handle)|Out-Null }; $paused=$true; $hotLoad=0; "$(Get-Date) PAUSED MT4 temp=$t load=$load" | Out-File $log -Append -Encoding utf8; if($t -eq $null){ Start-Sleep 60; $cool=$true } }
  if($paused -and ($cool -or -not $mt.Count)){ foreach($p in $mt){ [N.S]::NtResumeProcess($p.Handle)|Out-Null }; $paused=$false; "$(Get-Date) RESUMED MT4 temp=$t load=$load" | Out-File $log -Append -Encoding utf8 }
  Start-Sleep 15
}
foreach($p in Get-Process terminal -ErrorAction SilentlyContinue){ [N.S]::NtResumeProcess($p.Handle)|Out-Null }
"STOP $(Get-Date)" | Out-File $log -Append -Encoding utf8
