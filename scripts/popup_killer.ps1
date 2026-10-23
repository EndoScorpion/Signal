$wl=@("chrome","firefox","msedge","mt4terminal","windowsterminal","claude","notepad","explorer","taskmgr","code")
$sig='[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);'
Add-Type -MemberDefinition $sig -Name Win -Namespace WinAPI
$seen=@{}
while($true){Get-Process|?{$_.MainWindowTitle-ne""}&|%{$n=$_.Name.ToLower();$id=$_.Id;if(!$seen[$id]-and$wl-notcontains$n){[WinAPI.Win]::ShowWindow($_.MainWindowHandle,6)|Out-Null;$seen[$id]=$true;Add-Content "C:\Users\endos\Signal\logs\popup_killer.log" "$(Get-Date) MIN: $($_.Name) $id $($_.MainWindowTitle)"}}; Start-Sleep -ms 500}
