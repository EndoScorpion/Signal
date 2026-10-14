---
name: "context-limit-warning"
description: "Warn the user at the top of a reply when a chat reaches 15 user messages or about 70% of the context window, whichever comes first, on any Claude surface."
---

# Context limit warning

The user is budget-conscious and restarts chats to save credits. Give an early, hard-to-miss warning.

## Trigger (whichever comes first)
- The conversation has 15 or more user messages (count every user turn, including ones sent mid-task).
- Context used is about 70% or more. Estimate it from any token or context figure visible in the session (for example remaining-token counters, system reminders, or a summary notice). If no figure is visible, estimate from the volume of long outputs, pasted files, tool results and screenshots so far, and say it is an estimate.

## What to do
1. Put a single warning banner as the FIRST line of the reply, before any other content. Use this exact style so it is easy to spot:
   `⚠️ CONTEXT WARNING: message N of 15 | about X% context used | reason: <15 messages | 70% context>`
2. Immediately below it, in one or two sentences, recommend starting a fresh chat and offer to prepare a handoff first.
3. Offer the handoff in a compact form: current build or version, what is done, what is pending, file or artifact names, and any state or backup files. If the user says yes, write it as a .txt so it can be pasted into the new chat.
4. After the first warning, repeat the banner on every following reply (shorter: just the first line) until the user starts a new chat or says to stop.
5. Before the warning threshold, when the count reaches 12 messages or about 55% context, add a softer one-line heads-up: `Heads-up: N of 15 messages, about X% context.`

## Counter
Always keep a running message counter in each reply, as `msg N/15`, when this skill is active, so the user can see the count without asking.

## Surfaces
- Web, desktop app, and mobile app: the banner is the warning. Claude cannot create an operating-system popup from a skill.
- Offline or local sandboxes and artifacts: if the user is working in an HTML artifact, offer to add an on-page warning banner or toast that counts messages or shows memory use, since a page can display a real popup but a skill cannot.
- Do not claim a popup appeared outside the chat itself.

## Keep it cheap
The warning is short. Do not recap the whole chat unless the user asks for the handoff.