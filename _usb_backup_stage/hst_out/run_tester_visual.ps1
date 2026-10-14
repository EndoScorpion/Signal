# run_tester_visual.ps1 - variant of run_tester.ps1 that opens the report with its balance graph for 5 s at the end - unattended MT4 Strategy Tester run (portable copy, never touches the live terminal)
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

# 4. launch portable instance and wait for it to shut itself down
$t0 = Get-Date
$proc = Start-Process -FilePath "$P\terminal.exe" -ArgumentList "`"$cfg`"", "/portable" -WindowStyle Minimized -PassThru   # MT4: ini path as plain first arg, NOT /config:
Add-Type 'using System;using System.Runtime.InteropServices;public class MinW{[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int c);[DllImport("user32.dll")]public static extern bool IsIconic(IntPtr h);}' -EA 0
$deadline=(Get-Date).AddMinutes($TimeoutMin); while(-not $proc.HasExited -and (Get-Date) -lt $deadline){ Get-Process terminal -EA 0 | ? { $_.Path -like "$P\*" -and $_.MainWindowHandle -ne 0 } | % { if(-not [MinW]::IsIconic($_.MainWindowHandle)){ [MinW]::ShowWindow($_.MainWindowHandle,7) | Out-Null } }; Start-Sleep -Milliseconds 500 }
if (-not $proc.WaitForExit($TimeoutMin * 60000)) { Stop-Process -Id $proc.Id -Force; Write-Output "TIMEOUT after $TimeoutMin min"; exit 3 }

# 5. collect report
$htm = Get-ChildItem "$P\reports" -Filter "$Tag*.htm" -EA 0 | ? { $_.LastWriteTime -ge $t0 }
if (-not $htm) { Write-Output "NO REPORT - check $P\tester\logs"; exit 4 }
Copy-Item "$P\reports\$Tag*" $Out -Force
$min = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
try { $dv="$env:TEMP\mt4_report_dark"; New-Item -ItemType Directory -Force $dv | Out-Null; Copy-Item "$Out\$Tag.gif" $dv -Force -EA 0
  $hd=[IO.File]::ReadAllText("$Out\$Tag.htm"); $css='<style>body,table,td,th{background:#000 !important;color:#33ff66 !important}a{color:#7fc8ff !important}img{float:right;margin:0 0 8px 12px;max-width:55%}</style>'
  if($hd -match '(?i)<head>'){ $hd=$hd -replace '(?i)<head>',('<head>'+$css) } else { $hd=$css+$hd }; $bal=@(); foreach($m in [regex]::Matches($hd,'(?is)<tr[^>]*>(.*?)</tr>')){ $cc=@([regex]::Matches($m.Groups[1].Value,'(?is)<td[^>]*>(.*?)</td>')|%{($_.Groups[1].Value -replace '<[^>]+>','').Trim()}); if($cc.Count -ge 10 -and $cc[0] -match '^\d+$' -and $cc[9] -match '^[\d\.]+$'){ $bal+=[double]$cc[9] } }
  if($bal.Count -gt 1){ $mn=($bal|Measure -Min).Minimum; $mx=($bal|Measure -Max).Maximum; if($mx -eq $mn){$mx=$mn+1}; $pts=for($k=0;$k -lt $bal.Count;$k++){ '{0:F1},{1:F1}' -f (10+620*$k/($bal.Count-1)),(370-340*($bal[$k]-$mn)/($mx-$mn)) }
    $g="<div style='position:fixed;right:10px;top:10px;width:660px;border:1px solid #33ff66'><svg width='640' height='390' style='background:#000'><polyline fill='none' stroke='#33ff66' stroke-width='1.5' points='$($pts -join ' ')'/><text x='10' y='20' fill='#7fc8ff' font-size='13'>$Tag balance  start $($bal[0])  end $($bal[-1])  min $mn  max $mx</text></svg></div>"
    $hd=$hd -replace '(?i)<img[^>]*>',''; $hd=$hd -replace '(?i)<body([^>]*)>',('<body$1>'+$g) }
  $hd=$hd -replace '(?i)<body([^>]*)>','<body$1><div style=''width:48%''>'
  [IO.File]::WriteAllText("$dv\$Tag.htm",$hd)
  $ps=60; try { $ps=[int](Get-Content "$Out\popup_seconds.txt" -TotalCount 1) } catch { $ps=60 }; if($ps -lt 0){ $ps=60 }; if($ps -eq 0){ throw "popup off" }; try { & C:\Users\endos\AppData\Local\Python\bin\python.exe -I "$Out\stat_corr\dark_report.py" $Tag | Out-Null; $hd=[IO.File]::ReadAllText("$Out\dark_reports\$Tag.htm") } catch {}
  $bar="<div style='position:fixed;left:10px;bottom:10px;background:#111;border:1px solid #33ff66;padding:6px;font:13px Arial'><span id='cd'></span> <button onclick='go(""set?s=30"",30)'>30 s</button> <button onclick='go(""set?s=60"",60)'>60 s</button> <button onclick='go(""set?s=120"",120)'>120 s</button> <button onclick='go(""keep"",-1)'>Keep open</button> <button onclick='go(""close"",0)'>Close now</button></div><script>var q=new URLSearchParams(location.search),P=q.get('port'),t=+q.get('s')||60;function go(p,s){fetch('http://localhost:'+P+'/'+p).catch(function(){});t=s;if(s==0)window.close();}setInterval(function(){if(t>0)t--;document.getElementById('cd').textContent=t<0?'kept open':'closes in '+t+' s';},1000);</script>"
  $hd=$hd -replace '(?i)</body>',($bar+'</body>'); [IO.File]::WriteAllText("$dv\$Tag.htm",$hd)
  $port=8790+(Get-Random -Maximum 200); Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$Out\popup_view.ps1",'-Page',"$dv\$Tag.htm",'-Tag',$Tag,'-Seconds',$ps,'-Port',$port } catch {}
Write-Output "OK $Tag in $min min -> $Out\$Tag.htm"




















