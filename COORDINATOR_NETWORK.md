# Coordinator Network — saved 17 Oct 2026

## This session
- ID: session_01AwGqTBwwANZ9wkVkawhUeJ
- Title: Board game combining Monopoly and Life
- Owner: Nasif (endoscorpion@gmail.com)
- Repos: EndoScorpion/Signal, EndoScorpion/MQL
- Branch: claude/monopoly-life-board-game-19wke4

## Cloud Coordinator (reachable via send_message)
- Session: session_01Mq2bMczc5kd2NRjKs2Sxgn
- Title: </> <-> (Cloud Coordinator) ClaudeCode
- Project channel: chan_01FBcuCkxBs6Xeu1VMX4W8e9
- Status: fully available, no tasks in flight
- Migration: approved both ends

## GOON Coordinator (cross-account — relay through Nasif only)
- Session: session_016WSkJ8PKnSRX16LYuQdqPd
- Channel: chan_01G28AKCrBTUmVa3k3L6nLXA
- Status: idle, waiting for go-ahead on Signal backtesting work
- Constraint: send_message blocked cross-account → all messages relay via Nasif

## Relay rule
- This session → Cloud Coordinator: direct send_message ✅
- This session → GOON Coordinator: NOT direct — must go via Nasif ❌→✅
- GOON Coordinator → this session: NOT direct — must go via Nasif ❌→✅
