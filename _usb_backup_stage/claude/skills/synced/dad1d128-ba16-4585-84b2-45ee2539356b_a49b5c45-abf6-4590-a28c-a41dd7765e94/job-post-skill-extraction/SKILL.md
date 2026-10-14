---
name: "job-post-skill-extraction"
description: "Use when job posts are pasted or found, to update the keyword dropdown, missing-skills list, aspirational skills table and study quizzes."
---

# Job post to skills workflow (job tracker artifact)

For every pasted or discovered job post, update the tracker artifact (single HTML file with embedded JSON `#jobdata`):

1. **Job record**: fields t, co, loc, city, pay, arr, et, region, band, dod, haspay, href, lk, age, note, mid (hourly x 2080 for mid). If the company and title already exist, update that record instead of duplicating. Regions: Jacksonville / NE FL, Tampa Bay, Orlando / Central FL, Panhandle, South FL, Fort Myers / SW FL, Statewide / remote. Pay bands by mid.
2. **Routing**: DoD/clearance posts go to the DoD page (dod true, last page). Partly-IT or stretch posts go to the yellow Borderline table (and bump its count). Applied posts get applied:true and a note with the date.
3. **Fit note**: give a percent fit with pros and gaps, based on Nasif's resume (help desk, M365/Exchange/Azure AD/Intune, credit-union tier 2 work).
4. **Skills**: add short keyword lists to `SKILL_KEYWORDS` (powers the Live Job Search keyword dropdown), add missing skills to `SK_LACK` (yellow underline), and add rows to `#possibleSkillsTable` (aspirational skills) with the source post.
5. **Study**: add a 4-5 question multiple-choice quiz per new missing skill in the quiz data and a `MAP` regex so the Study button appears. Prefer multiple choice.
6. **Applications**: if the user applied, mark it and keep the EEOC section current.
7. Test with a headless browser (no page errors), back up the previous file, republish to the same artifact URL, and tell the user briefly what changed.

Never remove existing features (live text edit, sortable tables, index) without asking.