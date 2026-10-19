@echo off
:: 00_INSTALL_ALL.bat - One-click master installer for the GitHub relay system
:: Run as Administrator. Idempotent - safe to run multiple times.
::
:: Does in order:
::   1. Clone Signal repo + checkout relay branch
::   2. Download NSSM if missing
::   3. Install CloudCmdPollerGH as a Windows service
::   4. Patch Claude Code settings.json (allow relay tools)
::   5. Create shortcuts on Desktop

setlocal
set REPO=C:\Users\endos\Desktop\hst_work\Signal
set LOGDIR=C:\Users\endos\Desktop\hst_out
set SCRIPTS=%REPO%\relay\scripts

echo ============================================
echo  Signal GitHub Relay - Master Installer
echo ============================================
echo.

:: Step 1: Clone / update Signal
call "%~dp000_INSTALL_ALL.bat" >nul 2>&1
call "%~dp001_clone_signal.bat"
if %ERRORLEVEL% neq 0 ( echo [FAIL] Clone step failed. & goto :end )

:: Step 2 + 3: NSSM service
call "%SCRIPTS%\02_install_nssm_service.bat"
if %ERRORLEVEL% neq 0 ( echo [WARN] Service install had issues - check output above. )

:: Step 4: Patch Claude settings
powershell -NonInteractive -ExecutionPolicy Bypass -File "%SCRIPTS%\03_patch_claude_settings.ps1"

:: Step 5: Desktop shortcuts
call "%SCRIPTS%\06_create_shortcuts.bat"

echo.
echo ============================================
echo  Done. Poller service should be running.
echo  Log: %LOGDIR%\cmd_poller_svc.log
echo  Test: python relay\enqueue_cmd.py "Get-Date"
echo ============================================
:end
pause
