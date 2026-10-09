import base64,re
T=open('kit_template.html',encoding='utf8').read()
mods=''.join(open(f'addon{n}.html',encoding='utf8').read()+'\n' for n in (29,32,33,36,37,38))
# kit build: the companion-only 'btn' helpers are harmless; strip nothing
T=T.replace('__ADDONS__',mods)
b64=base64.b64encode(T.encode('utf8')).decode()
js='''<script>
(function(){
var B64="%s";
function tpl(){var bin=atob(B64),u=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);return new TextDecoder("utf-8").decode(u)}
var MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function stamp(){var d=new Date();return {h:d.getDate()+" "+MN[d.getMonth()]+" "+d.getFullYear()+" "+d.toTimeString().slice(0,5),f:d.toISOString().slice(0,16).replace(/[-:T]/g,"")}}
function ls(k){try{return JSON.parse(localStorage.getItem(k)||"null")}catch(e){return null}}
function build(){var t=stamp(),H=null;try{if(window.slcDivTop&&Object.keys(slcDivTop._H||{}).length)H=slcDivTop._H}catch(e){}H=H||ls("slc_divyield_v1")||{};
 var data={slc_divyield_v1:H,slc_fundperf_v1:ls("slc_fundperf_v1")||{},tested:ls("slc_tested_v1")||[],MET:(window.slcMD&&slcMD.list&&slcMD.list.MET)||[],DIV:(window.slcMD&&slcMD.list&&slcMD.list.DIV)||[],CAT:(window.slcMD2&&slcMD2.CAT)||{}};
 var plan=(document.getElementById("mdPlan")||{}).value||"",rules="";try{rules=document.querySelector("#slcRob")?"":"";}catch(e){}
 var rs="ROBUST DIP-REBOUND RULES (build 039) - BUY only\\nR1 3h drop > 1.5%% AND 12h drop > 3%%\\nR2 Stoch(14) < 10 AND 12h drop > 3%%\\nR3 Bollinger %%B < 5 AND 12h drop > 3%%\\nR4 price > 2 std below SMA20 AND 12h drop > 3%%\\nExit: 4 hourly bars or hard stop -1.5%%. One trade per coin at a time. SELL rules failed out-of-sample and were dropped. Past results; not advice.".replace(/%%/g,"%%");
 var title="Weekly Dividends + Funds + Win Rules - Signal Live Companion v0.01d build 039 - "+t.h;
 var html=tpl().split("__TITLE__").join(title).split("__STAMP__").join(t.h);
 var inj="var __D="+JSON.stringify(data).replace(/</g,"\\\\u003c")+";window.__PLAN="+JSON.stringify(plan).replace(/</g,"\\\\u003c")+";window.__RULES="+JSON.stringify(rs)+";";
 html=html.replace("var __D=/*__DATA__*/{};",function(){return inj});return {html:html,n:Object.keys(H).length,f:t.f}}
var NEED=["dtLoad","dtCsv","dtJs","dtVw","fpLoad","fpHead","fpCsv","fpJs","fpVw","rbDed","rbScan","rbSv","gbGo","gbTest","gbCsv","slcSave=","slcNet","slcGetMcp","slcDivTop","slcFund","slcRobust","slcGrab","slcSplit","kOpen","kReset"];
function verify(h){var miss=NEED.filter(function(k){return h.indexOf(k)<0});return {ok:!miss.length&&h.indexOf("</html>")>0&&(h.match(/<script/g)||[]).length===(h.match(/<\/script>/g)||[]).length,miss:miss}}
function go(){var r=build();var v=verify(r.html);if(!v.ok){try{slcNotify("error","Export NOT saved - integrity check failed, missing: "+(v.miss.join(", ")||"unbalanced script tags"))}catch(e){}return}if(!r.n){try{slcNotify("warn","Load the yield leaderboard first (Load button), then export - otherwise the file would be empty.")}catch(e){}try{slcDivTop.open()}catch(e){}return}
 window.slcSave("slc_dividends_funds_FULL_APP_b039_"+r.f+".html",r.html,"text/html")}
function rebind(){var b=document.getElementById("slcDivHx");if(b&&!b.__full){b.__full=1;b.onclick=go;b.textContent="⬇ HTML export: Dividends (full app)";b.title="One standalone HTML file with the leaderboard, fund table, rules checker and file tools - all buttons work offline."}}
setInterval(rebind,800);rebind();window.slcKit={build:build,go:go,verify:verify};
})();
</script>
''' % b64
open('addon40.html','w',encoding='utf8').write(js)
print(len(T),len(js))
