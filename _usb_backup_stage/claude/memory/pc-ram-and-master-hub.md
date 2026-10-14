---
name: pc-ram-and-master-hub
description: "Nasif's PC has 5.8 GB RAM; ClaudeHub master controller setup, RAM gates, and paste issues"
metadata:
  node_type: memory
  type: project
  originSessionId: d18a4f8d-ceb3-41ff-9580-5082760bf98a
  modified: 2026-10-12T08:33:40.659Z
---

PC has only 5.8 GB RAM; each Claude CLI + its pdf/desktop-commander node helpers costs ~0.5 GB. Gates: MT4 >= 1.0 GB free, new CLI clone >= 1.5 GB.
Master controller (set up 2026-10-12): C:\Users\endos\ClaudeHub (hub.ps1, CLAUDE.md, start_master.bat, .txt backups). It owns the MT4 queue (MT4_Backtest\queue.txt via run_queue.ps1 / watch_queue.ps1). Cloud sessions are reached one-way via SendMessage or the Signal repo git bridge (branch claude/mql4-analysis-comments-bd4kz3, data/ out, results/ in).

**Why:** admin ("Run as admin") Claude windows can't be pasted into, can't be seen by ListAgents, and their messages never reach other sessions. PowerShell ISE can't host the claude CLI. Shift+Insert paste is broken on this PC (PowerToys remap failed; user wants to fix later).
**How to apply:** tell the user to start CLIs non-admin in Windows Terminal; for input, suggest typing a short command that points at a file instead of pasting. Check RAM before suggesting any new process.
