# black_overlay.ps1 - flat black full-screen overlay on every monitor; closes when the mouse moves (>10 px),
# a key is pressed, or after -Minutes (default 120). Tests keep running underneath.
#   powershell -ExecutionPolicy Bypass -File C:\Users\endos\Desktop\hst_out\black_overlay.ps1 [-Minutes 120]
param([int]$Minutes=120)
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$start=[System.Windows.Forms.Cursor]::Position; $forms=@()
foreach($scr in [System.Windows.Forms.Screen]::AllScreens){
  $f=New-Object System.Windows.Forms.Form
  $f.FormBorderStyle='None'; $f.BackColor=[System.Drawing.Color]::Black; $f.TopMost=$true; $f.ShowInTaskbar=$false
  $f.StartPosition='Manual'; $f.Bounds=$scr.Bounds; $f.Cursor=[System.Windows.Forms.Cursors]::Default
  $f.Add_KeyDown({ [System.Windows.Forms.Application]::Exit() })
  $forms+=$f; $f.Show() }
$t0=Get-Date; $timer=New-Object System.Windows.Forms.Timer; $timer.Interval=250
$timer.Add_Tick({ $p=[System.Windows.Forms.Cursor]::Position
  if([math]::Abs($p.X-$start.X) -gt 10 -or [math]::Abs($p.Y-$start.Y) -gt 10 -or ((Get-Date)-$t0).TotalMinutes -ge $Minutes){ [System.Windows.Forms.Application]::Exit() }
  foreach($f in $forms){ if(-not $f.TopMost){ $f.TopMost=$true } } })
$timer.Start(); [System.Windows.Forms.Application]::Run()
foreach($f in $forms){ $f.Close() }
