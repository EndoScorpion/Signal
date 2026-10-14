---
name: ts-full-artifact
description: >
  Produce a full self-contained .html artifact (rendered in the artifact panel
  to the right) for the Trade Signals dashboard. Use when the user says
  "full artifact preview", "show full artifact", "artifact to the right",
  or any phrasing asking for the HTML file in the panel — NOT an inline widget.
  Never use visualize:show_widget for this skill; always use create_file +
  present_files.
aliases: [full artifact preview, ts artifact, trade signals artifact]
sources: [chat]
---

# Trade Signals — Full Artifact Skill

## Prime directive

When triggered, produce a **complete self-contained HTML file** and present
it via `present_files`. The file opens in the artifact panel to the right of
chat in Claude Web / Chrome. Do NOT call `visualize:show_widget` — that
renders an inline iframe widget, not a panel artifact.

## Trigger phrases (fire this skill)

- "full artifact preview"
- "show full artifact"
- "artifact to the right"
- "artifact in the panel"
- "html file preview"
- "dynamic live [artifact/preview]" when a Trade Signals file is in context
- Any prior `/trade-signals-preview` invocation where the user corrects
  "no, I want the full artifact"

## Workflow

### Step 1 — Extract from uploaded file (cheap bash slices)

```python
with open('/mnt/user-data/uploads/<file>.html','r') as f:
    c = f.read()

# Copyright
cp = c.find('<div class="copyright">')
print(c[cp:c.find('</div>',cp)+6])

# Toolbar (first 3000 chars)
t1 = c.find('<div id="toolbar">')
print(c[t1:t1+3000])

# Snapshot bar
s1 = c.find('<div id="snapshotBar"')
print(c[s1:s1+600])

# Panel template
idx = c.find('innerHTML = `\n    <div class="panel-head"')
print(c[idx:idx+3000])
```

Never load the full file into context — always slice.

### Step 2 — Build the HTML file

Write a **complete** `<!DOCTYPE html>` file to `/mnt/user-data/outputs/`.

**Required sections (never omit):**

| # | Section | Notes |
|---|---------|-------|
| 1 | Copyright bar | Exact text from file, Times New Roman serif |
| 2 | Volume Leader Bar | Stablecoin + Non-stablecoin pair spans, ↻ Refresh |
| 3 | Status row | Live clock (ticks via JS), global WSS dot + text |
| 4 | Main toolbar | All buttons: + New Panel / Backup All / Restore All / Auto-Arrange / WSS / 📡 Sources ▾ / + Live Chart Prompt / S·M·L font toggle / News / ? / ⌨ Terminal / ⬇ Download |
| 5 | News ticker bar | Scrolling marquee, toggleable |
| 6 | Snapshot bar | Auto toggle, interval input, Snapshot Now, View Snapshots |
| 7 | Min 4 panels | See panel spec below |
| 8 | JS terminal | Collapsible eval console at bottom |

**Per-panel spec:**

- Panel head: title, tricolor dot (live/warn/dead), timeframe select,
  symbol input, provider input, source info text
- Icon buttons: ↻ Refresh, B Backup, R Restore, — Minimize, + Maximize,
  ⬜ Reset Size, X+ X− Y+ Y− ↺
- Chart area: mock candlestick flex divs (no canvas), status line,
  price hi/lo label
- Chart controls row 1: Line | Candles | Overlay | ECharts | SVG |
  X+ | X− | Y+ | Y− | Reset | Upload CSV
- Indicator row: Volume | Stoch | Range | CCI/ADX | [spacer] | + MA
- Resize handle (corner triangle)

**Backtest panel** (on one panel, e.g. ETH/USDT):

```html
<div class="bt-section">
  <div class="bt-header">⚗ Backtest Engine</div>
  <div class="bt-controls">
    <select id="btStrat">SMA Crossover / RSI Reversal</select>
    <input id="btPeriod" value="1y">
    <input id="btCapital" value="10000">
    <button onclick="runBacktest()">▶ Run</button>
    <span id="btSpinner" style="display:none">● Running…</span>
  </div>
  <div id="btResult"><!-- populated by runBacktest() --></div>
</div>
```

`runBacktest()` must: show spinner, hide Run btn, wait ~1.5s, display
Return / Ann / Win Rate / Sharpe / MaxDD / Trades / Final equity.

### Step 3 — Color spec (always dark trading theme)

```
page bg:        #0b0c10
panel bg:       #131722
panel head:     #1a1e29
source/ind row: #161a24
grid/border:    #2a2e39
toolbar bg:     #000
toolbar btn:    bg #000 / color #3f3 / border #2a2
ctrl btn:       bg #0d0f14 / color #9aa / border #333
candle up:      #26a69a    candle down: #ef5350
ind btn active: bg rgba(160,120,255,.22) / color #c7a8ff / border #a078ff
mode-candle on: bg rgba(38,166,154,.25) / color #26a69a
mode-line on:   bg rgba(33,125,245,.25) / color #7af
mode-overlay:   bg rgba(255,180,0,.18) / color #ffb400
mode-echarts:   bg rgba(180,120,255,.2) / color #b478ff
wss dot:        #3ecf5e + CSS pulse animation
```

Never use Claude light theme tokens (`--surface-1`, `--text-primary`, etc.).
This file is standalone — no CDN imports needed, pure HTML/CSS/JS.

### Step 4 — JS interactivity (required)

```js
// Clock — tick every second
setInterval(tick, 1000);

// Candle builder — flex divs, 14-15 per panel, random heights
function buildCandles(id) { ... }

// Price sim — update status lines every ~2.5s
setInterval(updatePrices, 2500);

// setMode(btn, cls) — toggle mode-* class on ctrl-row buttons
// toggleInd(btn)    — toggle .on on indicator buttons
// toggleNews()      — show/hide news bar
// toggleSnap()      — toggle Auto:On/Off label + color
// addPanel()        — dynamically append new panel with full rows
// runBacktest()     — sim delay + display metrics
// termRun(e)        — eval JS terminal on Enter
```

### Step 5 — Output + present

```python
# Write
with open('/mnt/user-data/outputs/trade_signals_preview_<slug>.html','w') as f:
    f.write(html)
```

Then call `present_files(['/mnt/user-data/outputs/trade_signals_preview_<slug>.html'])`.

The file card renders in the artifact panel — user clicks to open in Chrome.

## Hard rules

- ❌ Never call `visualize:show_widget` for this skill
- ❌ Never omit chart controls row 1 or indicator row from any panel
- ❌ Never use `position:fixed` (breaks standalone HTML scroll)
- ❌ Never import external CDN resources (file must work fully offline)
- ✅ Always use `create_file` → `present_files`
- ✅ Always include live clock JS, price sim JS, backtest JS
- ✅ Always include the JS terminal (collapsible)
- ✅ Candlesticks = flex divs only (no canvas, no ECharts at preview time)
- ✅ File must be fully self-contained (one .html, no external deps)

## Prose after present_files

One line max — e.g.:
> "Full artifact in the panel — 4 panels, live clock, backtest on ETH, JS terminal."

Never enumerate all buttons — the user can see them in the file.
