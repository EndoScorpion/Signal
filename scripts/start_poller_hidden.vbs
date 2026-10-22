' start_poller_hidden.vbs — kill existing poller and restart fully hidden
Dim objShell, objWMI, objProcessSet, objProcess
Set objShell = CreateObject("WScript.Shell")
Set objWMI = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")

' Kill existing CloudCmdPollerGH processes
Set objProcessSet = objWMI.ExecQuery("SELECT * FROM Win32_Process WHERE Name='powershell.exe'")
For Each objProcess In objProcessSet
    If InStr(LCase(objProcess.CommandLine), "cloudcmdpollergh") > 0 Then
        objProcess.Terminate
    End If
Next

' Wait 1 second
WScript.Sleep 1000

' Restart poller hidden
objShell.Run "powershell.exe -WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File ""C:\Users\endos\Signal\scripts\CloudCmdPollerGH.ps1""", 0, False
Set objShell = Nothing
