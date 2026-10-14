# Live Search Dashboard — Full Artifact Template

Use this when building a search-results dashboard artifact.
Claude searches → injects data → artifact renders.

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { background:#0b0c10; color:#ccc; font-family:monospace; margin:0; padding:16px; }
  h2   { color:#8f8; font-size:14px; margin:0 0 12px; }
  .search-bar { display:flex; gap:8px; margin-bottom:16px; }
  .search-bar input  { flex:1; background:#0d0f14; color:#ddd; border:1px solid #2a2e39;
                        border-radius:4px; padding:6px 10px; font-family:monospace; font-size:12px; }
  .search-bar button { background:#000; color:#3f3; border:1px solid #2a2; border-radius:4px;
                        padding:6px 14px; font-family:monospace; font-size:12px; cursor:pointer; }
  .result-card { background:#131722; border:1px solid #2a2e39; border-radius:5px;
                  padding:10px 14px; margin-bottom:10px; }
  .result-card a    { color:#9db4ff; font-size:13px; text-decoration:none; font-weight:bold; }
  .result-card a:hover { text-decoration:underline; }
  .result-card .snippet { color:#787b86; font-size:11px; margin-top:4px; }
  .result-card .date    { color:#3a3; font-size:10px; margin-top:3px; }
  .note { color:#555; font-size:10px; margin-top:12px; }
</style>
</head>
<body>

<h2>🔍 Live Search</h2>

<div class="search-bar">
  <input id="q" placeholder="Type a query and press Search..." />
  <button onclick="doSearch()">Search</button>
</div>

<div id="results"></div>
<div class="note" id="note"></div>

<script>
/* Injected by Claude after web_search — replace this array with real results */
const SEARCH_RESULTS = [
  {
    title: "Sample result — Claude will replace this with live data",
    url: "https://example.com",
    snippet: "When you submit a search query, Claude runs web_search and re-renders this artifact with real results.",
    date: ""
  }
];

function renderResults(results) {
  const el = document.getElementById('results');
  if (!results.length) {
    el.innerHTML = '<div class="result-card"><span class="snippet">No results found.</span></div>';
    return;
  }
  el.innerHTML = results.map(r => `
    <div class="result-card">
      <a href="${r.url}" target="_blank">${r.title}</a>
      <div class="snippet">${r.snippet}</div>
      ${r.date ? '<div class="date">' + r.date + '</div>' : ''}
    </div>
  `).join('');
}

function doSearch() {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  document.getElementById('note').textContent = 'Sending to Claude...';
  if (typeof sendPrompt === 'function') {
    sendPrompt('Live search request: ' + q);
  } else {
    document.getElementById('note').textContent =
      'sendPrompt not available — open this artifact in Claude to enable live search.';
  }
}

/* Render initial injected results on load */
renderResults(SEARCH_RESULTS);
document.getElementById('note').textContent =
  'Searches run through Claude • Submit a query above to fetch fresh results';
</script>

</body>
</html>
```

## How Claude fills in SEARCH_RESULTS

After receiving a `sendPrompt("Live search request: <query>")` message:

1. Call `web_search` with the query
2. Extract up to 8 results: `{ title, url, snippet, date }`
3. Re-render the artifact with the array replaced:

```javascript
const SEARCH_RESULTS = [
  { title: "...", url: "https://...", snippet: "...", date: "Aug 14 2026" },
  // ...
];
```
