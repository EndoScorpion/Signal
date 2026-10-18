@echo off
:: 06_create_shortcuts.bat - Create Desktop shortcuts for relay scripts
:: Uses PowerShell WScript.Shell to create proper .lnk shortcuts.

set REPO=C:\Users\endos\Desktop\hst_work\Signal
set DESKTOP=C:\Users\endos\Desktop
set SCRIPTS=%REPO%\relay\scripts

powershell -NonInteractive -ExecutionPolicy Bypass -Command "& {
    $ws = New-Object -ComObject WScript.Shell

    function Make-Shortcut($name, $target, $args, $icon) {
        $s = $ws.CreateShortcut(\"$env:USERPROFILE\\Desktop\\$name.lnk\")
        $s.TargetPath = $target
        if ($args) { $s.Arguments = $args }
        if ($icon) { $s.IconLocation = $icon }
        $s.Save()
        Write-Host \"[OK] Shortcut: $name\"
    }

    Make-Shortcut 'Poller - Install Service' 'cmd.exe' \"/k \\\"%SCRIPTS%\\02_install_nssm_service.bat\\\"\" 'shell32.dll,21'
    Make-Shortcut 'Poller - Status' 'powershell.exe' \"-NoExit -Command sc query CloudCmdPollerGH; Get-Content C:\\Users\\endos\\Desktop\\hst_out\\cmd_poller_svc.log -Tail 20 -ErrorAction SilentlyContinue\" 'shell32.dll,23'
    Make-Shortcut 'Launch MT4' 'cmd.exe' \"/c \\\"%SCRIPTS%\\04_mt4_launcher.bat\\\"\" 'shell32.dll,13'
    Make-Shortcut 'Launch DC Remote' 'cmd.exe' \"/k \\\"%SCRIPTS%\\05_dc_remote_launcher.bat\\\"\" 'shell32.dll,44'
    Make-Shortcut 'Signal - Pull Relay' 'powershell.exe' \"-NoExit -Command git -C $env:USERPROFILE\\Desktop\\hst_work\\Signal pull origin relay --rebase\" 'shell32.dll,45'
}"

echo [OK] Shortcuts created on Desktop.
