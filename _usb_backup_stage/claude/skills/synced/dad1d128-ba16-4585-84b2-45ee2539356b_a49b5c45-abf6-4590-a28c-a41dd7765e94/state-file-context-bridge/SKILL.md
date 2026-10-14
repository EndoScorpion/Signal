---
name: "state-file-context-bridge"
description: "Use when moving files, state, console logs or DOM snapshots between Claude web and Claude Code/Desktop, or when backing up work so it survives a session change."
---

# Unified State, File, and Context Bridge (v1.0)

Track, snapshot and bridge environment state between the Web UI and local Claude Code/Desktop.

## 1. Payload types
Categorize every backup or generated file as one of:
- Data/config: csv, txt, xml, json
- Web/DOM: html, css, svg, js-backup, dom-snapshot
- Diagnostics: console-log, cache-info, memory-info, resource-usage

## 2. Transfer envelope
When handing context from web to local (or back), emit one JSON envelope in a markdown code block preceded by `<!-- STATE_BRIDGE_SNAPSHOT -->`:
{
  "timestamp": "ISO-8601",
  "sessionType": "web" | "local",
  "contextInfo": { "currentTask": "string", "tokenEstimate": 0 },
  "files": [ { "path": "name.ext", "type": "csv|html|txt|svg", "content": "RAW_OR_BASE64" } ],
  "diagnostics": { "consoleLogs": [], "domState": {}, "resourceUsage": {} }
}
On the web there is no local code execution: read and write these text blocks only. Do not claim a file was saved locally unless a tool confirmed it.

## 3. Local rule
If a bridge MCP server (save_bridge_snapshot / load_bridge_snapshot / list_bridge_snapshots) is connected, sync files into ./.claude_bridge/. If it is not connected, say so and fall back to the envelope or a normal file delivery.

## 4. User conventions
- File names are feature-descriptive plus version, build number and timestamp (e.g. Name_v0.01d_build016_2026-10-03-1952.ext).
- Keep at most 3 backups of the same version; offer .txt backups of important code occasionally.
- Keep replies short; show a message counter and an honest usage estimate.