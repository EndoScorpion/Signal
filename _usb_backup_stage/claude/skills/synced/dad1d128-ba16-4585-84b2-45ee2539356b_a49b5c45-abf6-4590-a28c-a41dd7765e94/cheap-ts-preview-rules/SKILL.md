---
name: cheap-ts-preview-rules
description: >
  LOW COST (~500 tokens). Rules and color spec for rendering Trade Signals
  dashboard previews. Load this BEFORE cheap-ts-preview-extract. Contains
  required UI sections, color tokens, hard rules, candlestick mock pattern.
  Use when showing any Trade Signals preview or mockup.
---
## Required sections — never omit
1. Live clock (green monospace, top-left, EDT/EST)
2. Copyright line (exact text from file)
3. Global toolbar: + New Panel / Backup All / Restore All / Auto-Arrange /
   WSS Stream (blue) / + Live Chart Prompt (amber) / WSS status dot+text /
   S·M·L font toggle / News (purple)
4. Snapshot bar: Auto:Off / interval inputs / Snapshot Now / View Snapshots
5. Per panel (min 2): header icon buttons + source row + candle mock +
   status line + chart controls row 1 + indicator row + resize handle

## Chart controls row 1
`Line | Candles | Overlay | ECharts | X+ | X− | Y+ | Y− | Reset | Upload CSV`

## Indicator row
`Volume | Stoch | Range | CCI/ADX | [→right] + MA`

## Color tokens
```
page bg: #0b0c10    panel: #131722      grid: #2a2e39
toolbar btn: bg #000, color #3f3, border #2a2
ctrl btn: bg #0d0f14, color #9aa, border #333
candle-on: rgba(38,166,154,.25) color #26a69a
indicator-on: rgba(160,120,255,.22) color #c7a8ff
panel head: #1a1e29   source/ctrl rows: #161a24
wss live dot: #3ecf5e with pulse keyframe
```

## Candlestick mock (no canvas)
```html
<div style="display:flex;align-items:flex-end;gap:2px;position:absolute;inset:8px 8px 18px;">
  <div style="display:flex;flex-direction:column;align-items:center;flex:1;">
    <div style="width:1px;height:20px;background:#444;"></div>
    <div style="width:100%;height:18px;background:#26a69a;border-radius:1px;"></div>
    <div style="width:1px;height:8px;background:#444;"></div>
  </div><!-- repeat ~10x alternating #26a69a / #ef5350 -->
</div>
```

## Hard rules
- Never use position:fixed (collapses iframe)
- Never omit chart controls row 1 or indicator row
- Never use Claude light theme — always dark trading theme
- Visual first — no prose before widget renders
