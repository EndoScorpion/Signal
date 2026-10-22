' run_hidden.vbs — launch a PowerShell script with zero visible window. No pm2 needed.
' Usage: wscript.exe run_hidden.vbs "C:\path\to\script.ps1"
Dim wsh, script
Set wsh = CreateObject("WScript.Shell")
script = WScript.Arguments(0)
wsh.Run "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File """ & script & """", 0, False
Set wsh = Nothing
