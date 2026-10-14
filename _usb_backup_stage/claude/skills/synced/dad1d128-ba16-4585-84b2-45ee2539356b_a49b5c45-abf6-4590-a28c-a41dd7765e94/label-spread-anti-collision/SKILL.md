---
name: "label-spread-anti-collision"
description: "Use when map or canvas text labels crowd or overlap: add a spread/padding slider and autofit that pushes labels apart without losing drag edits."
---

# Label Spread, Padding and Anti-Collision

1. Keep a pristine baseline copy of label positions (`baseline`). Never spread from the already-spread array, or repeated slider moves compound drift. Slider 0 restores baseline.
2. Spread slider (0-60px): work in pixel space, not percent. Run 3-5 passes; for each pair closer than the radius, push both apart along the line between them by (radius - dist)/2. Use a deterministic nudge when dist is 0. Clamp to the container (2%-94%).
3. For rectangular labels, test box overlap (width + padding) instead of centre distance, so wide names like Jacksonville don't collide.
4. Padding slider (4-16px) drives CSS variables (--label-padding-y, --label-padding-x = 1.5x). Re-run the spread after padding or scale changes, because box sizes changed.
5. Dragging a label updates both the live position and the baseline; re-run the spread on drop if the slider is above 0.
6. Undo/redo: snapshot before each mutation (cap 50), clear redo on new edits, resync baseline after undo/redo, reset the slider to 0.
7. Debounce vector/leader-line redraws (150ms). Never re-label dot elements that are already towns (exclude .tdot) or labels multiply on every repair.
8. Zoom: counter-scale dot radii and halos by about 1/zoom^0.85 so dots keep a sane on-screen size when the map is zoomed.
9. Verify with a check that counts overlaps, missing leader lines and labels out of bounds (target 0/0/0).