' start_poller_hidden.vbs — starts CloudCmdPollerGH.ps1 with no visible window
' Double-click this file (or put it in shell:startup) to launch the poller silently.
Dim shell, cmd
Set shell = CreateObject("WScript.Shell")
cmd = "powershell.exe -NonInteractive -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File ""C:\Users\endos\Signal\scripts\CloudCmdPollerGH.ps1"""
shell.Run cmd, 0, False
