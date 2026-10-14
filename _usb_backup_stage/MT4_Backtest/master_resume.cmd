@echo off
rem Reopens the "master" clone-hub Claude Code CLI session (cwd C:\Users\endos).
rem If the window's claude exits or crashes, it offers to relaunch instead of closing.
title MASTER clone hub - Claude CLI (do not close)
color 0A
cd /d C:\Users\endos
:loop
"C:\Users\endos\.local\bin\claude.exe" --resume f7efebdd-8d88-4823-86eb-cefeb3cd5d0c
echo.
echo Master session exited. Press any key to relaunch it, or close this window to stop.
pause >nul
goto loop
