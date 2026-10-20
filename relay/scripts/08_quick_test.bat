@echo off
:: 08_quick_test.bat - Enqueue Get-Date command to test the relay end-to-end
:: Run this after the service is installed. Should get a result back in ~10-30s.

set REPO=C:\Users\endos\Desktop\hst_work\Signal

where python >nul 2>&1
if %ERRORLEVEL% neq 0 ( where python3 >nul 2>&1 && set PY=python3 || echo [ERROR] Python not found & pause & exit /b 1 ) else ( set PY=python )

echo [INFO] Enqueuing Get-Date test command...
%PY% "%REPO%\relay\enqueue_cmd.py" "Get-Date"
pause
