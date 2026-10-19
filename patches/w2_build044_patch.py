#!/usr/bin/env python3
# Win Logic v2 build 044 patch (applied on top of build 043): more MQL-style families (Keltner breakout, Envelope bounce,
# Momentum, Awesome Oscillator, Ichimoku, slow Stochastic), short holds + 1xATR exit, "vol" regime, external seed series
# with explicit cost class (localStorage slc_win2_ext or window.W2EXT), tiered generation so the 042 and 043 paths stay
# strict subsets, build bump 043 -> 044. Exact read-replace with count assertions.
# usage: python3 patches/w2_build044_patch.py <w2_module_source.html> <build043.html> <YYYYMMDD-HHMM> "<D Mon YYYY HH:MM EDT>"
import sys,os
src_in,html_in,stamp,disp=sys.argv[1:5]
def rep(s,old,new,n=1):
    c=s.count(old);assert c==n,('count %d != %d for: %s'%(c,n,old[:90]));return s.replace(old,new)
m0=open(src_in,encoding='utf-8').read();m=m0;E=[]
# ---- external series (explicit cost class) read beside the HL seed
E.append(('var HL=ld("slc_win2_hl",{});','var HL=ld("slc_win2_hl",{}),EXT=ld("slc_win2_ext",{}); /* build 044: external real-bar series {"SYM|TF":{cls,src,b:[[t,o,h,l,c]..]}} from localStorage or window.W2EXT */'))
E.append((' function add(s,tf,arr,src){var b=arr.map(nb).filter(Boolean);',' function add(s,tf,arr,src,cls){var b=arr.map(nb).filter(Boolean);'))
E.append(('S.push({s:s,tf:tf,m:TFM[tf]||60,b:b,src:src})}','S.push({s:s,tf:tf,m:TFM[tf]||60,b:b,src:src,cls:cls})}'))
E.append((' try{Object.keys(HL).forEach(function(k){var p=k.split("|");if(Array.isArray(HL[k]))add(p[0],p[1],HL[k],"hl")})}catch(e){}',
' try{Object.keys(HL).forEach(function(k){var p=k.split("|");if(Array.isArray(HL[k]))add(p[0],p[1],HL[k],"hl")})}catch(e){}\n'
' try{[EXT,(typeof window!=="undefined"&&window.W2EXT)||{}].forEach(function(X){Object.keys(X).forEach(function(k){var p=k.split("|"),e=X[k];if(e&&Array.isArray(e.b)&&p.length===2)add(p[0],p[1],e.b,e.src||"ext",e.cls)})})}catch(e){}'))
# ---- indicators
E.append(('/* ---------- specs ---------- */',
'/* ---------- build 044: more MQL-style indicators (median price, null-aware SMA, slow Stochastic, Ichimoku) ---------- */\n'
'function mdp(b){return b._mp||(b._mp=b.map(function(x){return(x.h+x.l)/2}))}\n'
'function smaN(a,n){var o=new Array(a.length).fill(null);for(var i=n-1;i<a.length;i++){var s=0,ok=1;for(var j=i-n+1;j<=i;j++){if(a[j]==null){ok=0;break}s+=a[j]}if(ok)o[i]=s/n}return o}\n'
'function stos(b,n,s){var k=smaN(sto(b,n),s);return{k:k,d:smaN(k,3)}}\n'
'function ich(b,t,k,s){var n=b.length,tk=new Array(n).fill(null),kj=new Array(n).fill(null),sa=new Array(n).fill(null),sb=new Array(n).fill(null),hT=roll(b,t,1),lT=roll(b,t,0),hK=roll(b,k,1),lK=roll(b,k,0),hS=roll(b,s,1),lS=roll(b,s,0),i;\n'
' for(i=0;i<n;i++){if(hT[i]!=null)tk[i]=(hT[i]+lT[i])/2;if(hK[i]!=null)kj[i]=(hK[i]+lK[i])/2}\n'
' for(i=k;i<n;i++){var j=i-k;if(tk[j]!=null&&kj[j]!=null)sa[i]=(tk[j]+kj[j])/2;if(hS[j]!=null)sb[i]=(hS[j]+lS[j])/2}return{tk:tk,kj:kj,sa:sa,sb:sb}}\n'
'/* ---------- specs ---------- */'))
E.append(('else if(k==="sar")r=sar(b,n[0],n[1]);else r=roll(b,n,0);return m[K]=r}',
'else if(k==="sar")r=sar(b,n[0],n[1]);else if(k==="smp")r=sma(mdp(b),n);else if(k==="ich")r=ich(b,n[0],n[1],n[2]);else if(k==="stos")r=stos(b,n[0],n[1]);else r=roll(b,n,0);return m[K]=r}'))
# ---- names
E.append(('k==="CCI"?"CCI"+sp.n+" -"+sp.lo+"/+"+sp.hi:k;return base+e+r}',
'k==="CCI"?"CCI"+sp.n+" -"+sp.lo+"/+"+sp.hi:k==="KC"?"Keltner"+sp.n+" "+(sp.m/10)+"xATR"+sp.a:k==="ENV"?"Env"+sp.n+" "+(sp.p/100)+"%":k==="MOM"?"Momentum"+sp.n:k==="AO"?"AO "+sp.f+"/"+sp.s:k==="ICH"?"Ichimoku "+sp.t+"/"+sp.kj+"/"+sp.s:k==="STD"?"SlowStoch"+sp.n+"/"+sp.s+" "+sp.lo+"/"+sp.hi:k;return base+e+r}'))
# ---- families
E.append(('ex[i]=cc[i]>sp.hi?1:0}}\n return{en:en,ex:ex}}',
'ex[i]=cc[i]>sp.hi?1:0}}\n'
' /* build 044 families: Keltner breakout, Envelope bounce, Momentum (ROC crosses 100), Awesome Oscillator zero cross, Ichimoku Tenkan/Kijun cross above cloud, slow Stochastic %K/%D cross below lo */\n'
' else if(sp.k==="KC"){var ke=I(b,"ema",sp.n),ka=I(b,"atr",sp.a),km=sp.m/10;for(i=1;i<n;i++){if(ke[i]==null||ka[i]==null||ke[i-1]==null||ka[i-1]==null)continue;var ku1=ke[i-1]+km*ka[i-1],ku0=ke[i]+km*ka[i];en[i]=c[i-1]<=ku1&&c[i]>ku0?1:0;ex[i]=c[i]<ke[i]?1:0}}\n'
' else if(sp.k==="ENV"){var ev=I(b,"sma",sp.n),ep=sp.p/10000;for(i=1;i<n;i++){if(ev[i]==null||ev[i-1]==null)continue;var el1=ev[i-1]*(1-ep),el0=ev[i]*(1-ep);en[i]=c[i-1]<el1&&c[i]>=el0?1:0;ex[i]=c[i]>=ev[i]?1:0}}\n'
' else if(sp.k==="MOM"){for(i=sp.n+1;i<n;i++){var r1=c[i-1]/c[i-1-sp.n],r0=c[i]/c[i-sp.n];en[i]=r1<=1&&r0>1?1:0;ex[i]=r1>=1&&r0<1?1:0}}\n'
' else if(sp.k==="AO"){var af=I(b,"smp",sp.f),as=I(b,"smp",sp.s);for(i=1;i<n;i++){if(af[i]==null||as[i]==null||af[i-1]==null||as[i-1]==null)continue;var o1=af[i-1]-as[i-1],o0=af[i]-as[i];en[i]=o1<=0&&o0>0?1:0;ex[i]=o1>=0&&o0<0?1:0}}\n'
' else if(sp.k==="ICH"){var ic=I(b,"ich",[sp.t,sp.kj,sp.s]),tk=ic.tk,kj=ic.kj,sa=ic.sa,sb=ic.sb;for(i=1;i<n;i++){if(tk[i]==null||kj[i]==null||tk[i-1]==null||kj[i-1]==null||sa[i]==null||sb[i]==null)continue;en[i]=tk[i-1]<=kj[i-1]&&tk[i]>kj[i]&&c[i]>Math.max(sa[i],sb[i])?1:0;ex[i]=tk[i]<kj[i]?1:0}}\n'
' else if(sp.k==="STD"){var ss=I(b,"stos",[sp.n,sp.s]),sk=ss.k,sd2=ss.d;for(i=1;i<n;i++){if(sk[i]==null||sd2[i]==null||sk[i-1]==null||sd2[i-1]==null)continue;en[i]=sk[i-1]<=sd2[i-1]&&sk[i]>sd2[i]&&sk[i-1]<sp.lo?1:0;ex[i]=sk[i]>sp.hi?1:0}}\n'
' return{en:en,ex:ex}}'))
# ---- regime: vol (ATR14 % above its 60-bar mean; inverse of quiet)
E.append((' if(sp.reg==="us"||sp.reg==="eu"){',
' if(sp.reg==="vol"){var a1=I(b,"atr",14),c1=C(b);if(a1[i]==null||a1[i-60]==null)return false;var m1=0,k1=0;for(var j1=i-60;j1<i;j1++){if(a1[j1]!=null){m1+=a1[j1]/c1[j1];k1++}}return k1>0&&(a1[i]/c1[i])>(m1/k1)}\n'
' if(sp.reg==="us"||sp.reg==="eu"){'))
# ---- generation: seeds, exits, regimes, tiers
E.append(('ADX:["n","th"],CCI:["n","lo","hi"]}[sp.k]||[];','ADX:["n","th"],CCI:["n","lo","hi"],KC:["n","m","a"],ENV:["n","p"],MOM:["n"],AO:["f","s"],ICH:["t","kj","s"],STD:["n","s","lo","hi"]}[sp.k]||[];'))
E.append(('if(c.k==="MACD"&&c.f>=c.s)return;','if(c.k==="MACD"&&c.f>=c.s)return;if(c.k==="AO"&&c.f>=c.s)return;if(c.k==="ICH"&&c.t>=c.kj)return;'))
E.append(('var EXITS2=[{atp:1.5},{atp:2},{asl:1},{atp:2,asl:1},{atp:3,asl:1.5},{atr:1.5}],REGS2=["quiet","trend","adx","cg","us","eu"],NEWK={EMA:1,MACD:1,BB:1,BBO:1,SAR:1,ADX:1,CCI:1};',
'var EXITS2=[{atp:1.5},{atp:2},{asl:1},{atp:2,asl:1},{atp:3,asl:1.5},{atr:1.5}],REGS2=["quiet","trend","adx","cg","us","eu"],NEWK={EMA:1,MACD:1,BB:1,BBO:1,SAR:1,ADX:1,CCI:1};\n'
'/* build 044: third seed tier (KC m = ATR mult in tenths, a = ATR period; ENV p = envelope in hundredths of a percent; STD s = slowing), short holds + 1xATR exit, vol regime.\n'
'   tierOf(spec) = 0 for the build-042 search space, 1 for build-043 additions, 2 for build-044 additions: each tier is searched exactly as the earlier build searched it (tops per tier, seeds per cumulative tier), so every earlier build\'s branches are still generated and old winners reproduce. */\n'
'var BASE3=[{k:"KC",n:20,m:15,a:10},{k:"KC",n:20,m:20,a:10},{k:"ENV",n:20,p:50},{k:"ENV",n:20,p:100},{k:"MOM",n:10},{k:"MOM",n:14},{k:"AO",f:5,s:34},{k:"ICH",t:9,kj:26,s:52},{k:"STD",n:14,s:3,lo:20,hi:80},{k:"STD",n:5,s:3,lo:20,hi:80}];\n'
'var EXITS3=[{hold:2},{hold:3},{atp:1,asl:.5}],REGS3=["vol"],KT={EMA:1,MACD:1,BB:1,BBO:1,SAR:1,ADX:1,CCI:1,KC:2,ENV:2,MOM:2,AO:2,ICH:2,STD:2},RT={adx:1,cg:1,us:1,eu:1,vol:2},XT={};\n'
'EXITS.forEach(function(x){XT[JSON.stringify(x)]=0});EXITS2.forEach(function(x){XT[JSON.stringify(x)]=1});EXITS3.forEach(function(x){XT[JSON.stringify(x)]=2});\n'
'function tierOf(sp){var r=sp.reg?(RT[sp.reg]||0):0;if(sp.k==="MIX")return Math.max(tierOf(sp.a),tierOf(sp.b),r);var x=sp.x?XT[JSON.stringify(sp.x)]:0;if(x==null)x=2;return Math.max(KT[sp.k]||0,x,r)}\n'
'function tierTop(res,t,k){return topSpecs(res.filter(function(r){return tierOf(r.spec)===t}),k)}function tierUpTo(res,t,k){return topSpecs(res.filter(function(r){return tierOf(r.spec)<=t}),k)}'))
E.append(('var A=uniqSpecs(BASE.concat.apply(BASE,BASE.map(neighbours)).concat(BASE2.concat.apply(BASE2,BASE2.map(neighbours))));',
'var A=uniqSpecs(BASE.concat.apply(BASE,BASE.map(neighbours)).concat(BASE2.concat.apply(BASE2,BASE2.map(neighbours)),BASE3.concat.apply(BASE3,BASE3.map(neighbours))));'))
E.append(('var top=topSpecs(rA.filter(function(r){return isLeg(r.spec)}),12).concat(topSpecs(rA.filter(function(r){return!isLeg(r.spec)}),8)),B=[];',
'var top=tierTop(rA,0,12).concat(tierTop(rA,1,8),tierTop(rA,2,6)),B=[];'))
E.append(('top.forEach(function(sp){EXITS.concat(EXITS2).forEach(function(x){','top.forEach(function(sp){EXITS.concat(EXITS2,EXITS3).forEach(function(x){'))
E.append(('var D=[],seed=top.concat(topSpecs(rB.filter(function(r){return isLeg(r.spec)}),6),topSpecs(rC.filter(function(r){return isLeg(r.spec)}),4),topSpecs(rB,6),topSpecs(rC,4));',
'var D=[],seed=top.concat(tierUpTo(rB,0,6),tierUpTo(rC,0,4),tierUpTo(rB,1,6),tierUpTo(rC,1,4),topSpecs(rB,6),topSpecs(rC,4));'))
E.append(('seed.forEach(function(sp){REGS2.forEach(function(rg){','seed.forEach(function(sp){REGS2.concat(REGS3).forEach(function(rg){'))
E.append(('||((isLeg(b.spec)?1:0)-(isLeg(a.spec)?1:0))}).forEach(','||(tierOf(a.spec)-tierOf(b.spec))}).forEach('))
# ---- memory: cap 5000 -> 8000 (~416 chars per winner; Chromium allows ~5M chars per origin) + quota-aware save that trims only if the browser refuses
E.append(('.slice(0,5000);mem.build=B2','.slice(0,8000);mem.build=B2'))
E.append(('mem.when=Date.now();sv("slc_win2",mem);','mem.when=Date.now();var trimmed=0;for(;;){try{localStorage.setItem("slc_win2",JSON.stringify(mem));break}catch(e){if(mem.winners.length<=300)break;mem.winners=mem.winners.slice(0,Math.floor(mem.winners.length*0.9));trimmed++}}'))
E.append(('" clones dropped). Memory holds "+mem.winners.length+"."+(plateau?','" clones dropped). Memory holds "+mem.winners.length+"."+(trimmed?" <span class=warn>Browser storage full: memory trimmed to "+mem.winners.length+" best branches - export the winners .txt to keep the full list.</span>":"")+(plateau?'))
# ---- export ships the new indicator functions
E.append(('var code=[sma,rsi,sto,atr,roll,ema,macd,sdev,sar,adx,cci,C,I,nm,sigOf,regOK].map(String).join("\\n");','var code=[sma,rsi,sto,atr,roll,ema,macd,sdev,sar,adx,cci,mdp,smaN,stos,ich,C,I,nm,sigOf,regOK].map(String).join("\\n");'))
for old,new in E: m=rep(m,old,new)
# ---- build bump inside the module (count computed: banners + B2 + build-043 comments)
nb=m.count('build 043');assert nb>=4;m=m.replace('build 043','build 044')
m=rep(m,'build043','build044',m.count('build043'))
old_disp=[l for l in m.split('\n') if 'var B2="v0.01d build 044 | ' in l][0].split('var B2="v0.01d build 044 | ')[1].split('"')[0]
m=rep(m,old_disp,disp,m.count(old_disp))
open(src_in,'w',encoding='utf-8').write(m)
bk=[f for f in os.listdir('.') if f.startswith('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build043')][0]
hdr='\n'.join(open(bk,encoding='utf-8').read().split('\n')[:4]).replace('build 043','build 044').replace(old_disp,disp)
open('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build044_'+stamp+'.txt','w',encoding='utf-8').write(hdr+'\n'+m)
open('patches/w2_build044_added_code_BACKUP.txt','w',encoding='utf-8').write('Win Logic v2 build 044 patch - added/changed code (new text of every replacement) | '+disp+'\n\n'+'\n\n'.join('--- replaces: '+o[:100]+'\n'+n for o,n in E))
h=open(html_in,encoding='utf-8').read();h=rep(h,m0,m);h=h.replace('build 043','build 044');h=h.replace('build043','build044')
out='Signal_Live_Companion_v0.01d_build044_WinLogicV2_MQL2_'+stamp+'.html';open(out,'w',encoding='utf-8').write(h)
print('wrote',out,len(h),'| module',len(m),'| "build 043" left:',h.count('build 043'),'| "build 044":',h.count('build 044'),'| disp',old_disp,'->',disp)
