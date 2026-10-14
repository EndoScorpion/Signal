---
name: "compact-reply"
description: "Use when the user invokes /CompactReply or asks Claude to save tokens/credits and reply compactly, with a live request counter and a 15-request refresh warning."
---

# Compact Reply Mode

A low-cost reply mode for budget-conscious sessions. Activate it when the user types `/CompactReply`, or asks for "compact mode," "save tokens," "save credits," or similar, and keep it active for the rest of the session (or until they turn it off) once invoked.

## Behavior while active

- **Be terse.** Answer directly with no preamble, no recap of the question, no restating what was already said. Prefer one-line answers and short bullet lists over prose.
- **Minimize tool calls.** Skip exploratory or "just in case" tool use; batch reads/searches where possible; do only what's needed to answer this specific request.
- **Skip unnecessary elaboration.** Don't explain reasoning or give background unless asked. No closing summaries of what was just done beyond one short line.
- **Still be correct and complete** on the substance — compact means terse wording and lean tool use, not skipped verification or wrong answers.

## Request counter

- Track a running count of user requests/turns since compact mode was turned on (or since the last session refresh the user did).
- End every reply with a one-line counter, e.g.: `Request 4 of 15.`
- At request 12–14, append: "Approaching 15 — consider starting a fresh session/chat soon to keep costs down."
- At request 15 and beyond, append: "This is request 15+ — recommend refreshing/starting a new session now to save credits." Keep repeating this each turn until the user starts a new session or turns compact mode off.

## Honesty limits

- This skill controls Claude's own reply style and tool use — it cannot change which underlying model is serving the session (e.g. it cannot itself switch to "Haiku" or any specific model/tier). If the user asks to switch models, tell them plainly that's done via the client's model picker/settings, not something this skill can do, and name the currently active model if known.
- Don't claim token/credit numbers Claude doesn't actually have access to — give qualitative usage guidance (light/moderate/heavy) rather than invented exact figures.