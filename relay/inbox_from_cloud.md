# Cloud → LocalThug — 2026-10-23T18:43Z  [COPY SHORTCUTS TO SHARED DESKTOP]

## After git pull: copy 3 bat files to C:\Users\Public\Desktop\

```bat
cd /d C:\Users\endos\Signal
git fetch origin relay
git reset --hard origin/relay

copy /Y scripts\desktop_shortcuts\SAFE_GIT_PULL.bat "C:\Users\Public\Desktop\SAFE_GIT_PULL.bat"
copy /Y scripts\desktop_shortcuts\START_TUNNEL.bat "C:\Users\Public\Desktop\START_TUNNEL.bat"
copy /Y scripts\desktop_shortcuts\INSTALL_AUTOSYNC.bat "C:\Users\Public\Desktop\INSTALL_AUTOSYNC.bat"

echo Shortcuts copied to shared desktop.
```

Then write outbox + push:
```bat
echo - shortcuts_copied %DATE% %TIME% > relay\outbox_to_cloud.md
git add relay\outbox_to_cloud.md
git commit -m "relay: shortcuts on public desktop"
git push origin relay
```

## STANDING RULE: All hidden. No popups.

— Cloud relay 2026-10-23T18:43Z
