---
name: "autonomous-job-hunt"
description: "Use when asked to find jobs, sweep Reddit/job boards, dedupe new posts against what the tracker already has, log skill gaps, or prep an IT skill-gap quiz."
---

# Autonomous job hunt, dedupe and skill-gap quiz

## Phase 1: Context
1. Read the candidate profile (target titles, stack, location, pay) and the job tracker's current records. The tracker's job list is the 'seen' ledger; match on employer + title + city/href so nothing is added twice.
2. Note standing rules: ask a yes before using Firecrawl and only after free methods (WebSearch/WebFetch, connectors) stop finding new posts; never remove anything without asking; borderline (partly IT/stretch) posts go yellow in a Borderline section; senior/lead/Tier 3+ only in the senior list; DoD/clearance last; expired posts only in the grey minimized section; dates like '8 Oct 2026'.

## Phase 2: Crawl
1. Use free methods first: WebSearch (site: queries for boards), WebFetch on job-board and employer pages, user-pasted threads. Reddit pages usually cannot be searched or fetched here, so rely on pasted text and board listings; never claim a Reddit post was verified if it was not.
2. Keep a post only if it is a real, current, IT/support-relevant role the candidate can plausibly take (Florida or true remote). Match score about 75% or higher against the stack.
3. Record source, date seen and caveats (stale, unverified, borderline) on every record. Never invent recruiter names or emails; give search links instead.

## Phase 3: Memory
1. Append new records and links without removing anything; show unique post counts.
2. If a missing skill or cert appears in 3 or more listings, add it to the desired-skills list and keyword/location/skill search lists.

## Phase 4: Skill-gap quiz (optional)
1. From the logged gaps, write 3 to 5 production-level questions (K8s/CNI MTU, DNS egress control, zero-trust mTLS, multi-region replication, M365/Intune/AD for this candidate).
2. Show the answer and a one-line reason after each; track score and weak topics in a small progress note.

## Output
Short summary: counts added, caveats, what was skipped and why; then a one-line usage estimate and an occasional offer of a .txt backup.