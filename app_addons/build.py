b=open('companion_v0.01d_build036.html').read()
a3b=open('addon3b.html').read().strip();a5=open('addon5.html').read().strip();a4=open('addon4.html').read().strip()
a4b=a4.replace('#slcDockGrip{position:absolute;left:0;right:0;top:-13px;height:14px;','#slcDockGrip{position:relative;height:11px;').replace('dock.appendChild(dg);','dock.insertBefore(dg,dock.firstChild);').replace('build 036 | NEW','build 039 | NEW').replace('Drag up / down to make the dock thumbnails bigger / smaller','Drag up / down: thumbnails bigger / smaller')
def blk(b,m):
    i=b.index(m); i=b.rindex('<style>',0,i); j=b.index('</script>',i)+9; return i,j
i,j=blk(b,':root{--cp:#39ff14;--mw:#ffb000');b=b[:i]+a3b+b[j:]
i,j=blk(b,'#slcHost{max-height:none!important');b=b[:i]+a4b+b[j:]
a6=open('addon6.html').read().strip()
b=b.replace('window.hxDl=dl;window.hxPick=pick;','window.hxDl=dl;window.hxPick=pick;window.hxBuild=build;window.hxHX=HX;window.hxRng=rng;window.hxLoad=load;window.hxRender=render;window.hxFmtD=fmtD;',1)
k=b.rindex('</body>');b=b[:k]+a5+'\n'+a6+'\n'+b[k:]
b=b.replace('<script>','<script>try{localStorage.setItem("slc_mwmode","DEFAULT");localStorage.removeItem("slc_mwoff")}catch(e){}</script><script>',1)
b=b.replace('<style>','<style>#float:not(.slcOn){display:none!important}',1)
b=b.replace('build 036','build 039')
b=b.replace('var LOG=[','var LOG=[\n ["037","2026-10-04","EDT","Page 1 green Companion Control Panel (single START, results box under thumbnails), Page 2 purple Control Deck (loaded, resources, estimates, break-up, memory/loading options for all parts), Page 3 blue Main App; text tiles + 0.5-line spacing; long logs behind bottom buttons; dock grip no longer covers START"],',1)
b=b.replace('</body>',open('addon7.html').read()+open('addon8.html').read()+open('addon9.html').read()+open('addon10.html').read()+open('addon11.html').read()+open('addon12.html').read()+open('addon13.html').read()+open('addon14.html').read()+open('addon15.html').read()+open('addon16.html').read()+open('addon17.html').read()+open('addon18.html').read()+open('addon19.html').read()+open('addon20.html').read()+open('addon21.html').read()+open('addon22.html').read()+open('addon23.html').read()+open('addon24.tpl').read()+open('addon25.html').read().replace('__P4THUMB__',open('p4_thumb.b64').read())+open('addon26.html').read()+open('addon27.html').read()+open('addon28.html').read()+open('addon30.html').read()+open('addon31.html').read()+open('addon29.html').read()+open('addon32.html').read()+open('addon33.html').read()+open('addon34.html').read()+open('addon35.html').read()+open('addon36.html').read()+open('addon37.html').read()+open('addon38.html').read()+open('addon39.html').read()+open('addon40.html').read()+'</body>')
b=b.replace('build 037','build 039')
b=b.replace('var LOG=[','var LOG=[\n ["038","2026-10-04","EDT","Saves split into pieces of 7 MB or less with progress pill; Start buttons show estimates and live response; edge resize on every panel; Page 3 history grab: progress, file info, trade-record option"],',1)
b=b.replace('build 039','build 039')
b=b.replace('Main App (MarketWatch)','MarketWatch').replace('PAGE 3 \\u00b7 MAIN APP','PAGE 3 \\u00b7 MARKETWATCH').replace('PAGE 3 \u00b7 MAIN APP','PAGE 3 \u00b7 MARKETWATCH').replace('Page 3 Main App','Page 3 MarketWatch').replace('P3 Main App','P3 MarketWatch')
b=b.replace('function mwGet(cb){','window.__rmStrip=rmStrip;window.__rmPatch=rmPatch;function mwGet(cb){',1)
b=b.replace('function lfLog(k,t){if(!lfOn)return;','function lfLog(k,t){try{window.slcNotifyLog&&window.slcNotifyLog(k,t)}catch(e){}if(!lfOn)return;')
b=b.replace('if(e&&e.code==="cancelled")return;fb()','if(e&&(e.code==="cancelled"||e.code==="declined")){window.__slcCancelled=Date.now();return}fb()')
b=b.replace('<script>','<script>window.__slcClickT=0;window.__slcCancelled=0;document.addEventListener("click",function(e){if(e.isTrusted)window.__slcClickT=Date.now()},true);</script><script>',1)
b=b.replace('var LOG=[','var LOG=[\n ["039","2026-10-04","EDT","Page 3 panel hidden at load and shown only when MarketWatch reports ready (auto-closes after 20 s); bottom Document & Auto tools with Auto diag / Autorepair (run on load); toolbar buttons autofit; History/Backtest panel stacks buttons; Home Index fills width"],',1)
open('companion_v0.01d_build038.html','w').write(b);open('srv/index.html','w').write(b)
