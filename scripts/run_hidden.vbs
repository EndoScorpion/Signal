' run_hidden.vbs — VBS silent launcher, runs any command with WindowStyle 0 (no visible window)
' Usage: wscript.exe run_hidden.vbs "powershell.exe -WindowStyle Hidden ..."
Dim objShell, strCmd
strCmd = WScript.Arguments(0)
Set objShell = CreateObject("WScript.Shell")
objShell.Run strCmd, 0, False
Set objShell = Nothing
