---
name: "job-search-discovery"
description: "Use to find more IT help desk and L1/Tier 1 job posts in Florida with ZipRecruiter, Firecrawl and web search, stopping at a plateau and logging results."
---

# Job search discovery loop

Goal: find new IT / help desk / L1-Tier 1 / non-sales call-center posts for Nasif (Florida, plus remote), add them to the tracker artifact, and record how they were found.

## Method order (cheapest and most useful first)
1. **ZipRecruiter connector `search_jobs`** (5 results per call, includes pay, days posted, direct apply link). Search by role and city: help desk technician, IT support specialist/technician, desktop support technician, service desk, technical support representative. Cities: Jacksonville, Tampa, Tallahassee, Pensacola, Panama City, Orlando, Miami, Fort Myers, Gainesville, Daytona Beach. Also remote (location_types REMOTE, seniority NO_EXPERIENCE/JUNIOR, max_posted_minutes_ago 10080-20160). Use `offset` 5 for a second page. Use radius_miles 50-60 for small cities. Send several calls in parallel.
2. **Firecrawl `firecrawl_search`** (2 credits, web results with excerpts): employer career pages, staffing firms, state/university sites. Use `tbs: qdr:w` (week) or `qdr:m`, and `includeDomains` for gov or career sites.
3. **Firecrawl `firecrawl_scrape` with `formats: ["query"]`** and a short targeted prompt (5 credits): only for promising posts. Ask for title, company, location, pay, remote/hybrid, contract or direct, requirements, posted date. It fails on script-loaded pages (State of Florida, ZipRecruiter company pages); do not retry.
4. **Built-in WebSearch** for exact posting links and titles.

## Loop rules
- Work in rounds of 5-8 parallel searches. After each round, dedupe against the tracker (normalize company + title) and count new posts by type.
- Stop at a plateau: when the new core L1/help-desk count per round falls to 1-2 and results are mostly field-service or non-IT jobs. A typical run is 4 rounds.
- Do not use WebFetch/curl alternatives when a fetch is blocked; report it.

## Classify each post
L1 / Tier 1 help desk and service desk; desktop/deskside/field IT; sysadmin/network/intermediate service desk; State of Florida computer support (titles only); remote tech-support/call-center (non-sales, non-insurance-sales); DoD/clearance (goes on the last page only); borderline (partly IT or stretch: yellow Borderline section, nothing removed). Skip and count: field-service/front-desk/non-IT, bilingual-only, expired, too senior, outside Florida and not remote.

## Record results
Add to the artifact: a Discovery log section with minimized (details) buttons per method and per type, a rounds-yield table, and an index group with one line per type and the count. Include the method, queries, what worked, what failed. Use direct ZipRecruiter job_redirect_url links when available, otherwise career-page links.

## Always
Never remove existing features or visuals without asking. Back up the artifact source before editing. Offer a .txt backup occasionally. End replies with a short usage estimate.