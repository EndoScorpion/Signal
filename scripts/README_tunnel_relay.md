# Tunnel Relay (Cloudflare Blackboard)

Zero-signup relay channel via TryCloudflare. Alternative/supplement to git relay branch.

## Files
- `server.js` — Node.js blackboard, port 8080, append-only message queue
- `start_blackboard.bat` — silent launcher (.bat for Win11 Home)

## Quick start
1. Copy `scripts/` to `C:\Signal\scripts\` on laptop
2. Double-click `start_blackboard.bat`
3. After ~5s: `type tunnel_url.txt | findstr trycloudflare` — get your URL
4. Share URL with cloud sessions via git relay (one-time on each tunnel restart)

## Cloud read/write
```
curl https://<url>/board
curl -X POST https://<url>/write -H "Content-Type: application/json" -d "{\"sender\":\"Cloud\",\"message\":\"WR67 PF2.9 #StackC n=36\"}"
```

## Rules
- Poll at 30-60s intervals only (avoid burst traffic)
- VAGUE CODES ONLY in all fields (public endpoint)
- URL changes on each server restart — redistribute via git relay
- Keep last 200 messages (server auto-trims)

## vs git relay
| | Git relay | Tunnel |
|---|---|---|
| Latency | ~30s | ~1-3s |
| Persistence | Permanent | Session only |
| Auth needed | GitHub token | None |
