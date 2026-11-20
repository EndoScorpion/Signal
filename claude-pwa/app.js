'use strict';

const BOARD_URL = 'https://raw.githubusercontent.com/EndoScorpion/signal-board/main/board.json';
const BOARD_LOCAL = 'http://10.30.30.80:7861/board';

let isOnline = navigator.onLine;
let currentView = 'board';

// ── Service Worker ──────────────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').then(reg => {
    reg.addEventListener('updatefound', () => log('sys', 'SW updating…'));
  });
}

// ── Routing ──────────────────────────────────────────────────────────────────
function switchView(name) {
  currentView = name;
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.getElementById(name + '-view').classList.add('active');
  document.querySelector(`[data-view="${name}"]`).classList.add('active');
  if (name === 'board') loadBoard();
  if (name === 'files') loadFiles();
}

document.querySelectorAll('[data-view]').forEach(btn =>
  btn.addEventListener('click', () => switchView(btn.dataset.view))
);

// ── Online status ────────────────────────────────────────────────────────────
function updateOnlineStatus() {
  isOnline = navigator.onLine;
  const dot = document.getElementById('status-dot');
  dot.className = 'status-dot ' + (isOnline ? 'online' : '');
  document.getElementById('status-text').textContent = isOnline ? 'Online' : 'Offline';
}
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
updateOnlineStatus();

// ── Board ────────────────────────────────────────────────────────────────────
async function loadBoard() {
  const el = document.getElementById('board-content');
  el.textContent = 'Loading…';

  let data = null;

  // Try local board first (faster)
  try {
    const r = await fetch(BOARD_LOCAL, { signal: AbortSignal.timeout(1500) });
    if (r.ok) data = await r.json();
  } catch {}

  // Fallback to GitHub
  if (!data && isOnline) {
    try {
      const r = await fetch(BOARD_URL, { signal: AbortSignal.timeout(5000) });
      if (r.ok) data = await r.json();
    } catch {}
  }

  // Fallback to cache
  if (!data) {
    try {
      const c = await caches.open('claude-local-v1');
      const r = await c.match('/cached-board.json');
      if (r) data = await r.json();
    } catch {}
  }

  if (data) {
    el.textContent = JSON.stringify(data, null, 2);
    localStorage.setItem('lastBoard', JSON.stringify({ data, ts: Date.now() }));
  } else {
    const cached = localStorage.getItem('lastBoard');
    if (cached) {
      const { data: d, ts } = JSON.parse(cached);
      el.textContent = JSON.stringify(d, null, 2);
      el.textContent += '\n\n[cached ' + Math.round((Date.now() - ts) / 60000) + 'm ago]';
    } else {
      el.textContent = 'Board unavailable (offline + no cache)';
    }
  }
}

document.getElementById('refresh-board').addEventListener('click', loadBoard);

// ── Files ────────────────────────────────────────────────────────────────────
const FILE_SHARE_ENDPOINT = 'http://localhost:8765';

async function loadFiles() {
  const container = document.getElementById('files-list');
  container.innerHTML = '<div style="color:var(--muted);padding:10px">Scanning…</div>';

  let files = [];
  try {
    const r = await fetch(FILE_SHARE_ENDPOINT + '/list', { signal: AbortSignal.timeout(2000) });
    if (r.ok) files = await r.json();
  } catch {
    // Try cached file list
    const cached = localStorage.getItem('cachedFiles');
    if (cached) files = JSON.parse(cached);
  }

  if (!files.length) {
    container.innerHTML = `
      <div class="board-card">
        <h3>File share server not running</h3>
        <pre>Start it with:\npython -m http.server 8765 --directory C:\\Users\\endos\\Signal</pre>
        <div style="margin-top:8px;font-size:12px;color:var(--muted)">Or run share.ps1</div>
      </div>`;
    return;
  }

  localStorage.setItem('cachedFiles', JSON.stringify(files));
  container.innerHTML = '';
  files.forEach(f => {
    const row = document.createElement('div');
    row.className = 'file-row';
    row.innerHTML = `
      <span class="fname">${f.name}</span>
      <span class="fsize">${fmtSize(f.size)}</span>
      <button onclick="downloadFile('${f.name}')">↓</button>`;
    container.appendChild(row);
  });
}

