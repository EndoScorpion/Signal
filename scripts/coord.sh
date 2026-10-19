#!/usr/bin/env bash
# Signal Coord — post to shared ntfy channel from CLI / THUG / any agent
# Usage:
#   ./coord.sh STATUS "DC online, RAM 62%"
#   ./coord.sh ALERT  "MT4 disconnected"
#   ./coord.sh DONE   "b62 backtest complete"
#   ./coord.sh ASK    "Nasif: approve PAUSE lift?"
#   ./coord.sh INFO   "any message"
#
# Set COORD_AGENT env to override agent name (default: hostname)
# Set COORD_TOPIC env to override ntfy topic (default: signal-coord)

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

curl -s \
  -H "Title: ${TITLE}" \
  -H "Content-Type: text/plain" \
  -d "${MSG}" \
  "https://ntfy.sh/${TOPIC}" \
  && echo "✓ sent to #${TOPIC}" \
  || echo "✗ failed"
