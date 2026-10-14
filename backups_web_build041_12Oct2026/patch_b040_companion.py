import re
SRC="/root/.claude/projects/-home-claude/7eb190e1-037f-5a0c-b656-44bb6c5bb081/tool-results/artifact-1d8df881-1791487233-b40b.html"
DST="/tmp/claude-0/-home-claude/7eb190e1-037f-5a0c-b656-44bb6c5bb081/scratchpad/signal-live-companion-b040.html"
s=open(SRC,encoding="utf-8").read()

def rep1(old,new):
    global s
    n=s.count(old)
    assert n==1, ("count",n,old[:80])
    s=s.replace(old,lambda_new(new),1)
def lambda_new(x): return x

# 1. build label + title (global banner/tag replace; changelog lines use a different format so are untouched)
s=s.replace("<title>Signal Live Companion v0.01d build 039 (Copy) (Copy) (Copy)</title>","<title>Signal Live Companion v0.01d build 040 | 8 Oct 2026</title>",1)
s=s.replace("build 039 | 2026-10-04 EDT","build 040 | 8 Oct 2026 EDT")

# 2. CSS: minimize toggle for metals/dividends card + progress bar
css='''/* build 040: minimize toggle + progress bar */
#dmDet>summary{cursor:pointer;padding:4px 0;list-style:none;color:var(--ok);font-weight:700}
#dmDet>summary::-webkit-details-marker{display:none}
#dmDet>summary::before{content:"+ ";color:#39ff14;font-weight:700}
#dmDet[open]>summary::before{content:"\\2212  ";color:#d29922}
#hxRec{border-left:3px solid #39ff14;padding:4px 8px;background:#39ff1410;border-radius:4px}
'''
rep1("/* history preview modal */", css+"/* history preview modal */")

# 3. history card: recommendation line + loading bar under the size summary
rep1('<div class="mu" id="hxSum"></div>',
 '<div class="mu" id="hxSum"></div><div class="mu" id="hxRec" style="font-size:12px;margin:6px 0;line-height:1.5"></div>'
 '<div id="hxBarWrap" style="display:none;height:12px;border:1px solid #39ff14;border-radius:6px;overflow:hidden"><div id="hxBarFill" style="height:100%;width:0;background:#39ff14;transition:width .25s"></div></div>'
 '<div class="mu" id="hxBarTxt" style="font-size:11px;min-height:14px;margin-bottom:4px"></div>')

# 4. metals + dividends panel starts minimized
rep1('<h2>Dividends &amp; Metals only &mdash; starts paused</h2><div id="dmBody"></div>',
 '<details id="dmDet"><summary><b>Dividends &amp; Metals only</b> &mdash; minimized, starts paused</summary><div id="dmBody" style="margin-top:6px"></div></details>')

# 5. backtest info line (symbols, timeframe, dates, sizes, run estimate)
rep1('<div class="card"><h2>Light backtest (latest run, 4 main symbols, 0.1% cost per trade) - highest win rate first</h2><table id="tbl">',
 '<div class="card"><h2>Light backtest (latest run, 4 main symbols, 0.1% cost per trade) - highest win rate first</h2><div class="mu" id="btInfo" style="font-size:12px;margin:0 0 6px;line-height:1.5"></div><table id="tbl">')

# 6. loader bar: stream the MarketWatch file read with progress
rep1('st("Reading the MarketWatch data file (~7 MB, one time; released after 3 min idle)...");fetch("files/marketwatch_v0.01d.html").then(function(r){return r.text()})',
 'st("Reading the MarketWatch data file (~7 MB, one time; released after 3 min idle)...");bar(0,"Starting read of MarketWatch data");fetch("files/marketwatch_v0.01d.html").then(readProg)')
rep1('st("Catalog ready: "+HX.cat.length+" series.");cb()','bar(null);st("Catalog ready: "+HX.cat.length+" series.");cb()')
rep1('}).catch(function(e){st("Failed to read data: "+e.message)})}','}).catch(function(e){bar(null);st("Failed to read data: "+e.message)})}')

helpers='''function bar(p,t){var w=g("hxBarWrap"),f=g("hxBarFill"),x=g("hxBarTxt");if(!w)return;if(p==null){w.style.display="none";if(x)x.textContent="";return}w.style.display="block";f.style.width=Math.max(0,Math.min(100,p))+"%";if(x)x.textContent=t||""}
function readProg(r){var len=+r.headers.get("content-length")||7e6;if(!r.body||!r.body.getReader)return r.text();var rd=r.body.getReader(),dec=new TextDecoder(),parts=[],got=0;function pump(){return rd.read().then(function(x){if(x.done){parts.push(dec.decode());return parts.join("")}parts.push(dec.decode(x.value,{stream:true}));got+=x.value.length;bar(Math.min(99,got/len*100),"Reading MarketWatch data: "+(got/1048576).toFixed(1)+" MB");return pump()})}return pump()}
'''
rep1("function load(cb){", helpers+"function load(cb){")

