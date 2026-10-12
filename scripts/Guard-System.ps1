# RAM guard + CPU anti-overheat guard. Never kills MT4/metatester.
# RAM guard : free RAM < $RamLowMB  -> close chrome + PhoneExperienceHost (what you did by hand); logs it.
# CPU guard : temp >= $TempHi C (needs admin) OR load >= $LoadHi % for $SustainSec s -> MT4 priority BelowNormal
#             and a short throttle; returns to Normal once temp <= $TempLo / load < $LoadLo.
# Stop: New-Item mt4_guard.stop -ItemType File (in this folder).
$RamLowMB = 500; $TempHi = 88; $TempLo = 80; $LoadHi = 97; $LoadLo = 85; $SustainSec = 30
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class G {
  [StructLayout(LayoutKind.Sequential)] public struct LII { public uint cb; public uint t; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LII p);
  public static double IdleSec() { LII i = new LII(); i.cb = (uint)Marshal.SizeOf(i); GetLastInputInfo(ref i); return (Environment.TickCount - (int)i.t) / 1000.0; }
}
'@
$dir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$stop = Join-Path $dir 'mt4_guard.stop'
$log  = Join-Path $dir 'mt4_guard.log'
Remove-Item -LiteralPath $stop -ErrorAction SilentlyContinue
function Log($m) { Add-Content -LiteralPath $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function Get-Temp {
  try { $t = Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop |
        ForEach-Object { $_.CurrentTemperature / 10 - 273.15 } | Measure-Object -Maximum
        return [math]::Round($t.Maximum, 1) } catch { return $null }
}
function Set-Prio($pri) {
  foreach ($n in 'terminal','metatester','metatester64') {
    Get-Process -Name $n -ErrorAction SilentlyContinue | ForEach-Object { try { $_.PriorityClass = $pri } catch {} }
  }
}
$hot = $false; $hiCount = 0
Log 'guard started'
while (-not (Test-Path -LiteralPath $stop)) {
  $freeMB = [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024)
  if ($freeMB -lt $RamLowMB) {
    $k = Get-Process -Name chrome,PhoneExperienceHost -ErrorAction SilentlyContinue
    if ($k -and [G]::IdleSec() -ge 10) { $k | Stop-Process -Force -ErrorAction SilentlyContinue; Log "RAM low ($freeMB MB): closed chrome/PhoneExperienceHost" }
  }
  $load = (Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average
  $temp = Get-Temp
  if ($load -ge $LoadHi) { $hiCount++ } else { $hiCount = 0 }
  $tooHot = ($temp -ne $null -and $temp -ge $TempHi) -or ($hiCount * 5 -ge $SustainSec)
  $cool   = ($temp -eq $null -or $temp -le $TempLo) -and $load -lt $LoadLo
  if (-not $hot -and $tooHot) { $hot = $true; Set-Prio 'BelowNormal'; Log "CPU hot (temp=$temp load=$load): MT4 -> BelowNormal" }
  elseif ($hot -and $cool)    { $hot = $false; $hiCount = 0; Set-Prio 'Normal'; Log "CPU cooled (temp=$temp load=$load): MT4 -> Normal" }
  elseif ($hot)               { Start-Sleep -Milliseconds 1500 }  # extra breathing room while hot
  Start-Sleep -Seconds 5
}
Log 'guard stopped'
