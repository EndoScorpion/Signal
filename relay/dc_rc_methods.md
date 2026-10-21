# DC & RC Connection Methods — 2026-10-21

Reference for restoring laptop↔cloud connectivity. Private relay branch.

## Method 1: DC Remote (easiest, recommended)

One command in any terminal on the laptop — keep the window open:

```
npx @wonderwhy-er/desktop-commander@latest remote
```

- Device ID (LenovoLaptop): `24123e3e-6795-430b-abf6-32e186477523`
- Connector UUID on claude.ai: `daef668b`
- Reconnect at: claude.ai Settings → Connectors

## Method 2: RC Session via Claude Project Thread

Start from any project thread:
- Use `start_remote_control` with `environment_id: env_01NgJTR6zYm3KYGtfCvGCPGF`
- Works even when DC Remote is offline — uses Claude desktop app
- Best for interactive sessions and one-off tasks

## Method 3: Git Relay (slowest, always available)

Write commands to `relay/to_cli.json` on this branch (Signal relay):
- LocalThug (laptop poller) picks up and executes
- Results appear in `relay/cmd_results.json`
- Poller script: `cmd_poller.ps1` (NSSM service or Task Scheduler)
- Works as long as laptop is on and polling

## Method 4: DC Clone (scheduled auto-start)

```powershell
Start-ScheduledTask DcCloneServer
```

Auto-starts at login. Check watchdog:

```powershell
Get-ScheduledTask Cloud_DC_Watchdog
```

## Full Repair Sequence

```powershell
# Kill stale node
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Restart DC Clone
Start-ScheduledTask DcCloneServer

# Restart DC Remote (keep window open)
npx @wonderwhy-er/desktop-commander@latest remote
```

## Watchdog

`Cloud_DC_Watchdog` scheduled task auto-restarts DC Clone + DC Remote at login and every 15 min.

## Priority Order

1. RC Session (most capable, interactive)
2. DC Remote (fast, persistent)
3. Git Relay (always available, async)
