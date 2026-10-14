---
name: "state-history-undo-redo"
description: "Use when a UI lets users drag, edit or filter data and needs undo/redo (for example label positions on a map)."
---

# State History Stack (Undo / Redo)

## Rules
1. Treat the editable state (node coordinates, filters, settings) as an immutable timeline: after each completed action (drag end, filter change, slider release) push a deep snapshot (`structuredClone` or JSON copy) onto `pastStates`; clear `futureStates`.
2. Cap the stack (for example 50 snapshots) to protect memory; drop the oldest.
3. `executeUndo()` pops the last snapshot, pushes the current state to `futureStates`, applies the popped state, then repaints. `executeRedo()` does the reverse.
4. Never push during a drag, only when it ends. Never push when nothing changed (compare JSON).
5. Buttons and Ctrl+Z / Ctrl+Y (Ctrl+Shift+Z) call the same two functions; disable the buttons when a stack is empty.
6. Persist the current state (try/catch localStorage), not the entire history, unless asked.

## Blueprint
```js
const past = [], future = []; const MAX = 50;
const snap = () => JSON.stringify(state);
function commit() { const s = snap(); if (past[past.length-1] === s) return; past.push(s); if (past.length > MAX) past.shift(); future.length = 0; }
function executeUndo() { if (past.length < 2) return; future.push(past.pop()); state = JSON.parse(past[past.length-1]); render(); }
function executeRedo() { if (!future.length) return; const s = future.pop(); past.push(s); state = JSON.parse(s); render(); }
```