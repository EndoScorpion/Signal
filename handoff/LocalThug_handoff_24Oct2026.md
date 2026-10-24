# LocalThug Handoff — 2026-10-24

## Active State
- MT4 test running: b31_tp50_base (run_tester.ps1, background)
- RAM watch: ClaudeRAMWatch scheduled task, every 5 min, hidden, board.json only
- TightVNC: running as SYSTEM on port 5900
- Tailscale IP: 100.113.25.60 (VNC via 100.113.25.60:5900)
- Tor onion: 4tg7ciliburib3mm6amxpacxt4uohqr56dybdsklae65ze6ijr3x2aqd.onion:5900
- Telegram bot: @EndoScorpionBot token saved, chat ID pending (send "hi" to bot)

## Queued Work
- Theory 58: Hard Flip reversal (logged in TEST_LOG.txt + board.json)
- T59-T62: sell stop flip, hedge+decide, double lot flip, straddle (after T58)
- History CSV metadata labeling (.meta.json sidecar files)
- Signal Desktop alert hooks (once installed + linked)
- Telegram alert hooks (once chat ID retrieved)
- Dark Reader config import: C:\Users\endos\claude_notes\dark_reader_config.json

## Key Files
- board.json: C:\Users\endos\board.json
- RAM watch: C:\Users\endos\Desktop\hst_out\ram_watch.ps1
- Dark Reader config: C:\Users\endos\claude_notes\dark_reader_config.json
- Test log: C:\Users\endos\Desktop\hst_out\winners\TEST_LOG.txt
- Settings: C:\Users\endos\.claude\settings.json (SessionStart hook added)

## DST Note
EA uses UTC internally — no DST action needed Sunday Oct 26.

## Remote Access
- Tailscale: 100.113.25.60:5900 (primary)
- Tor onion: see above (requires Tor Browser running)
- DC web link: active
