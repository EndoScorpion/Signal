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

## Skill: Data Retrieval Architecture (Multi-Tier Waterfall)

All data retrieval in the Signal dashboard follows a strict priority waterfall. Each tier auto-falls
to the next on failure. The diagnostic panel (`#restDiagPopup`) logs every attempt.

### Architecture constants
```javascript
var _TFD = { // Timeframe definitions (Binance interval → bar count)
  M1:{bi:'1m',bars:1000}, M5:{bi:'5m',bars:1000}, M15:{bi:'15m',bars:500},
  M30:{bi:'30m',bars:400}, H1:{bi:'1h',bars:300}, H4:{bi:'4h',bars:200},
  D1:{bi:'1d',bars:150},  WK1:{bi:'1w',bars:80},  MN1:{bi:'1M',bars:36}
};
var _KPS = [5, 10, 15, 20]; // Stochastic K periods for convergent signal detection
var _dc = {};               // Central data cache: key = "SYM__TF", value = {data, dataType, src}
// dataType: 'live' (REST OHLCV), 'sim' (synthetic), 'snap' (sparkline/CSV/image parse)
```

### Tier 0 — WebSocket (Live tick data)
- **Source**: `wss://stream.binance.com:9443/stream?streams=btcusdt@ticker/ethusdt@ticker/solusdt@ticker/bnbusdt@ticker/xrpusdt@ticker`
- **Function**: `connectBinanceWSS()` — reconnects on close, 3-attempt backoff
- **Output**: Live `price`, `change%`, `volume` injected into `.status-line` elements
- **Known limit**: WSS gives tick data only, NOT OHLCV candles. Use REST for candle history.

### Tier 1 — Binance REST (Direct + Proxy)
```javascript
var _restDirect = 'https://api.binance.com/api/v3/klines';
var _restProxy  = 'https://corsproxy.io/?https://api.binance.com/api/v3/klines';
// Usage: ?symbol=BTCUSDT&interval=1h&limit=500
// Returns: [[openTime, open, high, low, close, volume, ...], ...]
// Parser: arr.map(k => ({open:+k[1], high:+k[2], low:+k[3], close:+k[4], volume:+k[5]}))
```
- **Function**: `fetchOHLCV(pid, interval, limit, cb)` — tries direct first, then corsproxy
- **Blocked by**: Claude.ai Artifact CSP (sandbox blocks ALL external fetch)
- **Works in**: Local .html file, Node, non-sandboxed browser

### Tier 2 — Multi-Source REST Probe Waterfall
`window._probeAllSources()` tries these in order, 4.2s timeout each:
```javascript
var sources = ['binance', 'coingecko', 'cryptocompare', 'allorigins', 'corsproxy'];
// binance:       https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=2
// coingecko:     https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
// cryptocompare: https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=5
// allorigins:    https://api.allorigins.win/raw?url=<encoded-binance-url>
// corsproxy:     https://corsproxy.io/?url=<encoded-binance-url>
```
- Sets `window._restLive = true` and `window._liveSrcWorking = srcName` on first success
- All failures → auto-triggers Tier 4 (Historical), then Tier 5 (Adaptive Synth)

### Tier 3 — CSV Download (Yahoo Finance via allorigins)
```javascript
window._tryCSVDownload = function() {
  var url = 'https://query1.finance.yahoo.com/v7/finance/download/BTC-USD?period1=0&period2=9999999999&interval=1d&events=history';
  var proxy = 'https://api.allorigins.win/raw?url=' + encodeURIComponent(url);
  // Returns text/csv: Date,Open,High,Low,Close,Adj Close,Volume
  // Parse: lines.map(l => { c=l.split(','); return {open:+c[1],high:+c[2],low:+c[3],close:+c[4]} })
}
```

### Tier 4 — Historical Sources (CryptoCompare / Bybit / CoinCap)
```javascript
// CryptoCompare histohour — free, no auth, 2000 bars per call
// URL: https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=2000
// Paginate back: add &toTs=<unix_seconds> for history scroll
// Response: d.Data.Data[] → [{time, open, high, low, close, volumeto}]

// Bybit kline — public REST, no auth
// URL: https://api.bybit.com/v5/market/kline?category=spot&symbol=BTCUSDT&interval=60&limit=200
// Paginate back: add &end=<unix_ms>
// Response: d.result.list[] → [[time,open,high,low,close,vol], ...] (newest first → reverse)

// CoinCap price history — CORS-friendly, no auth
// URL: https://api.coincap.io/v2/assets/bitcoin/history?interval=h1&start=<ms>&end=<ms>
// Response: d.data[] → [{priceUsd, time}] — price ONLY, reconstruct OHLCV by grouping
// Symbol map: bitcoin, ethereum, solana, binancecoin, xrp

window._tryHistoricalSources()  // Tries all above, stores as dataType:'snap' in _dc
window._loadMoreHistory(sym, tf) // Scroll back: fetches bars before oldest cached timestamp
```

