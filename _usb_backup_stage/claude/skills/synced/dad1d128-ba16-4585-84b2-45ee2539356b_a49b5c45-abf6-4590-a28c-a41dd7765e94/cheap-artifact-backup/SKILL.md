---
name: cheap-artifact-backup
description: >
  LOW COST (~500 tokens). Add debounced auto-save + status badge to any HTML
  artifact. Saves state to localStorage, restores on reload, shows Saved/Saving/
  Error badge. Use when "artifact keeps resetting", "save state in artifact",
  "auto-save", "artifact should remember settings".
---
## Core pattern
```js
var STORAGE_KEY = 'artifact_SLUG_state';
var saveTimer = null;

function saveState(state) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); showBadge('saved'); }
  catch(e) { showBadge('error'); }
}
function loadState() {
  try { var r=localStorage.getItem(STORAGE_KEY); return r?JSON.parse(r):null; } catch(e){return null;}
}
function scheduleSave(state) {
  showBadge('saving');
  clearTimeout(saveTimer);
  saveTimer = setTimeout(function(){ saveState(state); }, 800);
}
var BADGE={
  saved: {bg:'#0d1a10',color:'#3ecf5e',border:'#2a2',label:'Saved \u2713'},
  saving:{bg:'#1a140d',color:'#f2c400',border:'#a86',label:'Saving...'},
  error: {bg:'#1a0d0d',color:'#ef5350',border:'#522',label:'Save failed'}
};
function showBadge(type){
  var b=document.getElementById('backup-badge'),s=BADGE[type];
  if(!b||!s)return;
  b.style.background=s.bg;b.style.color=s.color;b.style.borderColor=s.border;
  b.querySelector('span').textContent=s.label;
}
```
## Badge HTML
```html
<div id="backup-badge" style="display:inline-flex;align-items:center;gap:5px;
  padding:3px 9px;border-radius:3px;font-size:10px;font-family:monospace;
  background:#0d1a10;color:#3ecf5e;border:1px solid #2a2;">
  <span>Saved ✓</span>
</div>
```
## Trade Signals state keys to save
`symbol, timeframe, chartMode, indicators[], maOverlays[], panelPos{left,top,w,h}, fontSizeTier, wssSymbol`
