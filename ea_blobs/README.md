# ea_blobs

AES-256 encrypted EA and set file backups. Safe to push — plaintext never stored here.

## Convention
- `<label>.ea.enc`  — encrypted EA source
- `<label>.set.enc` — encrypted set file
- `<label>.log.enc` — encrypted backtest report

## Labels (map in private_map.enc)
- alpha   = current best
- bravo   = gen0 range
- charlie = gen0 zgate
- zero    = base

## Decrypt
Requires: C:\Users\endos\.mapkey (local only, never in this repo)

## Rules
- NEVER commit raw .mq4 / .set / .html
- Only .enc files belong here
- .gitignore enforces this at repo level