### Tier 5 — Chart Image / Sparkline SVG Parsing
```javascript
// CoinGecko sparkline SVG — parse <polyline points="x1,y1 x2,y2 ...">
// URL: https://www.coingecko.com/coins/{coinId}/sparkline.svg
// Via proxy: https://api.allorigins.win/raw?url=<encoded-sparkline-url>
// or:        https://corsproxy.io/?<encoded-sparkline-url>

window._tryChartImages() // Fetches sparklines for BTC/ETH/SOL/BNB/XRP, parses SVG polyline
// SVG Y-axis is INVERTED — high Y = low price. Normalize: price = base + ((maxY - y) / rngY - 0.5) * priceRange
// Groups polyline points into ~100 OHLCV bars per symbol
// Stores as dataType:'snap' in _dc (only if no live data present)
```

### Tier 6 — Adaptive Synthetic Fallback
```javascript
// Parameter sweep: tries 100+ combinations of {hold bars, entry level, offset, trend}
// Finds synthetic bar generator params that produce ≥51% win rate
// Stores best params in window._bestSynthParams
window._runAdaptiveSynthSearch() // Auto-triggered after all real-data tiers fail
```

### Tier 7 — Manual Backup Options
```javascript
window._showBackupOptions() // Shows panel with:
// - Clickable "Copy URL" buttons for each API
// - Direct "Open ↗" links in new tab
// - File upload input (accepts CSV/JSON from Yahoo/Binance/CryptoCompare)

window._handleHistUpload(file) // Parses uploaded file:
// - JSON: Binance klines array [[time,o,h,l,c,v,...]] or CryptoCompare {Data:{Data:[]}}
// - CSV: Yahoo Finance format (Date,Open,High,Low,Close,Adj Close,Volume)
// Stores in _dc['BTC/USDT__H1'] and _dc['BTC/USDT__D1'] as dataType:'snap'
```

### Diagnostic Panel Architecture
```javascript
// All tiers report to the unified log via:
_restDiagEntry(name, status, detail)
// status: 'pending' | 'ok' | 'fail'
// Stored in window._diagSrcLog[] (max 40 entries, newest first)
// Rendered in #restDiagLog inside #restDiagPopup

_setTpSrc(msg, color)
// Updates #tpDataSrc status indicator in top toolbar
// Colors: #3ecf5e (live/ok), #ffb400 (snap/warn), #ef5350 (fail/blocked), #4ab4ff (hist), #aaff44 (synth)

// Diagnostic popup buttons (in #restDiagPopup):
// Binance | CoinGecko | CryptoCompare | allorigins proxy | corsproxy.io | CSV (Yahoo) | Adaptive Synth ▶ | 📸 Chart Imgs | 📅 History | ⬅ More Hist | ⚠ Backups
```

### Complete Symbol Maps
```javascript
var _UNI = {
  'BTC/USDT': {id:'BTCUSDT', base:43000, vol:0.025, type:'crypto'},
  'ETH/USDT': {id:'ETHUSDT', base:2400,  vol:0.030, type:'crypto'},
  'SOL/USDT': {id:'SOLUSDT', base:140,   vol:0.040, type:'crypto'},
  'BNB/USDT': {id:'BNBUSDT', base:280,   vol:0.025, type:'crypto'},
  'XRP/USDT': {id:'XRPUSDT', base:0.60,  vol:0.045, type:'crypto'},
  // + forex: 'EUR/USD', 'GBP/USD', 'USD/JPY'
};
var _HIST_SYMS = {
  'BTC/USDT': {cc:'BTC', coinCap:'bitcoin',      bybit:'BTCUSDT', kraken:'XBTUSD'},
  'ETH/USDT': {cc:'ETH', coinCap:'ethereum',     bybit:'ETHUSDT', kraken:'XETHUSD'},
  'SOL/USDT': {cc:'SOL', coinCap:'solana',        bybit:'SOLUSDT', kraken:'SOLUSD'},
  'BNB/USDT': {cc:'BNB', coinCap:'binancecoin',  bybit:'BNBUSDT', kraken:'BNBUSD'},
  'XRP/USDT': {cc:'XRP', coinCap:'xrp',          bybit:'XRPUSDT', kraken:'XXRPUSD'},
};
```

