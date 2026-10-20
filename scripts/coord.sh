#!/usr/bin/env bash
# Signal Coord — post to ntfy + Slack + chat_bus.json from CLI / THUG / any agent
# Usage:
#   ./coord.sh STATUS "DC online, RAM 62%"
#   ./coord.sh ALERT  "MT4 disconnected"
#   ./coord.sh DONE   "b62 backtest complete"
#   ./coord.sh ASK    "Nasif: approve PAUSE lift?"
#   ./coord.sh INFO   "any message"
#
# Env vars:
#   COORD_AGENT    agent name (default: hostname)
#   COORD_TOPIC    ntfy topic (default: signal-coord)
#   SLACK_WEBHOOK  Slack incoming webhook URL (optional, enables Slack posting)
#   COORD_BUS      path to chat_bus.json (default: auto-detect from script location)

TOPIC="${COORD_TOPIC:-signal-coord}"
AGENT="${COORD_AGENT:-$(hostname -s 2>/dev/null || echo CLI)}"
TYPE="${1:-INFO}"
MSG="${2:-}"

if [[ -z "$MSG" ]]; then
  echo "Usage: $0 <TYPE> <message>"
  echo "Types: STATUS ALERT DONE ASK INFO"
  exit 1
fi

TITLE="[${AGENT}] [${TYPE}] ${MSG:0:60}"
TS="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# 1. ntfy
curl -s \
  -H "Title: ${TITLE}" \
  -H "Content-Type: text/plain" \
  -d "${MSG}" \
  "https://ntfy.sh/${TOPIC}" \
  && echo "✓ ntfy #${TOPIC}" \
  || echo "✗ ntfy failed"

# 2. Slack webhook (if set)
if [[ -n "$SLACK_WEBHOOK" ]]; then
  SLACK_TEXT="*[${AGENT}]* \`${TYPE}\` ${MSG}"
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"${SLACK_TEXT}\"}" \
    "${SLACK_WEBHOOK}" \
    && echo "✓ Slack" \
    || echo "✗ Slack failed"
fi

# 3. chat_bus.json (project shared file)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUS="${COORD_BUS:-${SCRIPT_DIR}/../data/chat_bus.json}"
if [[ -f "$BUS" ]] || [[ -d "$(dirname "$BUS")" ]]; then
  python3 - <<PYEOF 2>/dev/null && echo "✓ chat_bus" || true
import json, pathlib
bus = pathlib.Path("${BUS}")
data = json.loads(bus.read_text()) if bus.exists() else {"messages": []}
data["messages"].append({"ts": "${TS}", "session": "${AGENT}", "type": "${TYPE}", "msg": "${MSG}"})
bus.write_text(json.dumps(data, indent=2))
PYEOF
fi
