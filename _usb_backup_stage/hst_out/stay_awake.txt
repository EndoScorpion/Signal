Add-Type -Name P -Namespace W -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
while($true){ [W.P]::SetThreadExecutionState(0x80000003) | Out-Null; Start-Sleep 50 }
