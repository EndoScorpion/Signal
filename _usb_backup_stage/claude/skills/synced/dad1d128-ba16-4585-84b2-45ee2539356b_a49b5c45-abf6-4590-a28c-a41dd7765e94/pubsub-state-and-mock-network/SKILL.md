---
name: "pubsub-state-and-mock-network"
description: "Use when separating data logic from UI render code in single-file apps, or when testing loading/error states with a fake network layer."
---

# PubSub Micro-State + Mock Latency Gate

## PubSub core
1. Widgets never mutate data directly. They `publish('action:name', payload)`.
2. One state engine subscribes, does the math, updates the register, then publishes `state:changed`.
3. Renderers (SVG, labels, ledger, counters) subscribe to `state:changed` and repaint; no calculation inside click handlers.
4. Keep the bus tiny (Map of arrays), with `subscribe` returning an unsubscribe function. Debounce repaints (see debounced-reflow).

```js
const bus = { h: new Map(), on(t, f){ (this.h.get(t) || this.h.set(t, []).get(t)).push(f); return () => this.h.set(t, this.h.get(t).filter(x => x !== f)); }, emit(t, p){ (this.h.get(t) || []).forEach(f => f(p)); } };
bus.on('node:moved', ({id, x, y}) => { engine.move(id, x, y); bus.emit('state:changed'); });
bus.on('state:changed', () => render());
```

## Mock latency gate (testing only)
1. Wrap the data fetch in a Promise with a random 800-2000ms delay.
2. In about 15% of calls reject with a `500 Server Error` or `429 Too Many Requests` object so loading skeletons, retry/backoff and toast alerts get exercised.
3. Label it clearly as a MOCK in the UI and console, make it switchable with a flag, and never present mock results as real data.
4. On 429 back off (for example 2x delay up to a cap); on 500 show a toast and keep the last good data.

```js
const mockFetch = (data) => new Promise((res, rej) => setTimeout(() => {
  const r = Math.random();
  if (r < 0.075) rej({ status: 500 }); else if (r < 0.15) rej({ status: 429 }); else res(data);
}, 800 + Math.random() * 1200));
```