async function downloadFile(name) {
  try {
    const r = await fetch(FILE_SHARE_ENDPOINT + '/files/' + encodeURIComponent(name));
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const blob = await r.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
  } catch (e) {
    alert('Download failed: ' + e.message);
  }
}
window.downloadFile = downloadFile;

function fmtSize(bytes) {
  if (!bytes) return '';
  const units = ['B','KB','MB','GB'];
  let i = 0;
  while (bytes > 1024 && i < 3) { bytes /= 1024; i++; }
  return bytes.toFixed(1) + units[i];
}

// ── CLI ────────────────────────────────────────────────────────────────────────
const COMMANDS = {
  help: () => [
    'Available commands:',
    '  board          — refresh board.json',
    '  status         — online/offline status',
    '  cache list     — show cached items',
    '  cache clear    — clear all cached data',
    '  sync           — trigger background sync',
    '  open claude    — open claude.ai in app',
    '  open files     — go to files view',
    '  version        — show app version',
    '  clear          — clear terminal',
  ].join('\n'),

  status: () => `Online: ${navigator.onLine}\nSW: ${'serviceWorker' in navigator ? 'active' : 'none'}\nStorage: ${navigator.storage ? 'available' : 'none'}`,

  version: () => 'Claude Local PWA v1.0.0',

  board: async () => {
    await loadBoard();
    return 'Board refreshed';
  },

  sync: () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.ready.then(reg => {
        if (reg.sync) reg.sync.register('sync-board');
      });
    }
    return 'Sync triggered';
  },

  'cache list': async () => {
    const keys = await caches.keys();
    const items = [];
    for (const k of keys) {
      const c = await caches.open(k);
      const reqs = await c.keys();
      items.push(`${k}: ${reqs.length} items`);
    }
    return items.join('\n') || 'No cache';
  },

  'cache clear': async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => caches.delete(k)));
    localStorage.clear();
    return `Cleared ${keys.length} caches`;
  },

  'open claude': () => {
    switchView('claude');
    return 'Opening Claude…';
  },

  'open files': () => {
    switchView('files');
    return 'Opening files…';
  },

  clear: () => { clearCLI(); return null; }
};

const history = [];
let histIdx = -1;

function log(type, text) {
  const out = document.getElementById('cli-output');
  const line = document.createElement('div');
  line.className = 'cli-line ' + type;
  line.textContent = (type === 'cmd' ? '$ ' : '') + text;
  out.appendChild(line);
  out.scrollTop = out.scrollHeight;
}

function clearCLI() {
  document.getElementById('cli-output').innerHTML = '';
}

async function runCmd(raw) {
  const cmd = raw.trim();
  if (!cmd) return;
  history.unshift(cmd);
  histIdx = -1;
  log('cmd', cmd);

  const handler = COMMANDS[cmd] || COMMANDS[cmd.toLowerCase()];
  if (handler) {
    try {
      const result = await handler();
      if (result) log('out', result);
    } catch (e) {
      log('err', e.message);
    }
  } else {
    log('err', `Unknown command: ${cmd}. Type 'help' for list.`);
  }
}

const input = document.getElementById('cli-input');
input.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    runCmd(input.value);
    input.value = '';
  } else if (e.key === 'ArrowUp') {
    histIdx = Math.min(histIdx + 1, history.length - 1);
    input.value = history[histIdx] || '';
    e.preventDefault();
  } else if (e.key === 'ArrowDown') {
    histIdx = Math.max(histIdx - 1, -1);
    input.value = histIdx >= 0 ? history[histIdx] : '';
    e.preventDefault();
  }
});

// Auto-focus CLI input when CLI view active
document.querySelector('[data-view="cli"]').addEventListener('click', () =>
  setTimeout(() => input.focus(), 50)
);

// ── Claude iframe ────────────────────────────────────────────────────────────
document.getElementById('open-claude-btn').addEventListener('click', () => {
  document.getElementById('claude-frame').src = 'https://claude.ai';
});

// ── Init ─────────────────────────────────────────────────────────────────────
log('sys', 'Claude Local PWA ready. Type "help" for commands.');
log('sys', 'Network: ' + (navigator.onLine ? 'online' : 'offline'));
switchView('board');
