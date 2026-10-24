@echo off
REM Stop all relay processes silently
taskkill /f /im cloudflared.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo Relay stopped.
