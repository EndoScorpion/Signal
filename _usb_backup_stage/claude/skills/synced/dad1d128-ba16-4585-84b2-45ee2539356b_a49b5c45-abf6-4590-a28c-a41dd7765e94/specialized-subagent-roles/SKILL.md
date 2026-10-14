---
name: "specialized-subagent-roles"
description: "Use when splitting a multi-step task (job crawl, fit scoring, quiz) across agents: use role-specialized subagents with one writer, never identical cloned agents."
---

# Role-specialized subagents, not clones

## Rule
Do not run identical cloned agents on the same job. Clones duplicate context, burn rate limits and credits, and race when writing shared memory or ledger files. Use one orchestrator plus a few role-specific workers.

## Default roles for the job pipeline
1. Scraper: runs searches/fetches only, returns structured candidate posts (title, employer, city, pay, link, source, caveats). No writes to shared files.
2. Matcher: read-only access to the resume/profile; scores each post 0-100% fit, flags borderline/senior/clearance, lists missing requirements.
3. Quiz coach: reads the logged skill gaps and writes 3 to 5 scenario questions with answers and one-line reasons.

## Orchestrator duties
- Be the single writer: merge worker outputs, dedupe against existing records, then update the tracker, the seen-ledger and skill_gaps notes once.
- Give each worker a narrow brief (goal, files to read, what to return); workers return summaries, not file dumps.
- Only spawn workers when tasks are independent or large; for a few lookups do the work inline to save credits.

## Setup notes
- In a Claude Project, keep the resume, target pay, locations and seniority in Project Knowledge and the role rules in custom instructions.
- In a code repo, keep the top-level instructions file short (under about 80 lines) and put role detail in skills.
- Heavier peer-to-peer agent teams only for multi-day research where agents must review each other; costs far more.
- Ask before using paid crawlers; never remove existing tracker items without asking.