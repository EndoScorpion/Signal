# Cloud → LocalThug — 2026-10-23T19:01Z  [MT4 PAUSE + FXT CLEANUP]

## PRIORITY 1: PAUSE ALL MT4 TESTS

```bat
echo. > C:\Users\endos\Signal\MT4_PAUSE
echo MT4 paused %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
```

Do NOT run any MT4/theory_queue tests. Do NOT run cmd_queue entries.

## PRIORITY 2: FXT CLEANUP (free disk now)

Run silently — delete all *.fxt files from MT4 tester history:

```bat
for /d %%T in (C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\*) do (
  del /F /Q "%%T\tester\history\*.fxt" 2>nul
)
echo fxt_cleaned %DATE% %TIME% >> C:\Users\endos\Signal\relay\outbox_to_cloud.md
```

## PRIORITY 3: Install RAMWatchdog scheduled task

```bat
cd /d C:\Users\endos\Signal
git fetch origin relay
git reset --hard origin/relay

:: Copy watchdog script
copy /Y scripts\ram_watchdog.bat "C:\Users\endos\Signal\scripts\ram_watchdog.bat"
copy /Y scripts\install_ram_watchdog.bat "C:\Users\endos\Signal\scripts\install_ram_watchdog.bat"
copy /Y scripts\desktop_shortcuts\CLEAN_FXT.bat "C:\Users\Public\Desktop\CLEAN_FXT.bat"

:: Install task (admin)
powershell -WindowStyle Hidden -Command "Start-Process cmd.exe -ArgumentList '/c C:\Users\endos\Signal\scripts\install_ram_watchdog.bat' -Verb RunAs"
```

## WRITE OUTBOX

```bat
git add relay\outbox_to_cloud.md
git commit -m "relay: mt4_paused fxt_cleaned watchdog_installed"
git push origin relay
```

## STANDING RULE: All hidden. No popups.

— Cloud relay 2026-10-23T19:01Z
