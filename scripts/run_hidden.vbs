' run_hidden.vbs — generic hidden launcher
' Usage: WScript run_hidden.vbs "C:\path\to\script.ps1" [optional args...]
' Runs PowerShell with -WindowStyle Hidden so NO terminal window appears.
Dim args, cmd, i
Set args = WScript.Arguments
If args.Count = 0 Then
    WScript.Echo "Usage: run_hidden.vbs <script.ps1> [args...]"
    WScript.Quit 1
End If
cmd = "powershell.exe -NonInteractive -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & args(0) & """"
For i = 1 To args.Count - 1
    cmd = cmd & " " & args(i)
Next
Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run cmd, 0, False
