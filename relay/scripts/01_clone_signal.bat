@echo off
:: 01_clone_signal.bat - Clone Signal repo and checkout relay branch
:: Idempotent: skips clone if repo already exists, just pulls latest.

set REPO=C:\Users\endos\Desktop\hst_work\Signal
set PARENT=C:\Users\endos\Desktop\hst_work

if not exist "%PARENT%" mkdir "%PARENT%"

if exist "%REPO%\.git" (
    echo [INFO] Repo exists. Fetching latest relay branch...
    git -C "%REPO%" fetch origin relay
    git -C "%REPO%" checkout relay
    git -C "%REPO%" pull origin relay --rebase
) else (
    echo [INFO] Cloning Signal repo...
    git clone https://github.com/EndoScorpion/Signal.git "%REPO%"
    if %ERRORLEVEL% neq 0 ( echo [ERROR] git clone failed. Check network + GitHub auth. & exit /b 1 )
    git -C "%REPO%" fetch origin relay
    git -C "%REPO%" checkout relay
)

echo [OK] Signal at %REPO% on relay branch.
exit /b 0
