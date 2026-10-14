Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$dir = 'C:\Users\endos\Desktop\hst_out'
$tags = @('WIN_GEN1_2015_sp8_full','WIN_GEN1_2018_sp8_full','WIN_GEN1_2023_sp8_full','WIN_GEN1_2024_sp8_full')
$avgMin = 3.5
$form = New-Object Windows.Forms.Form
$form.Text = 'Test tracker'; $form.TopMost = $true; $form.Width = 360; $form.Height = 230
$form.StartPosition = 'Manual'; $form.Location = New-Object Drawing.Point(20, 20)
$form.FormBorderStyle = 'FixedToolWindow'; $form.BackColor = [Drawing.Color]::FromArgb(30,30,30)
$lbl = New-Object Windows.Forms.Label
$lbl.ForeColor = [Drawing.Color]::White; $lbl.Font = New-Object Drawing.Font('Consolas', 10)
$lbl.Left = 10; $lbl.Top = 40; $lbl.Width = 330; $lbl.Height = 150
$bar = New-Object Windows.Forms.ProgressBar
$bar.Left = 10; $bar.Top = 10; $bar.Width = 330; $bar.Height = 22; $bar.Maximum = 100
$form.Controls.AddRange(@($bar, $lbl))
$start = Get-Date
function Update-View {
    $done = 0; $lines = @()
    foreach ($t in $tags) {
        $p = Join-Path $dir "$t.htm"
        if (Test-Path $p) { $done++; $lines += "[x] $t" } else { $lines += "[ ] $t" }
    }
    $running = [bool](Get-Process terminal -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*mt4_tester\*' })
    $remain = [math]::Max(0, ($tags.Count - $done) * $avgMin)
    $free = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB)
    $bar.Value = [int](100 * $done / $tags.Count)
    $state = if ($done -eq $tags.Count) { 'ALL DONE' } elseif ($running) { 'running' } else { 'idle' }
    $lbl.Text = ($lines -join "`n") + "`n`n$done of $($tags.Count) done - $state`nETA about $remain min`nFree RAM $free MB`nUpdated $(Get-Date -Format HH:mm:ss)"
}
$timer = New-Object Windows.Forms.Timer
$timer.Interval = 15000
$timer.Add_Tick({ Update-View })
Update-View
$timer.Start()
[void]$form.ShowDialog()
