---
name: "sandbox-map-rendering"
description: "Use when asked to render an interactive map (markers, popups, overlays) in the sandbox or an artifact with Leaflet.js and OpenStreetMap, no API keys."
---

# Sandbox Map Rendering

Render interactive maps with plain HTML5 + Leaflet.js + OpenStreetMap tiles. No API keys, one self-contained file.

## 1. Map CDN and dependency rules
- NEVER use a bare `https://unpkg.com` base URL (it loads nothing). Always pin the version and use the full production file path.
- Standard injection (Leaflet 1.9.4):
  - `<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>`
  - `<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>`
- Vanilla HTML/CSS/JS, single file, OSM tiles (no key).
- Give the map container an explicit height (100vh or fixed px); a zero-height div renders nothing.

## 2. Dynamic refitting and event triggers
- Bind a throttled `resize` listener on window.
- Check the instance exists before updating: `if (mapInstance) { mapInstance.invalidateSize({animate:false}); }`
- Call invalidateSize right after init, then at about 100ms, 500ms and 1500ms (sandbox paint timing).
- For UIs with draggable or resizable floating panels, call invalidateSize on every panel resize end (ResizeObserver on the container) so the map never collapses or gets cut off.
- Size the container from its own panel rect, not from innerHeight alone.

## 3. Sandboxed environment fallback protocol
- Published sandbox viewports or enterprise iframes may enforce a strict CSP that blocks external tile hosts (e.g. OpenStreetMap) or scripts.
- Always include an inline-SVG fallback map in the same file. If Leaflet is missing or no tile loads within 2500ms (no `tileload` event, or `window.L` undefined), hide the Leaflet container and show the static SVG map (lon/lat to x/y projection, outline, dots, labels; Natural Earth geojson converted to SVG paths for land and water).
- Say which mode was used.

## Boilerplate (map_sandbox.html)
```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sandbox Map Renderer</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<style>html,body{margin:0;width:100%;height:100%;overflow:hidden;font-family:system-ui,sans-serif}#map{width:100%;height:100%}#fallback{display:none;width:100%;height:100%}</style>
</head><body>
<div id="map"></div>
<svg id="fallback" viewBox="0 0 340 300" preserveAspectRatio="xMidYMid meet"><!-- static SVG map here --></svg>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
var mapInstance=null,tilesOk=false;
function useFallback(){document.getElementById('map').style.display='none';document.getElementById('fallback').style.display='block';}
if(window.L){
  mapInstance=L.map('map').setView([30.3322,-81.6557],7);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'}).on('tileload',function(){tilesOk=true}).addTo(mapInstance);
  L.marker([30.3322,-81.6557]).addTo(mapInstance).bindPopup('Map active');
}else useFallback();
function repair(){if(mapInstance){mapInstance.invalidateSize({animate:false});}}
[0,100,500,1500].forEach(function(t){setTimeout(repair,t)});
var rt;addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(repair,100)});
setTimeout(function(){if(!tilesOk)useFallback()},2500);
</script></body></html>
```

## Notes
- Respect OSM tile usage policy: attribution always shown, no heavy bulk tile loading.
- For job maps keep dots clickable with popups and keep labels from overlapping.