# 7. smart estimates + recommendations (replaces sum)
newsum='''function est(ds,fmt){var rows=0,ser=0,sy={};ds.forEach(function(d){var q=rng(d);rows+=q[1]-q[0];sy[d.id]=1;ser++});var bpr=fmt==="txt"?66:62,small=window.innerWidth<700,MB=small?2:5,CH=Math.max(5000,Math.min(150000,Math.floor(MB*1048576/bpr)));return{rows:rows,bytes:rows*bpr,ser:ser,syms:Object.keys(sy).length,CH:CH,ch:Math.max(1,Math.ceil(rows/CH)),secs:Math.max(1,Math.round(rows/60000)+(HX.raw?0:4)),small:small}}
function sz(b){return b>=1048576?(b/1048576).toFixed(1)+" MB":Math.max(1,Math.round(b/1024))+" KB"}
function rec(e){if(!e.rows)return"Tick a symbol or press a row button to see size, chapters and a start estimate.";var s="Size ~"+sz(e.bytes)+" as .csv | "+e.syms+" symbols, "+e.ser+" series | start: "+(HX.raw?"data already in memory":"reads the MarketWatch file once (~7 MB, a few seconds)")+" | build ~"+e.secs+" s.<br>";
if(e.ch===1)return s+"<b>Recommendation:</b> small, one file is fine.";
if(e.bytes<20*1048576)return s+"<b>Recommendation:</b> medium: saves as "+e.ch+" chapters of about "+e.CH.toLocaleString()+" rows (each ~"+sz(e.CH*62)+"). Keep this tab open until the bar finishes.";
return s+"<b>Recommendation:</b> large: "+e.ch+" chapters of about "+e.CH.toLocaleString()+" rows. To go faster or lighter: narrow Earliest/Latest, set Newest bars per series, or download one symbol at a time."+(e.small?" Phone detected: 2 MB chapters.":"")}
function sum(){if(!HX.cat)return;var ds=pick(function(d){return HX.sel[d.id]}),e=est(ds,"csv");g("hxSum").textContent=e.syms+" symbols ticked | "+ds.length+" series | about "+e.rows.toLocaleString()+" rows | ~"+sz(e.bytes)+" as .csv"+(e.rows>300000?"  (large: may be slow)":"");g("hxRec").innerHTML=rec(e)}'''
s,n=re.subn(r'^function sum\(\)\{.*$', lambda m: newsum, s, count=1, flags=re.M); assert n==1,"sum"

# 8. per-row and per-group size + start estimates
rep1("' &rarr; '+fmtD(t1)+'</span><button class=\"gb sm\" data-a=\"rdl\"",
 "' &rarr; '+fmtD(t1)+' &middot; ~'+sz(L.reduce(function(a,d){return a+d.n},0)*62)+' &middot; start ~'+Math.max(1,Math.round(L.reduce(function(a,d){return a+d.n},0)/60000))+' s</span><button class=\"gb sm\" data-a=\"rdl\"")
rep1("' symbols, '+ds.length+' series, '+tot.toLocaleString()+' bars</summary>",
 "' symbols, '+ds.length+' series, '+tot.toLocaleString()+' bars, ~'+sz(tot*62)+'</summary>")

