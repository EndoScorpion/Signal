---
name: bundler
description: >
  Bundle any active HTML/CSS/JS/SVG/JSON web app into a single self-contained
  offline-ready auto-repair HTML file. Use this skill when the user wants to:
  (1) backup their current artifact or preview as a portable offline file,
  (2) create a self-healing snapshot of a web workspace, (3) bundle all assets
  into one downloadable HTML, (4) restore a previous session from a backup file.
  Triggers: "backup this", "bundle this", "make an offline backup", "save this
  as a portable file", "create a backup file", "make it work offline",
  "auto-repair backup", "snapshot this workspace", "bundle my artifact".
  Also trigger proactively after generating or updating any significant artifact
  by offering: "Would you like an offline backup bundle of this?"
---

# Full-Stack Asset Backup & Auto-Repair Bundler

## Role

Bundle active web artifacts into a single monolithic HTML file that:
- Embeds all CSS inline in `<style>` blocks
- Inlines all SVG assets directly into the DOM
- Serializes all app state/config/chart data into a `<script type="application/json">` tag
- Includes a self-healing bootstrap that detects and repairs DOM corruption on load
- Works fully offline in any modern browser

## Trigger conditions

**Proactive**: After generating or significantly updating an HTML/JS artifact,
append to your response:
> "Would you like an offline backup bundle of this?"

**Reactive**: Fire immediately when the user says any of the trigger phrases above.

## Workflow

### Step 1 — Assess the source

Determine what needs bundling:
- **Uploaded HTML file** → read it from `/mnt/user-data/uploads/`
- **Artifact just generated** → use the code from this conversation
- **Backup file being restored** → parse the `#backup-state-json` tag and rebuild

### Step 2 — Run the bundler script

```bash
python3 scripts/bundle.py <input.html> --output /mnt/user-data/outputs/backup_bundle.html
```

The script will:
1. Parse HTML and inline all `<link rel="stylesheet">` CSS
2. Preserve all existing `<style>` blocks
3. Collect all inline `<svg>` elements (already inlined — no action needed)
4. Extract any `<script type="application/json">` state blocks
5. Inject the auto-repair bootstrap framework
6. Write one self-contained `.html` output file

### Step 3 — For Trade Signals / large single-file apps

When the source is already a monolithic HTML (like Trade Signals), the bundler:
- Verifies all CSS is already inline (it is)
- Snapshots current localStorage state into the `#backup-state-json` tag
  via an injected `<script>` that runs once on open
- Injects/updates the auto-repair bootstrap
- Sets a `data-backup-timestamp` on the root element

### Step 4 — Deliver

Call `present_files` with the output `.html` file.
State: file size, timestamp, what was bundled.

## Auto-repair bootstrap spec

Every bundle must include this framework (see `references/bootstrap.html`
for the full template). Key elements:

```html
<script type="application/json" id="backup-state-json">
{
  "version": "1.0.0",
  "timestamp": "<ISO timestamp>",
  "appState": { ... }
}
</script>

<script>
function bootstrapWorkspace() {
  try {
    const state = JSON.parse(document.getElementById('backup-state-json').textContent);
    // restore app from state ...
  } catch(e) {
    triggerAutoRepair(e);
  }
}

function triggerAutoRepair(err) {
  // visual indicator + DOM reconstruction fallback
}

window.onload = bootstrapWorkspace;
</script>
```

## Restoration workflow

When user uploads a backup file and says "restore" or "continue from backup":
1. Read the `#backup-state-json` payload
2. Reconstruct the full artifact from the embedded code + state
3. Resume development as if the session never ended

## Script location

`scripts/bundle.py` — the main bundler. Read before running.
`references/bootstrap.html` — the auto-repair template fragment.
