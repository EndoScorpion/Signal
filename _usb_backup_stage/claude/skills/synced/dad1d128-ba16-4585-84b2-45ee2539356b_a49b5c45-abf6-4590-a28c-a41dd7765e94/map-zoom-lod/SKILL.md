---
name: "map-zoom-lod"
description: "Use when adding or changing map layers, labels, roads or text on the Florida job-tracker map so detail, sizes and strokes adapt to zoom level."
---

# Map zoom level-of-detail (LOD) rules

Apply these whenever a map layer, label, road or icon is added to the job-tracker map.

## Zoom model
- Zoom is done through the SVG viewBox. zoom = 340 / viewBoxWidth (100% = 1, max about 6 = 600%).
- ppu (pixels per unit) = min(rect.width/vbW, rect.height/vbH). Text px size in map units = px / ppu.
- Page CSS forces font-size/font-family with !important, so set overlay text with style.setProperty('font-size', px/ppu + 'px', 'important').

## Three tiers
- Tier 1, 100-250%: interstates, large towns (cyan), bold labels, county outlines only. No ZIPs.
- Tier 2, 250-500%: medium towns (gold), US and state routes with route labels, county names in Times New Roman, text at least +2 sizes larger than the base.
- Tier 3, 500%+: small towns (pale), ZIP codes and ZIP zones, secondary roads, terrain notes. Hide overlapping labels (the overlap test must report 0).

## Scaling rules
- Strokes, dot radii and icons shrink with zoom: k = zoom^-1.1, exposed as the CSS var --ovk on the svg. Use calc(Npx * var(--ovk,1)) in CSS for rings and borders (for example rect.ov-score and the .mlbl.fair .mlbox border).
- Labels get rebuilt, so scaling that only runs when counts change can miss them. Prefer CSS vars over one-off JS.
- Keep new groups out of the generic stroke scaler when they set their own sizes (#ovCty, #ovZip, #ovRoads, #ovTowns, #ovZipB, #ovTerr, #ovDefs).

## Data and performance
- Use simplified geometry (Douglas-Peucker about 0.004 degrees), clipped to the Florida bbox. Roads come from Natural Earth 10m roads; counties from us-atlas.
- Add data in small chunks. Never paste a huge coordinate list into chat or the page at once.

## UI
- Label background opacity defaults to 50% and is user-changeable.
- The colour popup (button in the Map overlays panel) has a field dropdown, a colour picker and an opacity slider. Register any new colourable element in the field list (colorS snippet).
- Never remove existing layers, panels or features without asking.
- Test with Playwright: overlap 0, 0 page errors, job count unchanged.