### CORS Proxy Helper Pattern
```javascript
async function _histFetch(url, parseOk, useProxy) {
  var urls = useProxy
    ? ['https://api.allorigins.win/raw?url='+encodeURIComponent(url),
       'https://corsproxy.io/?'+encodeURIComponent(url), url]
    : [url, 'https://api.allorigins.win/raw?url='+encodeURIComponent(url)];
  for (var i = 0; i < urls.length; i++) {
    try {
      var r = await fetch(urls[i], {signal: AbortSignal.timeout(6000)});
      if (!r.ok) continue;
      var d = await r.json();
      if (parseOk(d)) return d;
    } catch(e) {}
  }
  return null;
}
```

### Sandbox CSP Limitation (Critical)
- In Claude.ai Artifact sandbox: **ALL external `fetch()` calls are blocked by CSP.**
- `<img>` tags CAN load external images (not parseable as data).
- CORS proxy wrappers (allorigins, corsproxy) also blocked in sandbox.
- **Solution**: All data tiers auto-fall to synthetic, which always works.
- **Best practice**: Run dashboard as local `.html` file for full API access.

---

## Skill: Live Data Flow (WSS → REST → Diagnostic Integration)

### WSS Live Feed
```javascript
function connectBinanceWSS() {
  var url = 'wss://stream.binance.com:9443/stream?streams=' +
    'btcusdt@ticker/ethusdt@ticker/solusdt@ticker/bnbusdt@ticker/xrpusdt@ticker';
  _wss = new WebSocket(url);
  _wss.onmessage = function(ev) {
    var msg = JSON.parse(ev.data);
    // msg.data: {s: symbol, c: lastPrice, P: priceChangePercent, v: volume, ...}
    // Updates: DOM .status-line elements, panels.btc/eth/sol/bnb.price
  };
  _wss.onclose = function() { setTimeout(connectBinanceWSS, 3000 * (++_wssRetry)); };
}
```

### REST OHLCV Fetch (backtest engine)
```javascript
// Per-symbol fetch with direct→proxy fallback:
function _fetchBTData(pid, interval, limit, cb) {
  var params = '?symbol=' + _restSym[pid] + '&interval=' + interval + '&limit=' + limit;
  // tries _restDirect + params → _restProxy + params → cb('both failed', null)
}
// _getData(sym, tf) checks _dc cache first, then _fetchBi (Binance), then _synth fallback
// Returns: {data: [{open,high,low,close,volume},...], dataType: 'live'|'sim'|'snap'}
```

### Stochastic oscillator (core signal)
```javascript
function _stochArr(data, n) {
  return data.map((d, i) => {
    if (i < n) return null;
    var lo = Infinity, hi = -Infinity;
    for (var j = i-n; j <= i; j++) { lo=Math.min(lo,data[j].low); hi=Math.max(hi,data[j].high); }
    return hi===lo ? 50 : (data[i].close - lo) / (hi - lo) * 100;
  });
}
// _KPS = [5,10,15,20] — four stoch periods run in parallel
// Convergent signal: ≥2 of _KPS agreeing bullish/bearish at same bar → entry
```

---

## Skill: Auto-Repair & Diagnostic Patterns

### Stale data detection
```javascript
function reportDataStale(pid, reason, src, fallback, cb) {
  // Shows amber warning in status-line, logs to _diagSrcLog
  // Triggers reconnect or fallback source
}
```

### Data source color coding
| Color | Meaning |
|-------|---------|
| `#3ecf5e` green | LIVE — from Binance WSS or REST |
| `#ffb400` amber | SNAP — from sparkline/CSV/image parse |
| `#4ab4ff` blue | HIST — from CryptoCompare/Bybit/CoinCap history |
| `#aaff44` lime | SYN — adaptive synthetic |
| `#ef5350` red | FAIL / blocked / loss |
| `#aaaaaa` grey | SIM — pure synthetic (no real data) |

### Auto-repair sequence (on page load)
1. `connectBinanceWSS()` — attempt WSS live feed
2. `window._probeAllSources()` (800ms delay) — probe REST waterfall
3. On full REST failure → `window._tryHistoricalSources()` (CryptoCompare/Bybit/CoinCap)
4. Historical failure → `window._runAdaptiveSynthSearch()` — sweep synth params
5. User can manually trigger: 📸 Chart Imgs | 📅 History | ⬅ More Hist | ⚠ Backups

### Diagnostic log entry pattern
```javascript
// Always log both to the panel AND set the toolbar status:
_restDiagEntry('Source Name', 'pending'|'ok'|'fail', 'human-readable detail string');
_setTpSrc('short status message', '#colorHex');
// Then trigger backtest if data loaded:
setTimeout(function(){ if(typeof runStochBTs === 'function') runStochBTs(); }, 300);
```

---

## Project: trade_signal_v0.01b_export.html
Single-file trading dashboard. Branch: `claude/live-artifact-preview-wt31x7`.
All changes must be committed to that branch and pushed. Always create draft PR if none exists.
Artifact URL: `https://claude.ai/artifact/Y9eRHftqRJetjqDWbEdnV5`
