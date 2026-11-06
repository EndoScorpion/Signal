const CACHE = 'claude-local-v1';
const STATIC = ['/', '/index.html', '/app.js', '/style.css', '/manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // Network-first for board.json and API calls
  if (url.pathname.includes('board.json') || url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request).catch(() => caches.match(e.request))
    );
    return;
  }
  // Cache-first for static assets
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).then(res => {
      if (res.ok) {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
      }
      return res;
    }))
  );
});

// Background sync for board.json
self.addEventListener('sync', e => {
  if (e.tag === 'sync-board') {
    e.waitUntil(syncBoard());
  }
});

async function syncBoard() {
  try {
    const r = await fetch('https://raw.githubusercontent.com/EndoScorpion/signal-board/main/board.json');
    if (r.ok) {
      const data = await r.json();
      const c = await caches.open(CACHE);
      c.put('/cached-board.json', new Response(JSON.stringify(data)));
    }
  } catch {}
}
