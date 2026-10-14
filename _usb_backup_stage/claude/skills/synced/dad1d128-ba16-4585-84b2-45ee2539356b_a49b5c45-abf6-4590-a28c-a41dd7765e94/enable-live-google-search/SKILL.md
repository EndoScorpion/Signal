---
name: enable-live-google-search
description: >
  Enable live Google search in chat and live preview. Use this skill when the
  user wants to: (1) search the web and display results inside a Claude artifact
  or visualizer, (2) build an artifact dashboard with live/real-time data pulled
  from search, (3) wire up a search bar in an HTML/React artifact that queries
  real web data, (4) fetch current news, prices, or information and render it
  visually. Triggers: "live search", "google search in artifact", "search the
  web and show results", "live data in dashboard", "real-time search widget",
  "search inside the preview", "add live search to this".
---

# Live Google Search — Chat + Artifact Integration

## How search actually works in Claude

**Critical constraint**: Artifact iframes run in a strict CSP sandbox. Direct
outbound HTTP calls to Google or any external search API from inside an artifact
are blocked — this cannot be bypassed from within the artifact itself.

**What actually works**:

| Method | Where search runs | Where results appear |
|---|---|---|
| Claude `web_search` tool | Chat (Claude's host) | Injected into artifact as data |
| MCP connector (e.g. Brave Search) | Claude's host | Injected into artifact as data |
| `sendPrompt()` bridge | User triggers from artifact → Claude searches → re-renders artifact | Artifact re-rendered with new data |

## Workflow — Search + Render to Artifact

### Pattern A: Claude searches, artifact displays (one-shot)

1. User asks for current data (e.g. "show me today's BTC news in a dashboard")
2. Claude calls `web_search` with relevant queries
3. Claude extracts structured results (title, url, snippet, date)
4. Claude generates an HTML/React artifact with the data hardcoded as a JS array
5. Artifact renders it as cards, table, or chart — no live network calls needed

### Pattern B: Interactive search bar via sendPrompt() bridge

The artifact renders a search input. When user submits:
1. Artifact calls `sendPrompt("search: <query>")` — sends to Claude chat
2. Claude receives it, calls `web_search`, gets results
3. Claude re-renders the artifact with fresh data injected

Template for the artifact search bar:

```html
<input id="q" placeholder="Search..." />
<button onclick="doSearch()">Search</button>
<div id="results"></div>

<script>
function doSearch() {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  // Bridge: sends to Claude chat, Claude searches and re-renders
  if (typeof sendPrompt === 'function') {
    sendPrompt('Live search request: ' + q);
  } else {
    document.getElementById('results').innerHTML =
      '<p style="color:#888">Open in Claude to enable live search.</p>';
  }
}
</script>
```

### Pattern C: MCP connector (Brave Search, Tavily, etc.)

If user has a search MCP connected:
1. Check available MCP tools with `tool_search("search")`
2. Call the MCP search tool directly
3. Inject results into artifact

## Artifact data injection pattern

When Claude has search results, inject them as a JS const in the artifact:

```html
<script>
const SEARCH_RESULTS = [
  { title: "...", url: "...", snippet: "...", date: "..." },
  // ...
];
</script>
```

Then the artifact JS reads `SEARCH_RESULTS` and renders without any network calls.

## What to tell the user

Always be transparent:
- Artifacts cannot directly call Google — searches run through Claude
- For truly live/auto-refreshing data, an MCP connector is needed
- The `sendPrompt()` bridge is the most interactive option available natively
- For Trade Signals: crypto prices come from Binance WebSocket (already wired) —
  not search — so "live data" there means WSS, not Google

## Response format

When user asks to add live search to an artifact:
1. Clarify which pattern fits their use case (A, B, or C)
2. Run `web_search` for any initial data they need right now
3. Build the artifact with data injected or `sendPrompt()` bridge wired
4. Note: "Search runs through Claude — type a query and I'll fetch fresh results"
