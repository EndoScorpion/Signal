import re
SRC="/tmp/claude-0/-home-claude/7eb190e1-037f-5a0c-b656-44bb6c5bb081/scratchpad/mw/files/marketwatch_v0.01d.html"
DST="/tmp/claude-0/-home-claude/7eb190e1-037f-5a0c-b656-44bb6c5bb081/scratchpad/mw/marketwatch_v0.01d_build041.html"
s=open(SRC,encoding="utf-8").read()
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:90]); s=s.replace(old,new)

JG='''<script>
/* build 041 Job Guard: heavy jobs run one at a time, yield to the UI in small slices,
   check memory before starting and during work, auto-pause when memory is high, and offer Pause / Stop. */
window.JG=(function(){
 var S={job:null,t0:0,paused:false,stop:false,msg:"Idle. Heavy jobs run one at a time in small chunks."};
 function heap(){try{var m=performance.memory;if(!m)return null;return m.usedJSHeapSize/m.jsHeapSizeLimit*100}catch(e){return null}}
 function tick(ms){return new Promise(function(r){setTimeout(r,ms||0)})}
 function box(){var b=document.getElementById("jgBox");if(b)return b;
  b=document.createElement("div");b.id="jgBox";
  b.style.cssText="position:fixed;right:8px;bottom:8px;z-index:2147483600;background:#000;color:#39ff14;border:1px solid #39ff14;border-radius:6px;padding:6px 8px;font:11px/1.4 Consolas,monospace;max-width:320px;display:none";
  b.innerHTML='<div id="jgT"></div><div id="jgM" style="opacity:.9;margin-top:2px"></div><div style="margin-top:4px"><button id="jgP" style="font-size:11px">Pause</button> <button id="jgS" style="font-size:11px">Stop</button></div>';
  document.body.appendChild(b);
  document.getElementById("jgP").onclick=function(){S.paused=!S.paused;this.textContent=S.paused?"Resume":"Pause";paint()};
  document.getElementById("jgS").onclick=function(){S.stop=true;S.paused=false;paint()};
  return b}
 function paint(){try{var b=box(),h=heap(),busy=!!S.job;
   b.style.display=(busy||(h!=null&&h>70))?"block":"none";
   document.getElementById("jgT").innerHTML=(busy?"Job: <b>"+S.job+"</b> &middot; "+Math.round((Date.now()-S.t0)/1000)+" s"+(S.paused?" &middot; PAUSED":""):"Idle")+" &middot; memory "+(h==null?"n/a":h.toFixed(0)+"%")+(h!=null&&h>80?" <span style='color:#ff5252'>HIGH</span>":"");
   document.getElementById("jgM").textContent=S.msg}catch(e){}}
 function begin(name){
  if(S.job){S.msg="Busy: \\u201c"+S.job+"\\u201d is still running. Wait for it or press Stop. Two heavy jobs at once is what freezes the tab.";paint();return false}
  var h=heap();if(h!=null&&h>85){S.msg="Memory at "+h.toFixed(0)+"%. Close other tabs, or export one symbol or one timeframe at a time. Nothing was started.";paint();return false}
  S.job=name;S.t0=Date.now();S.stop=false;S.paused=false;
  S.msg="Started in small chunks. The page stays responsive; Pause or Stop any time.";paint();return true}
 function end(){S.job=null;S.paused=false;S.stop=false;S.msg="Finished. Keep this tab open until the last save finishes.";paint()}
 async function checkpoint(){
  for(;;){
   if(S.stop){S.msg="Stopped by you. Parts already saved are kept; the rest was skipped.";paint();throw "stopped"}
   var h=heap();
   if(S.paused||(h!=null&&h>88)){
    if(!S.paused){S.paused=true;S.msg="Auto-paused: memory "+h.toFixed(0)+"%. Close other tabs, then press Resume (or Stop).";var p=document.getElementById("jgP");if(p)p.textContent="Resume"}
    paint();await tick(400);continue}
   break}
  await tick(0);paint()}
 function pauseFor(bytes){var ms=Math.round(500+Math.min(4000,bytes/1048576*250));S.msg="Cool-down "+(ms/1000).toFixed(1)+" s before the next file, so memory can be released.";paint();return ms}
 function gate(name,fn){if(!begin(name))return;
  setTimeout(async function(){try{await checkpoint();fn()}catch(e){S.msg="Failed: "+((e&&e.message)||e);paint()}finally{end()}},60)}
 setInterval(paint,1000);
 return {begin:begin,end:end,checkpoint:checkpoint,gate:gate,pauseFor:pauseFor,heap:heap,
  stop:function(){S.stop=true;S.paused=false},busy:function(){return S.job},msg:function(){return S.msg},note:function(m){S.msg=m;paint()}}
})();
</script>
'''
# insert the guard right after <body ...>
m=re.search(r'<body[^>]*>',s); assert m
s=s[:m.end()]+"\n"+JG+s[m.end():]

# run(): gate start, release end, yield in slices, yield per series, checkpoint before each save, cool-down
rep('busy=true;stopF=false;var I=seriesInfo(S),parts=[]',
    'if(window.JG&&!JG.begin("History export "+fmt.toUpperCase()+(tr?" +trades":""))){stat(JG.msg(),null,"");return}busy=true;stopF=false;var I=seriesInfo(S),parts=[]')
rep('busy=false;refresh()}\nfunction getS(kind)','busy=false;if(window.JG)JG.end();refresh()}\nfunction getS(kind)')
rep('if(++li%12000===0){','if(++li%3000===0){if(window.JG)await JG.checkpoint();')
rep('var s=S[si],M=tr?marks(s.d,sel):[],L=lines(s,fmt,tr,sel,M);',
    'var s=S[si];if(window.JG)await JG.checkpoint();stat("Preparing "+s.id+" "+s.tf.toUpperCase()+" ("+(si+1)+"/"+S.length+")"+(tr?" with trade records":""),Math.round(si/S.length*40),"");var M=tr?marks(s.d,sel):[],L=lines(s,fmt,tr,sel,M);')
rep('var _t0=Date.now();await saveFile(nm,parts[k2]);','if(window.JG)await JG.checkpoint();var _t0=Date.now();await saveFile(nm,parts[k2]);')
rep('break}await nap(1200)}','break}await nap(window.JG?JG.pauseFor(parts[k2].length):1200)}')
rep('$("v01eSp").onclick=function(){stopF=true}','$("v01eSp").onclick=function(){stopF=true;if(window.JG)JG.stop()}')

# top-bar HTML export: run through the guard (memory check, yield a frame, Pause/Stop box)
rep("on(){ try{ var st0=stamp(),html=", "on(){ if(window.JG)JG.gate('HTML export',function(){ try{ var st0=stamp(),html=")
rep("_tbPop('HTML export failed',esc(e.message)); } };", "_tbPop('HTML export failed',esc(e.message)); } }); };")

open(DST,"w",encoding="utf-8").write(s)
print("ok",len(s))
