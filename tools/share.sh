#!/bin/bash
# share.sh — Upload a file to signal-status/shared/ via GitHub API, return raw URL
# Usage: ./share.sh path/to/file
# Token from: $GITHUB_TOKEN, $GH_TOKEN, or ~/.claude/.gh_token

set -e

FILE="$1"
REPO="endoscorpion/signal-status"
BRANCH="main"

if [ -z "$FILE" ]; then echo "Usage: $0 <file>"; exit 1; fi
if [ ! -f "$FILE" ]; then echo "File not found: $FILE"; exit 1; fi

# Resolve token
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN}}"
if [ -z "$TOKEN" ] && [ -f "$HOME/.claude/.gh_token" ]; then
    TOKEN=$(cat "$HOME/.claude/.gh_token")
fi
if [ -z "$TOKEN" ]; then echo "No token: set GITHUB_TOKEN or ~/.claude/.gh_token"; exit 1; fi

FILENAME=$(basename "$FILE")
TS=$(date -u +%Y%m%d_%H%M%S)
REMOTE="shared/${TS}_${FILENAME}"
B64=$(base64 -w 0 "$FILE")
API="https://api.github.com/repos/${REPO}/contents/${REMOTE}"

# Check existing SHA
SHA=$(curl -sf -H "Authorization: token $TOKEN" \
     -H "Accept: application/vnd.github+json" \
     "$API" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sha',''))" 2>/dev/null || true)

if [ -n "$SHA" ]; then
    BODY="{\"message\":\"share: $FILENAME\",\"content\":\"$B64\",\"branch\":\"$BRANCH\",\"sha\":\"$SHA\"}"
else
    BODY="{\"message\":\"share: $FILENAME\",\"content\":\"$B64\",\"branch\":\"$BRANCH\"}"
fi

curl -sf -X PUT "$API" \
     -H "Authorization: token $TOKEN" \
     -H "Accept: application/vnd.github+json" \
     -H "X-GitHub-Api-Version: 2022-11-28" \
     -H "Content-Type: application/json" \
     -d "$BODY" > /dev/null

RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}/${REMOTE}"
echo ""
echo "Uploaded : $FILENAME"
echo "Raw URL  : $RAW"
echo ""
echo "$RAW"
