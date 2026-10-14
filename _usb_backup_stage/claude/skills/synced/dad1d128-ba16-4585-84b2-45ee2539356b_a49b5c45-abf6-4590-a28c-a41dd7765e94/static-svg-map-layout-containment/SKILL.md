---
name: "static-svg-map-layout-containment"
description: "Use when building or fixing maps/charts/panels: prefer static inline SVG, size by container math not pixel listeners, keep everything in one offline HTML file."
---

# Static SVG Map + Layout Containment

## 1. Static visuals first
- Default to inline SVG with a fixed viewBox and a simple lon/lat to x/y projection. Add JavaScript (pan/zoom, labels) only on top of that.
- Use Leaflet/OSM only when real tiles are required and external hosts are allowed (see sandbox-map-rendering).

## 2. Resizing and layout math
- Size the SVG from its container: `width:100%; height:100%; preserveAspectRatio="xMidYMid meet"`, and give the container a definite height (flex: 1 1 0 with min-height:0, or calc()).
- Compute heights from the panel's own rect (panel bottom minus view top), never from `innerHeight` alone: an iframe's innerHeight can differ from the panel's real size.
- Use CSS variables / calc()/clamp() for sizes; use one debounced ResizeObserver, not many raw pixel listeners.
- Reserve space for fixed bars (bottom toolbar) when positioning panels.

## 3. Self-check and repair on load
- Check: panel wide enough, SVG height equals its window height, no scrollHeight > clientHeight at zoom 1, bottom not under a toolbar, tiles not clipped.
- Repair: widen/move the panel, set view height from the panel rect, SVG height 100%, re-run; retry up to 3 passes, then keep a quiet watchdog.
- Log every check and repair to a minimized info-button dock.

## 4. Offline containment
- Ship one self-contained HTML file (inline CSS/JS, no required network). State in memory or try/catch localStorage.
- Offer a .txt backup of the key code.