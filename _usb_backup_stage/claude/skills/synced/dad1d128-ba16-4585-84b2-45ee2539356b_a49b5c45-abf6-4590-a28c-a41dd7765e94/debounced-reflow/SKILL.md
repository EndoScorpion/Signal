---
name: "debounced-reflow"
description: "Use when handling resize, drag or slider events that trigger layout/geometry recalculation in single-file HTML apps."
---

# Debounced Reflow

## Rules
1. Never run layout recalculation continuously from rapid events (resize, scroll, input sliders, MutationObserver). Wrap the handler in a debounce of about 150ms (120-200ms is fine) so heavy math runs once after the user stops.
2. While dragging, update only the dragged element (cheap, direct attribute/transform change, ideally via requestAnimationFrame). Do the full re-layout once on pointer up.
3. Guard observers: ignore your own mutations (flag or attribute filter), and never let a layout pass trigger another layout pass (re-entrancy flag).
4. Cap background watchdogs (interval 1.5-2s, limited repair count) and pause them during user interaction.
5. Persist only the settled result.

## Blueprint
```js
function debounce(fn, ms = 150) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
let busy = false;
const relayout = debounce(() => { if (busy) return; busy = true; try { layoutAll(); } finally { busy = false; } });
addEventListener('resize', relayout);
slider.addEventListener('input', relayout);
```