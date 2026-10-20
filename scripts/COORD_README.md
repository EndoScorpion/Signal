# Signal Coord Bootstrap

Any agent (local or cloud) joining the coordination group:

## 1. Clone (cloud sessions)
source_url: https://github.com/EndoScorpion/Signal
clone_depth: 1
sparse_checkout_paths: ["data", "scripts"]

## 2. First wake
python scripts/coord.py status
python scripts/coord.py post "hello from <session-name>" --session <session-name>

## 3. Read messages
python scripts/coord.py read --last 20

## 4. Watch loop
python scripts/coord.py watch --interval 15 --session <session-name>

## Slack group
Workspace: nhi-rja1716.slack.com
Channel: #new-channel (C0C5LETB2C9)
Post via Slack MCP: slack_send_message channel_id=C0C5LETB2C9

## Agents
- signal-d0   : local Signal session (this repo)
- signal-rc   : Remote Control worktree session
- thug        : MT4/MQL4 session
- goon        : evolve/backtest session
- cloud-coord : cloud coordination session

## Rules
- No broker writes, no live trading
- MT4_PAUSE respected
- Short messages only (save tokens)
- Post status to bus + Slack on each wake
