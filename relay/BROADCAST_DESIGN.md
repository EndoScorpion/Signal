# Multi-Channel Broadcast Design

## Channels (fire all simultaneously on important event)
| # | Channel | Status | Notes |
|---|---------|--------|-------|
| 1 | Git relay (`relay/to_cli.json`) | LIVE | ~5s latency |
| 2 | Gmail (endoscorpion@gmail.com) | LIVE (Gmail MCP) | Claude session sends |
| 3 | signal-board (`board.json`) | LIVE | vague codes only |
| 4 | Hastebin (public fallback) | LIVE | no secret in body |
| 5 | Claude project chat | Manual / coordinator | coordinator posts |
| 6 | Phone GOON | Via Nasif relay | reads git/Gmail |

## Message Schema
```json
{
  "ts": "2026-10-21T23:39:00Z",
  "sig": "<HMAC-SHA256 hex>",
  "type": "RESULT|SIGNAL|URGENT|INFO",
  "body": "<vague text — codes only: WR%, PF, #StackC, WP/t, etc.>"
}
```

## Auth Scheme
- `sig = HMAC-SHA256(ts + "|" + type + "|" + body, SLC_RELAY_SECRET)`
- `SLC_RELAY_SECRET` stored in **private memory only** — never committed
- Listener re-computes sig and calls `hmac.compare_digest()` to verify
- Rotation: change quarterly or on suspected leak; update memory + tell all listeners

## Usage
```bash
export SLC_RELAY_SECRET="<from private memory>"
python3 broadcast_all.py --type RESULT --body "WR 75% PF 5.2 n=36 #StackC"
python3 broadcast_all.py --test   # dry-run all channels
```

## Security rules
- Public channels (signal-board, hastebin): vague body only, **no sig**
- Private channels (Git relay, Gmail): full JSON with sig
- **Never log or commit `SLC_RELAY_SECRET`**
- Gmail stub: Claude session must invoke Gmail MCP `send_message` directly
