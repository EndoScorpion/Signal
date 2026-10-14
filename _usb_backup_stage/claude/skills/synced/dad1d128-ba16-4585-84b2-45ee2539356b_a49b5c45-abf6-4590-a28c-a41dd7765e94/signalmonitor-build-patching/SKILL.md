---
name: "signalmonitor-build-patching"
description: "Use when editing or building a new version of the user's SignalMonitor / MarketWatch single-file HTML trading app (SANDBOX_v0.01x_signal_container*.html)."
---

# SignalMonitor build patching

The app is one ~6.7 MB HTML file with a few multi-MB lines (embedded data). Never Read it whole.

## Workflow (token-cheap)
1. Get the file from the open artifact (Artifact read saves the full HTML to disk) or the user's upload. Work on a copy.
2. Locate code with `grep -n -o -E '.{0,60}NAME.{0,120}' file | cut -c1-260` (the -o and cut keep output small). Check `awk '{print length}'` first to find huge lines.
3. Key entry points: button `_v40RunAll()` -> `runAll()` (8 steps: stage 2, stage 3, learning, live seeds, new branches v40, metals, autopilot, pending/forward tests); `_v40Ph('csv'|'txt')` price history download; `V40G.dl(fmt)` grab history; `_v40Log()` winning-logic log; `saveFile()` is wrapped to add the build/name prefix taken from `document.title` (`v0.01x`); `_v40Bump()` makes the next build letter; `_ingest(sym,data,src,force)` loads bars; estimates come from localStorage `v40_dur_*` in the 'v40i' block.
4. Patch with a Python read-replace that asserts `s.count(old)==1`. Prefer appending a new `<style>`/`<script>` block before the LAST `</body>` over editing minified lines.
5. Verify: extract the changed `<script>` blocks and run `node --check`; then smoke-test in headless Chromium (Playwright, `executablePath:'/opt/pw-browsers/chromium'`, NODE_PATH from `npm root -g`) and check `pageerror` is empty.
6. Save a .txt backup of any code you added, and deliver the HTML with SendUserFile (display render for a full artifact preview).

## Conventions
- Bump the build: title `vX.YYz DD Mon YYYYz`, `#v40Cp` copyright text.
- Build tag goes in: title, top banner, bottom `#mbd` bar, log first line, exported .txt header, index tree.
- Chrome freezes on long single-thread runs: split into halves/steps with `await nap()` pauses, keep DevTools closed while running.
- Opened from file://, Binance fetches fail with CORS: import the downloaded history CSV through `#dgFile` instead.