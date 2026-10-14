---
name: artifact-autobackup
description: >
  Inject auto-backup and user greeting logic into every artifact Claude generates.
  Use this skill when building any HTML/React/JS artifact that should: (1) greet
  the user immediately on load, (2) auto-save its state to localStorage on every
  meaningful change, (3) restore state on reload without data loss, (4) show a
  visible backup status indicator. Triggers: "auto-backup artifact", "save state
  in artifact", "greet user on load", "artifact should remember state",
  "persist artifact data", "artifact auto-save", "artifact keeps resetting".
  Also apply proactively to any Trade Signals or dashboard artifact build.
---

# Artifact Auto-Backup + User Greeting Skill

## Prime directive

Every artifact Claude builds should be stateful by default. Apply this skill
whenever generating an HTML or React artifact that has user-configurable state
(inputs, selections, chart settings, panel positions, search history, etc.).

## What this skill injects

### 1 — Greeting on load

A one-time welcome message shown for 3 seconds on first load, suppressed on
subsequent loads via localStorage flag. Format: subtle banner, not a modal.

### 2 — Auto-backup to localStorage

State serialized to `localStorage` under a namespaced key on every change.
Debounced 800ms to avoid thrashing. Key format: `artifact_<slug>_state`.

### 3 — Restore on reload

On `DOMContentLoaded`, read saved state and rehydrate the UI before first paint.
If state is corrupt or missing, silently fall back to defaults.

### 4 — Backup status indicator

Small persistent badge (bottom-right, in-flow not fixed) showing:
- `Saved ✓` (green) — after successful write
- `Saving...` (amber) — during debounce window
- `Unsaved` (red) — if write failed

## Code template — inject into every artifact

Read `references/template.html` for the full annotated template.
Key sections to always include:

```js
const STORAGE_KEY = 'artifact_<slug>_state';
const GREETING_KEY = 'artifact_<slug>_greeted';

function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    showStatus('saved');
  } catch(e) {
    showStatus('error');
  }
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch(e) { return null; }
}

function showGreeting() {
  if (localStorage.getItem(GREETING_KEY)) return;
  localStorage.setItem(GREETING_KEY, '1');
  // show banner for 3s then fade
}

function showStatus(type) {
  // update badge: 'saving' | 'saved' | 'error'
}

// Debounced auto-save
let saveTimer = null;
function scheduleSave(state) {
  showStatus('saving');
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => saveState(state), 800);
}
```

## Greeting message format

Tailor greeting to the artifact type. Examples:
- Dashboard: `"Welcome back — your panel layout has been restored."`
- First load: `"Trade Signals loaded — your settings are saved locally."`
- Generic: `"Ready. Your work is saved automatically."`

Never use modal dialogs — greeting is a dismissible top banner only.

## Status badge spec

```html
<div id="backup-badge" style="
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 9px; border-radius:3px; font-size:10px;
  font-family:monospace; margin-top:6px;
  background:#0d1a10; color:#3ecf5e; border:1px solid #2a2;">
  <span id="badge-dot" style="width:6px;height:6px;border-radius:50%;background:#3ecf5e;"></span>
  <span id="badge-text">Saved ✓</span>
</div>
```

States:
- Saved: `background:#0d1a10; color:#3ecf5e; border:#2a2` dot `#3ecf5e`
- Saving: `background:#1a140d; color:#f2c400; border:#a86` dot `#f2c400`
- Error:  `background:#1a0d0d; color:#ef5350; border:#522` dot `#ef5350`

## Trade Signals specific

For Trade Signals panels, auto-backup must save:
- Panel positions (left, top, width, height) per panel ID
- Per-panel: symbol, timeframe, chart mode, active indicators, MA overlays
- Global: font size tier, WSS last-selected symbol, favorites list
- Snapshot interval settings

Key: `artifact_trade_signals_state`

## Restoration command

If user uploads a saved artifact and asks to restore:
1. Parse `localStorage` dump from `#backup-state-json` if present
2. OR read `artifact_*_state` keys described in the file
3. Rehydrate all UI state before first render