# 9. chapter-based saving with progress (replaces dl)
newdl='''function saveChapters(ds,fmt,label,cb){var e=est(ds,fmt),csv=fmt==="csv",SEP=csv?",":"\\t",mt=csv?"text/csv":"text/plain",H=["source","symbol","timeframe","timestamp_ms","time_utc","open","high","low","close","dividend"],plan=ds.map(function(d){var q=rng(d);return{d:d,lo:q[0],hi:q[1]}}).filter(function(p){return p.hi>p.lo}),total=plan.reduce(function(a,p){return a+p.hi-p.lo},0),N=Math.max(1,Math.ceil(total/e.CH)),ci=0,si=0,ri=-1,done=0,f=g("hxFrom").value,t=g("hxTo").value;
 var pad=function(x){return (x<10?"0":"")+x};
 function next(){if(si>=plan.length){bar(100,"Done: "+done.toLocaleString()+" rows in "+ci+" chapter(s)");setTimeout(function(){bar(null)},2500);return cb&&cb(done,ci)}
  ci++;var o=[],n=0;o.push(csv?H.join(SEP):"# Signal Live Companion history export | "+(window.slcBuildGet?window.slcBuildGet():"")+" | "+new Date().toISOString()+" | chapter "+ci+" of "+N);if(!csv)o.push("# columns: "+H.join("\\t"));
  while(si<plan.length&&n<e.CH){var p=plan[si];if(ri<0){ri=p.lo;if(!csv)o.push("## "+p.d.sym+" "+TFN[p.d.tf]+" | "+(p.hi-p.lo)+" rows | "+p.d.src)}
   var end=Math.min(p.hi,ri+(e.CH-n)),before=ri;for(;ri<end;ri++){o.push([p.d.src,p.d.sym,TFN[p.d.tf],p.d.T[ri],new Date(p.d.T[ri]).toISOString()].concat(rowAt(p.d,ri)).join(SEP))}
   n+=ri-before;if(ri>=p.hi){si++;ri=-1}}
  done+=n;var name=window.slcFname((label+"_ch"+pad(ci)+"of"+pad(N)+"_"+(f||"first")+"_to_"+(t||"last")).replace(/[^A-Za-z0-9_\\-]/g,"_"),"."+fmt);
  bar(done/total*100,"Chapter "+ci+" of "+N+" built: "+done.toLocaleString()+" / "+total.toLocaleString()+" rows");st("Saving chapter "+ci+" of "+N+" ...");
  window.slcSave(name,o.join("\\n"),mt).then(function(){setTimeout(next,700)},function(err){bar(null);st("Save failed at chapter "+ci+": "+((err&&err.message)||err))})}
 next()}
function dl(ds,fmt,label){if(!ds.length){st("Nothing selected: tick a symbol (or use a row / group button).");return}load(function(){var mode=g("hxMode").value;if(mode==="sym"){var by={},ord=[];ds.forEach(function(d){if(!by[d.id]){by[d.id]=[];ord.push(d.id)}by[d.id].push(d)});var k=0,go=function(){if(k>=ord.length){st("Saved "+ord.length+" symbol files.");return}var id=ord[k++];saveChapters(by[id],fmt,"history_"+by[id][0].sym+"_"+by[id][0].src,function(rows,ch){st("Saved "+k+"/"+ord.length+": "+id+" ("+rows.toLocaleString()+" rows, "+ch+" chapter(s))");setTimeout(go,900)})};go()}else{saveChapters(ds,fmt,"history_"+label,function(rows,ch){st("Saved "+label+" ."+fmt+": "+rows.toLocaleString()+" rows, "+ds.length+" series, "+ch+" chapter(s)")})}})}'''
s,n=re.subn(r'^function dl\(ds,fmt,label\)\{.*$', lambda m: newdl, s, count=1, flags=re.M); assert n==1,"dl"

# 10. backtest info updater (every 3 s, read-only view of lastBars)
btjs='''function btSize(){var el=document.getElementById("btInfo");if(!el||!window.__slc)return;var B=window.__slc.bars()||{},ks=Object.keys(B);if(!ks.length){el.innerHTML="Backtest info appears after the first Start run: symbols, timeframe, dates, sizes and run estimate.";return}
 var bars=0,lo=Infinity,hi=-Infinity,syms=[];ks.forEach(function(k){var a=B[k]||[];bars+=a.length;syms.push(k+" "+a.length);a.forEach(function(x){var v=typeof x.t==="number"?x.t:Date.parse(x.t);if(isFinite(v)){if(v<lo)lo=v;if(v>hi)hi=v}})});
 var V=8,ms=Math.max(5,Math.round(bars*V/50000*1000)),kb=Math.max(1,Math.round(bars*V*0.02));
 el.innerHTML="<b>Backtest data:</b> "+ks.length+" symbols ("+syms.join(", ")+") | timeframe 1h | "+bars.toLocaleString()+" bars | "+(isFinite(lo)?new Date(lo).toISOString().slice(0,10)+" to "+new Date(hi).toISOString().slice(0,10):"dates n/a")+"<br><b>Sizes:</b> bars in memory ~"+sz(bars*80)+" | results ~"+kb+" KB | <b>start estimate:</b> instant once bars are in | <b>run estimate:</b> ~"+ms+" ms for "+V+" variants"}
setInterval(btSize,3000);'''
rep1("function render(){var box=g(\"hxBody\")", btjs+"\nfunction render(){var box=g(\"hxBody\")")

# 11. changelog entry (new build on top)
n_=s.count('["039","2026-10-04","EDT",'); assert n_==1, ("cl",n_)
s=s.replace('["039","2026-10-04","EDT",', '["040","8 Oct 2026","EDT","Metals + dividends panels minimized by default; history rows show size, date range and start estimate; recommendations for every download size; loading bars for data reads and saves; downloads split into chapters (5 MB, 2 MB on phones); backtest info line with symbols, timeframe, dates, sizes and run estimate"],["039","2026-10-04","EDT",',1)

open(DST,"w",encoding="utf-8").write(s)
print("ok", len(s))
