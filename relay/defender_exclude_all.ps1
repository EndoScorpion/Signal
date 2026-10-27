# Defender exclusions for Signal/LocalThug stack
Add-MpPreference -ExclusionProcess 'node.exe'
Add-MpPreference -ExclusionProcess 'claude.exe'
Add-MpPreference -ExclusionProcess 'powershell.exe'
Add-MpPreference -ExclusionProcess 'wscript.exe'
Add-MpPreference -ExclusionPath 'C:\Users\endos\Signal'
Add-MpPreference -ExclusionPath "$env:APPDATA\npm"
Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\npx"
Add-MpPreference -ExclusionPath 'C:\Users\endos\Desktop'
Write-Host 'Defender exclusions applied.'
Read-Host 'Press Enter to close'
