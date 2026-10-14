---
name: trade-signals-preview
description: >
  Render a full static live-preview mockup of the Trade Signals HTML dashboard
  as a Claude artifact visualizer widget. Use this skill ANY TIME the user asks
  to "show a preview", "show the live preview", "show a dynamic artifact preview",
  "visualize the file", or any similar phrasing related to the Trade Signals HTML.
  Fire immediately — visual first, no explanations before the widget renders.
  This skill also governs what must ALWAYS be present in the preview: never omit
  the global toolbar buttons, per-panel header buttons, chart control rows, or
  indicator row. If any of these are missing from the widget output, the preview
  is wrong.
---

# Trade Signals Preview Skill

## Prime directive

**Visual first. Always.** No preamble, no explanation before the widget. Call
`visualize:read_me` (module: `mockup`) then immediately call `visualize:show_widget`.
Any prose goes after the widget, briefly.

## Trigger phrases

Fire this skill on any of:
- "show a preview" / "show me a preview"
- "live preview" / "dynamic preview" / "artifact preview"
- "show the UI" / "show the dashboard"
- "visualize the file" / "render the file"
- "what does it look like" (when a Trade Signals file is in context)

## Workflow

### Step 1 — Extract from uploaded file

Read the uploaded HTML to extract current UI state. Key targets:

```python
# Toolbar buttons (id="toolbar") — extract all <button> text + styles
# Panel template (innerHTML = `) — extract .panel-head, .source-row,
#   .chart-controls, .indicator-row, .ma-popover
# Snapshot bar (id="snapshotBar") — extract buttons + inputs
# CSS variables from <style> block
# Copyright line
```

Use bash/python to slice out just these sections — never load the full 1MB+ file
into context. Target selectors:

| Section | Selector / marker |
|---|---|
| CSS vars + theme | `<style>` block |
| Global toolbar | `id="toolbar"` div |
| Snapshot bar | `id="snapshotBar"` div |
| Panel template | `` innerHTML = ` `` (template literal) |
| Panel head buttons | `.panel-btns` inside template |
| Chart controls row 1 | `.chart-controls` (mode + zoom buttons) |
| Chart controls row 2 | `.indicator-row` (Volume/Stoch/Range/CCI/ADX/+MA) |
| Copyright | `.copyright` div |

### Step 2 — Build the widget

Reconstruct all UI as static HTML. Use the actual button labels/styles extracted
from the file — never guess or use placeholders.

**Required sections (never omit any):**

1. **Live clock** — `14:22:37 EDT` style, top-left, green monospace
2. **Copyright line** — exact text from file
3. **Global toolbar** — every button present in `id="toolbar"`, with correct
   colors (WSS Stream = blue-tinted border, Live Chart Prompt = amber-tinted,
   News = purple-tinted). Include WSS status dot + text, font size S/M/L toggle.
4. **Snapshot bar** — Auto on/off button, interval inputs, Snapshot Now, View Snapshots
5. **Panel layer** — at least 2 sample panels showing:
   - Panel header: title (e.g. `BTCUSDT · 5m`), all icon buttons
     (↻ Refresh, B Backup, R Restore, — Minimize, + Maximize, S Reset Size)
   - Source row: tricolor dot, source select, timeframe select, info text
   - Chart body: mock candlestick bars (use inline divs, no canvas)
   - Status line: price + change text
   - **Chart controls row 1**: Line / Candles / Overlay / ECharts / X+ / X− / Y+ / Y− / Reset / Upload CSV
   - **Chart controls row 2 (indicator row)**: Volume / Stoch / Range / CCI/ADX / + MA (right-aligned)
   - Resize handle (corner triangle)

### Step 3 — Color fidelity

Always use the dark trading theme — never the Claude light theme tokens:

```css
--tv-bg: #131722
--tv-grid: #2a2e39
background (page): #0b0c10
toolbar buttons: background #000, color #3f3, border #2a2
chart-controls buttons: background #0d0f14, color #9aa, border #333
active mode button (candle): background rgba(38,166,154,0.25), color #26a69a
active indicator button: background rgba(160,120,255,0.22), color #c7a8ff
WSS live dot: #3ecf5e with pulse animation
panel head: #1a1e29
source/indicator rows: #161a24
```

### Step 4 — Candlestick mock

Use flex divs — no canvas, no ECharts (both require runtime):

```html
<div style="display:flex;align-items:flex-end;gap:2px;position:absolute;inset:10px 10px 20px;">
  <!-- repeat ~10x, vary heights randomly -->
  <div style="display:flex;flex-direction:column;align-items:center;flex:1;">
    <div style="width:1px;height:20px;background:#555;"></div>
    <div style="width:100%;height:18px;background:#26a69a;border-radius:1px;"></div>
    <div style="width:1px;height:8px;background:#555;"></div>
  </div>
</div>
```

Alternate green (`#26a69a`) and red (`#ef5350`) bodies. Vary wick/body heights
for visual realism.

## Hard rules — never violate

- ❌ Never omit the chart controls row 1 (mode + zoom buttons)
- ❌ Never omit the indicator row (Volume/Stoch/Range/CCI/ADX/+MA)
- ❌ Never omit global toolbar buttons
- ❌ Never use `position:fixed` (collapses iframe)
- ❌ Never render explanation prose before the widget
- ✅ Always show all buttons from the extracted toolbar, in order
- ✅ Always include the resize handle on each panel
- ✅ Always show the WSS status inline in the toolbar
- ✅ Always use the dark trading theme colors, never Claude light theme

## Prose after the widget

One or two lines max. Example:
> "Two-panel preview — BTCUSDT/ETHUSDT. All toolbar and chart buttons present."

Do not summarize what buttons exist — the user can see them.
