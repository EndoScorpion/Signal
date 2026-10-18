@echo off
:: 05_dc_remote_launcher.bat - Launch / ensure Desktop Commander remote server is running
:: Desktop Commander remote server allows cloud Claude to connect via MCP.

set DCPATHS=0
set NODEPATH=

:: Check if node is available
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)

:: Check if Desktop Commander is already running (port 3000 typical)
powershell -NonInteractive -Command "if (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo [OK] Desktop Commander appears to be running on port 3000.
    goto :done
)

:: Try common npx path
echo [INFO] Starting Desktop Commander via npx...
start "Desktop Commander" /min cmd /c "npx @anthropic-ai/desktop-commander serve 2>> C:\Users\endos\Desktop\hst_out\dc_server.log"

timeout /t 3 /nobreak >nul
powershell -NonInteractive -Command "if (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo [OK] Desktop Commander started.
) else (
    echo [WARN] DC may not have started yet. Check: hst_out\dc_server.log
)

:done
