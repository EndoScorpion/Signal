#!/usr/bin/env python3
# Win Logic v2 build 043 patch: MQL-style branch families (EMA cross, MACD, Bollinger bounce/breakout, Parabolic SAR,
# ADX/DMI, CCI), ATR-multiple exits, extra regimes (adx, cost-gate, us/eu sessions), DD-ok judge flag, export sync,
# build bump 042 -> 043. Exact read-replace with count assertions; old win logic is left byte-identical.
# usage: python3 patches/w2_build043_patch.py <w2_module_source.html> <build042.html> <YYYYMMDD-HHMM> "<D Mon YYYY HH:MM EDT>"
import sys,re,os
src_in,html_in,stamp,disp=sys.argv[1:5]
def rep(s,old,new,n=1):
    c=s.count(old);assert c==n,('count %d != %d for: %s'%(c,n,old[:90]));return s.replace(old,new)
m0=open(src_in,encoding='utf-8').read();m=m0
E=[]
# ---- 1. indicators (appended after roll(), before the specs block)
E.append(('/* ---------- specs ---------- */',
'/* ---------- build 043: MQL-style indicators (EMA, MACD, Bollinger stdev, Parabolic SAR, ADX/DMI, CCI) - computed from real OHLC only ---------- */\n'
'function ema(c,n){var o=new Array(c.length).fill(null),k=2/(n+1),e=null,s=0;for(var i=0;i<c.length;i++){if(i<n){s+=c[i];if(i===n-1){e=s/n;o[i]=e}}else{e=c[i]*k+e*(1-k);o[i]=e}}return o}\n'
'function macd(c,f,s,g){var ef=ema(c,f),es=ema(c,s),m=new Array(c.length).fill(null),sg=new Array(c.length).fill(null),k=2/(g+1),e=null,q=0,sum=0;for(var i=0;i<c.length;i++){if(ef[i]==null||es[i]==null)continue;m[i]=ef[i]-es[i];if(e==null){q++;sum+=m[i];if(q===g){e=sum/g;sg[i]=e}}else{e=m[i]*k+e*(1-k);sg[i]=e}}return{m:m,sig:sg}}\n'
'function sdev(c,n){var o=new Array(c.length).fill(null),s=0,s2=0;for(var i=0;i<c.length;i++){s+=c[i];s2+=c[i]*c[i];if(i>=n){s-=c[i-n];s2-=c[i-n]*c[i-n]}if(i>=n-1){var mu=s/n,v=s2/n-mu*mu;o[i]=Math.sqrt(v>0?v:0)}}return o}\n'
'function sar(b,st,mx){var n=b.length,o=new Array(n).fill(null);if(n<2)return o;var up=b[1].c>=b[0].c,af=st,ep=up?b[0].h:b[0].l,s=up?b[0].l:b[0].h;for(var i=1;i<n;i++){s=s+af*(ep-s);if(up){s=i>=2?Math.min(s,b[i-1].l,b[i-2].l):Math.min(s,b[i-1].l);if(b[i].l<s){up=false;s=ep;ep=b[i].l;af=st}else if(b[i].h>ep){ep=b[i].h;af=Math.min(af+st,mx)}}else{s=i>=2?Math.max(s,b[i-1].h,b[i-2].h):Math.max(s,b[i-1].h);if(b[i].h>s){up=true;s=ep;ep=b[i].h;af=st}else if(b[i].l<ep){ep=b[i].l;af=Math.min(af+st,mx)}}o[i]=s}return o}\n'
'function adx(b,n){var N=b.length,A=new Array(N).fill(null),P=new Array(N).fill(null),M=new Array(N).fill(null),tr=0,pd=0,md=0,nd=0,ax=null,sd=0;for(var i=1;i<N;i++){var h=b[i].h,l=b[i].l,pc=b[i-1].c,up=h-b[i-1].h,dn=b[i-1].l-l,t=Math.max(h-l,Math.abs(h-pc),Math.abs(l-pc)),pp=up>dn&&up>0?up:0,mm=dn>up&&dn>0?dn:0;\n'
' if(i<=n){tr+=t;pd+=pp;md+=mm;if(i<n)continue}else{tr=tr-tr/n+t;pd=pd-pd/n+pp;md=md-md/n+mm}\n'
' var pdi=tr?100*pd/tr:0,mdi=tr?100*md/tr:0,d=(pdi+mdi)?100*Math.abs(pdi-mdi)/(pdi+mdi):0;P[i]=pdi;M[i]=mdi;if(ax==null){sd+=d;nd++;if(nd===n){ax=sd/n;A[i]=ax}}else{ax=(ax*(n-1)+d)/n;A[i]=ax}}\n'
' return{adx:A,pdi:P,mdi:M}}\n'
'function cci(b,n){var N=b.length,o=new Array(N).fill(null),tp=new Array(N),s=0,i;for(i=0;i<N;i++)tp[i]=(b[i].h+b[i].l+b[i].c)/3;for(i=0;i<N;i++){s+=tp[i];if(i>=n)s-=tp[i-n];if(i>=n-1){var mu=s/n,md=0;for(var j=i-n+1;j<=i;j++)md+=Math.abs(tp[j]-mu);md/=n;o[i]=md?(tp[i]-mu)/(0.015*md):0}}return o}\n'
'/* ---------- specs ---------- */'))
E.append(('else if(k==="hh")r=roll(b,n,1);else r=roll(b,n,0);return m[K]=r}',
'else if(k==="hh")r=roll(b,n,1);else if(k==="ema")r=ema(C(b),n);else if(k==="sd")r=sdev(C(b),n);else if(k==="cci")r=cci(b,n);else if(k==="adx")r=adx(b,n);else if(k==="macd")r=macd(C(b),n[0],n[1],n[2]);else if(k==="sar")r=sar(b,n[0],n[1]);else r=roll(b,n,0);return m[K]=r}'))
# ---- 2. names
E.append(('(x.tr?" trail"+x.tr:"")','(x.tr?" trail"+x.tr:"")+(x.atp?" atp"+x.atp:"")+(x.asl?" asl"+x.asl:"")+(x.atr?" atrail"+x.atr:"")'))
E.append(('k==="MIX"?nm(sp.a)+" & "+nm(sp.b)+" (3b)":k;return base+e+r}',
'k==="MIX"?nm(sp.a)+" & "+nm(sp.b)+" (3b)":k==="EMA"?"EMA "+sp.a+"/"+sp.b:k==="MACD"?"MACD "+sp.f+"/"+sp.s+"/"+sp.g:k==="BB"?"BB"+sp.n+" "+(sp.d/10)+"sd bounce":k==="BBO"?"BB"+sp.n+" "+(sp.d/10)+"sd breakout":k==="SAR"?"SAR "+(sp.st/1000)+"/"+(sp.mx/100):k==="ADX"?"ADX"+sp.n+">"+sp.th+" DI+ cross":k==="CCI"?"CCI"+sp.n+" -"+sp.lo+"/+"+sp.hi:k;return base+e+r}'))
# ---- 3. signal families
E.append(('ex[i]=c[i]<s2[i]||r2[i]>sp.hi?1:0}}\n return{en:en,ex:ex}}',
'ex[i]=c[i]<s2[i]||r2[i]>sp.hi?1:0}}\n'
' /* build 043: MQL-style families (long-only, same entry/exit contract as above) */\n'
' else if(sp.k==="EMA"){var ef=I(b,"ema",sp.a),es=I(b,"ema",sp.b);for(i=1;i<n;i++){if(ef[i]==null||es[i]==null||ef[i-1]==null||es[i-1]==null)continue;en[i]=ef[i-1]<=es[i-1]&&ef[i]>es[i]?1:0;ex[i]=ef[i-1]>=es[i-1]&&ef[i]<es[i]?1:0}}\n'
' else if(sp.k==="MACD"){var md=I(b,"macd",[sp.f,sp.s,sp.g]),ml=md.m,ms=md.sig;for(i=1;i<n;i++){if(ml[i]==null||ms[i]==null||ml[i-1]==null||ms[i-1]==null)continue;en[i]=ml[i-1]<=ms[i-1]&&ml[i]>ms[i]?1:0;ex[i]=ml[i-1]>=ms[i-1]&&ml[i]<ms[i]?1:0}}\n'
' else if(sp.k==="BB"||sp.k==="BBO"){var bm=I(b,"sma",sp.n),bs=I(b,"sd",sp.n),bd=sp.d/10;for(i=1;i<n;i++){if(bm[i]==null||bs[i]==null||bm[i-1]==null||bs[i-1]==null)continue;var lo1=bm[i-1]-bd*bs[i-1],lo0=bm[i]-bd*bs[i],up1=bm[i-1]+bd*bs[i-1],up0=bm[i]+bd*bs[i];\n'
'  if(sp.k==="BB"){en[i]=c[i-1]<lo1&&c[i]>=lo0?1:0;ex[i]=c[i]>=bm[i]?1:0}else{en[i]=c[i-1]<=up1&&c[i]>up0?1:0;ex[i]=c[i]<bm[i]?1:0}}}\n'
' else if(sp.k==="SAR"){var ps=I(b,"sar",[sp.st/1000,sp.mx/100]);for(i=1;i<n;i++){if(ps[i]==null||ps[i-1]==null)continue;en[i]=ps[i-1]>c[i-1]&&ps[i]<c[i]?1:0;ex[i]=ps[i-1]<c[i-1]&&ps[i]>c[i]?1:0}}\n'
' else if(sp.k==="ADX"){var ad=I(b,"adx",sp.n),ax=ad.adx,pd=ad.pdi,mdi=ad.mdi;for(i=1;i<n;i++){if(ax[i]==null||pd[i-1]==null||mdi[i-1]==null)continue;en[i]=pd[i-1]<=mdi[i-1]&&pd[i]>mdi[i]&&ax[i]>sp.th?1:0;ex[i]=mdi[i]>pd[i]?1:0}}\n'
' else if(sp.k==="CCI"){var cc=I(b,"cci",sp.n);for(i=1;i<n;i++){if(cc[i]==null||cc[i-1]==null)continue;en[i]=cc[i-1]<(-sp.lo)&&cc[i]>=(-sp.lo)?1:0;ex[i]=cc[i]>sp.hi?1:0}}\n'
' return{en:en,ex:ex}}'))
# ---- 4. regimes (new ones checked before the quiet fallthrough; quiet/trend untouched)
E.append(('function regOK(sp,b,i){if(!sp.reg)return true;if(sp.reg==="trend"){',
'function regOK(sp,b,i,rt){if(!sp.reg)return true;\n'
' /* build 043 regimes: adx = ADX14>20 (trend strength), cg = cost gate (ATR14 % of price >= 2x round-trip cost), us/eu = entry-bar session (UTC hours) */\n'
' if(sp.reg==="adx"){var ad=I(b,"adx",14).adx;return ad[i]!=null&&ad[i]>20}\n'
' if(sp.reg==="cg"){var a0=I(b,"atr",14),c0=C(b);return a0[i]!=null&&(a0[i]/c0[i]*100)>=2*(rt!=null?rt:0.15)}\n'
' if(sp.reg==="us"||sp.reg==="eu"){var hr=new Date(b[i].t).getUTCHours();return sp.reg==="us"?(hr>=13&&hr<=20):(hr>=7&&hr<=15)}\n'
' if(sp.reg==="trend"){'))
# ---- 5. ATR-multiple exits in bt2 (checked after the % exits, before hold/signal exit); rtOf helper
E.append(('function bt2(sp,se){','function rtOf(c0){return(c0.comm+c0.fee)*2+c0.spread}\nfunction bt2(sp,se){'))
E.append(('rt=(c0.comm+c0.fee)*2+c0.spread,hrs=(se.m||60)/60;','rt=(c0.comm+c0.fee)*2+c0.spread,hrs=(se.m||60)/60,AT=(x.atp||x.asl||x.atr)?I(b,"atr",14):null,ap=0;'))
E.append(('else if(x.tr&&hi>=x.tr&&g<=hi-x.tr)done=true;else if(x.hold?',
'else if(x.tr&&hi>=x.tr&&g<=hi-x.tr)done=true;else if(x.atp&&ap&&g>=x.atp*ap)done=true;else if(x.asl&&ap&&g<=-x.asl*ap)done=true;else if(x.atr&&ap&&hi>=x.atr*ap&&g<=hi-x.atr*ap)done=true;else if(x.hold?'))
E.append(('if(!pos&&s.en[i]&&regOK(sp,b,i)){pos={p:c,i:i};hi=0}}','if(!pos&&s.en[i]&&regOK(sp,b,i,rt)){pos={p:c,i:i};hi=0;ap=AT&&AT[i]!=null?AT[i]/c*100:0}}'))
# ---- 6. judge flag (PLAN.md stage 4: max DD < 2x avg net trade); passes() unchanged
E.append(('hmdd:DH.mdd,sig:nm(sp),','hmdd:DH.mdd,ddok:o.t>0&&D.mdd<2*(o.a/o.t),sig:nm(sp),'))
# ---- 7. generation
E.append(('keys={SMA:["a","b"],RSI:["n","lo","hi"],STO:["n","lo","hi"],DON:["n"],SR:["n","r","lo","hi"]}[sp.k]||[];',
'keys={SMA:["a","b"],RSI:["n","lo","hi"],STO:["n","lo","hi"],DON:["n"],SR:["n","r","lo","hi"],EMA:["a","b"],MACD:["f","s","g"],BB:["n","d"],BBO:["n","d"],SAR:["st","mx"],ADX:["n","th"],CCI:["n","lo","hi"]}[sp.k]||[];'))
E.append(('if(c.k==="SMA"&&c.a>=c.b)return;if((c.lo!=null)&&c.lo>=c.hi)return;',
'if((c.k==="SMA"||c.k==="EMA")&&c.a>=c.b)return;if(c.k==="MACD"&&c.f>=c.s)return;if((c.lo!=null)&&c.k!=="CCI"&&c.lo>=c.hi)return;'))
E.append(('var EXITS=[{hold:4},{hold:6},{hold:10},{tp:.5},{tp:1},{tp:2},{sl:.5},{sl:1},{tr:.5},{tr:1},{tp:1,sl:.5},{tp:2,sl:1}];',
'var EXITS=[{hold:4},{hold:6},{hold:10},{tp:.5},{tp:1},{tp:2},{sl:.5},{sl:1},{tr:.5},{tr:1},{tp:1,sl:.5},{tp:2,sl:1}];\n'
'/* build 043: MQL-style seed families (int-encoded params so neighbours()/vary() work unchanged: BB d in tenths, SAR st in thousandths / mx in hundredths, CCI lo/hi as magnitudes), ATR-multiple exits, extra regimes. BASE/EXITS above are untouched. */\n'
'var BASE2=[{k:"EMA",a:9,b:21},{k:"EMA",a:12,b:26},{k:"MACD",f:12,s:26,g:9},{k:"BB",n:20,d:20},{k:"BBO",n:20,d:20},{k:"SAR",st:20,mx:20},{k:"ADX",n:14,th:25},{k:"ADX",n:14,th:20},{k:"CCI",n:14,lo:100,hi:100},{k:"CCI",n:20,lo:100,hi:100}];\n'
'var EXITS2=[{atp:1.5},{atp:2},{asl:1},{atp:2,asl:1},{atp:3,asl:1.5},{atr:1.5}],REGS2=["quiet","trend","adx","cg","us","eu"],NEWK={EMA:1,MACD:1,BB:1,BBO:1,SAR:1,ADX:1,CCI:1};\n'
'function isLeg(sp){if(sp.k==="MIX")return isLeg(sp.a)&&isLeg(sp.b);var x=sp.x||{};return!NEWK[sp.k]&&!x.atp&&!x.asl&&!x.atr&&(!sp.reg||sp.reg==="quiet"||sp.reg==="trend")}'))
E.append(('var A=uniqSpecs(BASE.concat.apply(BASE,BASE.map(neighbours)));','var A=uniqSpecs(BASE.concat.apply(BASE,BASE.map(neighbours)).concat(BASE2.concat.apply(BASE2,BASE2.map(neighbours))));'))
E.append(('var top=topSpecs(rA,12),B=[];','var top=topSpecs(rA.filter(function(r){return isLeg(r.spec)}),12).concat(topSpecs(rA.filter(function(r){return!isLeg(r.spec)}),8)),B=[];'))
E.append(('top.forEach(function(sp){EXITS.forEach(function(x){','top.forEach(function(sp){EXITS.concat(EXITS2).forEach(function(x){'))
E.append(('var D=[],seed=top.concat(topSpecs(rB,6),topSpecs(rC,4));','var D=[],seed=top.concat(topSpecs(rB.filter(function(r){return isLeg(r.spec)}),6),topSpecs(rC.filter(function(r){return isLeg(r.spec)}),4),topSpecs(rB,6),topSpecs(rC,4));'))
E.append(('seed.forEach(function(sp){["quiet","trend"].forEach(function(rg){','seed.forEach(function(sp){REGS2.forEach(function(rg){'))
# ---- 8. fin(): legacy-first tie-break among clones (keeps build-042 winner names), ddok stored, memory cap 300 -> 600
E.append(('win.sort(function(a,b){return(b.hwp-a.hwp)||(b.wp-a.wp)}).forEach(','win.sort(function(a,b){return(b.hwp-a.hwp)||(b.wp-a.wp)||((isLeg(b.spec)?1:0)-(isLeg(a.spec)?1:0))}).forEach('))
E.append(('avgb:+r.avgb.toFixed(1),when:Date.now()};','avgb:+r.avgb.toFixed(1),ddok:!!r.ddok,when:Date.now()};'))
E.append(('.slice(0,300);mem.build=B2','.slice(0,5000);mem.build=B2'))
# ---- 9. table + txt: additive last column "DD ok"
E.append(("<th>Avg hold</th></tr>'+mem.winners.slice(0,40).map(","<th>Avg hold</th><th>DD ok</th></tr>'+mem.winners.slice(0,40).map("))
E.append(('(w.avgb*w.tfm).toFixed(0)+" min</td></tr>"}).join("")+"</table>"}','(w.avgb*w.tfm).toFixed(0)+" min</td><td class="+(w.ddok?"ok":"warn")+">"+(w.ddok==null?"-":w.ddok?"yes":"no")+"</td></tr>"}).join("")+"</table>"}'))
E.append(('\\tavg_hold_bars\\tspec_json");','\\tavg_hold_bars\\tspec_json\\tdd_ok");'))
E.append(('w.avgb,JSON.stringify(w.spec)].join("\\t"))});','w.avgb,JSON.stringify(w.spec),(w.ddok==null?"-":w.ddok?"yes":"no")].join("\\t"))});'))
# ---- 10. scan + export pass the round-trip cost into regOK; export ships the new indicator functions
E.append(('typ=s.en[n-1]&&regOK(w.spec,b,n-1)?"BUY":s.ex[n-1]?"EXIT":null;if(!typ)return;','typ=s.en[n-1]&&regOK(w.spec,b,n-1,rtOf(costOf(se)))?"BUY":s.ex[n-1]?"EXIT":null;if(!typ)return;'))
E.append(('var code=[sma,rsi,sto,atr,roll,C,I,nm,sigOf,regOK].map(String).join("\\n");','var code=[sma,rsi,sto,atr,roll,ema,macd,sdev,sar,adx,cci,C,I,nm,sigOf,regOK].map(String).join("\\n");'))
E.append(('return{s:w.s,tf:w.tf,tfm:w.tfm,sig:w.sig,spec:w.spec,hwp:w.hwp,wp:w.wp}});','return{s:w.s,tf:w.tf,tfm:w.tfm,sig:w.sig,spec:w.spec,hwp:w.hwp,wp:w.wp,cls:w.cls}});'))
E.append(('var typ=s.en[n-1]&&regOK(w.spec,b,n-1)?"BUY":s.ex[n-1]?"EXIT":null;if(typ)out.push(','var c0=COSTS[w.cls]||COSTS.perp||{comm:0,fee:0.045,spread:0.03};var typ=s.en[n-1]&&regOK(w.spec,b,n-1,(c0.comm+c0.fee)*2+c0.spread)?"BUY":s.ex[n-1]?"EXIT":null;if(typ)out.push('))
for old,new in E: m=rep(m,old,new)
# ---- 11. build bump inside the module
m=rep(m,'build 042','build 043',4)
m=rep(m,'build042','build043',m.count('build042'))  # export file names
m=rep(m,'9 Oct 2026 00:40 EDT',disp,5)
m=rep(m,'Win Logic v2 + Signal Alerts + JS Export |','Win Logic v2 + Signal Alerts + JS Export + MQL families |',3)
open(src_in,'w',encoding='utf-8').write(m)
# backup .txt = original 4-line header (bumped) + patched module
hdr='\n'.join(open([f for f in os.listdir('.') if f.startswith('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build042')][0],encoding='utf-8').read().split('\n')[:4])
hdr=hdr.replace('build 042','build 043').replace('9 Oct 2026 00:40 EDT',disp).replace('STAGES flash fix)','STAGES flash fix + MQL families)')
open('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build043_'+stamp+'.txt','w',encoding='utf-8').write(hdr+'\n'+m)
# added-code text backup
open('patches/w2_build043_added_code_BACKUP.txt','w',encoding='utf-8').write('Win Logic v2 build 043 patch - added/changed code (new text of every replacement) | '+disp+'\n\n'+'\n\n'.join('--- replaces: '+o[:100]+'\n'+n for o,n in E))
# ---- 12. page: splice patched module, bump page-level build strings
h=open(html_in,encoding='utf-8').read()
h=rep(h,m0,m)
h=rep(h,'build 042','build 043',12)
h=rep(h,'8 Oct 2026 EDT','9 Oct 2026 EDT',10)
h=rep(h,'build042','build043',h.count('build042'))
out='Signal_Live_Companion_v0.01d_build043_WinLogicV2_MQL_'+stamp+'.html'
open(out,'w',encoding='utf-8').write(h)
print('wrote',out,len(h),'| module',len(m),'| remaining "build 042":',h.count('build 042'),'| "build 043":',h.count('build 043'))
