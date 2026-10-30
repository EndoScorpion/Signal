@echo off
echo ===== BOARD SYNC SETUP =====
echo Keeps C:\Signal\board.json synced from GitHub every 2 minutes

if not exist "C:\Signal" mkdir "C:\Signal"

echo [1/3] Doing initial fetch now...
powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/EndoScorpion/signal-board/main/board.json' -OutFile 'C:\Signal\board.json' -UseBasicParsing"
echo Done.

echo [2/3] Verifying...
powershell -ExecutionPolicy Bypass -Command "Get-Content 'C:\Signal\board.json' | ConvertFrom-Json | Select-Object -First 2 | Format-List ts,from,msg"

echo [3/3] Registering BoardSync scheduled task (every 2 min)...
schtasks /Delete /TN "BoardSync" /F 2>nul
schtasks /Create /TN "BoardSync" /TR "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/EndoScorpion/signal-board/main/board.json' -OutFile 'C:\Signal\board.json' -UseBasicParsing\"" /SC MINUTE /MO 2 /RL HIGHEST /F
echo Done. Board will auto-sync every 2 minutes to C:\Signal\board.json

echo ===== DONE =====
pause
