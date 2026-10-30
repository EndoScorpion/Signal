@echo off
echo === FULL PC FIX SCRIPT ===
echo.

echo [1/5] Disabling RAM-heavy startup tasks...
schtasks /Change /TN "Cloud_DC_Watchdog" /Disable 2>nul
schtasks /Change /TN "ClaudePWAStartup" /Disable 2>nul
schtasks /Change /TN "DCRemoteService" /Disable 2>nul
schtasks /Change /TN "RelayAutoSync" /Disable 2>nul
echo Done.

echo [2/5] Reinstalling Bun...
powershell -ExecutionPolicy Bypass -Command "irm bun.sh/install.ps1 | iex"
echo Done.

echo [3/5] Reinstalling Claude CLI...
npm install -g @anthropic-ai/claude-code
echo Done.

echo [4/5] Setting up auto-RC on login...
echo Set WshShell = CreateObject("WScript.Shell") > "%USERPROFILE%\claude_rc_launcher.vbs"
echo WshShell.Run "cmd /c claude remote-control", 0, False >> "%USERPROFILE%\claude_rc_launcher.vbs"
schtasks /Create /TN "ClaudeAutoRC" /TR "wscript.exe \"%USERPROFILE%\claude_rc_launcher.vbs\"" /SC ONLOGON /RL HIGHEST /F 2>nul
echo Done.

echo [5/5] Starting RC now...
wscript.exe "%USERPROFILE%\claude_rc_launcher.vbs"
echo RC started in background. Claude can now connect.
pause
