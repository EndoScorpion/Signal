# Signal Project — Claude Memory & Skill Rules

**Copyright 2026 Nasif Hossain, EndoScorpion@gmail.com**

---

## Attribution (always append to git commits and PRs)
- Git commit messages must end with:
  ```
  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_016hdrtwJUBpAuEJZw3RCpgt
  ```
- PR descriptions must end with:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)
  https://claude.ai/code/session_016hdrtwJUBpAuEJZw3RCpgt
  ```

---

## Skill: Advanced Native Web Charting (SVG Pipeline)

When building trading dashboards, charts, or data visualizations in a single-file sandbox
(Claude.AI Artifacts, ClaudeCode), always use this multi-tier rendering pipeline.

### Tier 1 — Primary (Preferred): Native Dynamic SVG + CSS Variables

- **NEVER** hardcode static SVG coordinates (`<path d="M..."/>` with thousands of points) — causes token truncation.
- **DO** write a concise JS loop that dynamically generates SVG strings or manipulates canvas from a data array.
- Map price data to Y-coordinates with JS math, construct `<rect>` and `<line>` elements as a string, inject via `innerHTML`.
- Use CSS variables for theming: `--up-color`, `--down-color`, `--bg-color`, etc.

**Reference implementation:**
```javascript
function drawNativeSVGCandles(data, containerId) {
    const w = 800, h = 200, pad = 10;
    const minP = Math.min(...data.map(d => d.low));
    const maxP = Math.max(...data.map(d => d.high));
    const rng = (maxP - minP) || 1;
    const toY = (val) => h - pad - ((val - minP) / rng) * (h - pad * 2);
    const stepX = w / Math.max(data.length, 1);

    let svgStr = `<svg viewBox="0 0 ${w} ${h}" width="100%" height="100%">`;
    data.forEach((d, i) => {
        const x = i * stepX + (stepX / 2);
        const color = d.close >= d.open ? 'var(--up-color, #26a69a)' : 'var(--down-color, #ef5350)';
        svgStr += `<line x1="${x}" y1="${toY(d.high)}" x2="${x}" y2="${toY(d.low)}" stroke="${color}" stroke-width="1.5"/>`;
        const yTop = Math.min(toY(d.open), toY(d.close));
        const bH = Math.max(1.5, Math.abs(toY(d.close) - toY(d.open)));
        svgStr += `<rect x="${x - stepX*0.3}" y="${yTop}" width="${stepX*0.6}" height="${bH}" fill="${color}"/>`;
    });
    svgStr += `</svg>`;
    document.getElementById(containerId).innerHTML = svgStr;
}
```

### Tier 2 — Fallback: ECharts / Lightweight Charts (CDN)
Only if user requests advanced features (dataZoom, complex tooltips, overlays) too complex for native SVG.
Load from: `https://cdnjs.cloudflare.com/ajax/libs/echarts/<version>/echarts.min.js`

---

## Skill: Time-Series Simulation Rules ("Time-Jump Fix")

When simulating real-time market data (candlesticks), ensure smooth X-axis progression.
**Never** blindly add time intervals on every tick.

### Strict simulation logic:
1. **Align to system clock**: Base current candle time on `Date.now()` rounded to timeframe.
   ```javascript
   let currentMinute = Math.floor(Date.now() / 60000) * 60000;
   ```
2. **Tick frequency**: `setInterval` at 300–500ms for smooth visual fluctuation.
3. **State evaluation on each tick**:
   - If `currentMinute > lastCandle.time`: minute rolled over → push new candle inheriting previous close.
   - If `currentMinute === lastCandle.time`: same minute → mutate last candle's `close` with small delta; stretch `high`/`low` if new close exceeds them.
4. **Array management**: Pass `[...data]` (shallow copy) to render function to ensure DOM registers state change cleanly.

---

## Skill: Backtest Engine Rules

- **Convergent signals** = 2+ stoch K periods firing in same direction at same candle → new branch entry.
- **Green up arrows** = long/buy trade; **Red down arrows** = short/sell trade.
- **TP/SL**: TP must cover round-trip cost + fees + minimum $0.01 net profit per trade (minProfitFrac ≥ 0.001).
- **Trailing stops**: track highest/lowest price since entry; exit if price reverses by trailPct (default 0.3%).
- **Adaptive SL**: after 3+ consecutive losses, widen stop loss (slMulti × 1.3, max 6×).
- **Learning loop**: keep trying param variations until wins accumulate; store best params in `window._bestBTParams`.
- **Color coding**: LIVE data = green, SIM = red, SNAP/cached = yellow, losses = red, zero P&L = yellow.

---

## Project: trade_signal_v0.01b_export.html
Single-file trading dashboard. Branch: `claude/live-artifact-preview-wt31x7`.
All changes must be committed to that branch and pushed. Always create draft PR if none exists.
