---
name: model-cap-sonnet
description: Use Sonnet 5.5 only (floor and ceiling) for clones and work for now
metadata:
  type: feedback
---

Nasif (2026-10-12): "make sonnet 5 lowest the most powerful for now" — Sonnet 5.5 is both the minimum and the maximum model for spawned clones and this session.

**Why:** save usage (app showed "approaching weekly usage limit") and RAM-constrained PC.
**How to apply:** hub.ps1 -Model defaults to claude-sonnet-5-5; never pass Opus/Haiku. Revisit when Nasif says otherwise.
