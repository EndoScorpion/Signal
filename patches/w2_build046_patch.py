#!/usr/bin/env python3
# Win Logic v2 build 046 (on top of 045): (1) per-timeframe seed selection - the top 3/2/1 specs per tier of EVERY timeframe join the
# global tops for the exits (Gen B) and regime (Gen D) stages, so adding series of one timeframe no longer starves another's seeds;
# MIX pairs and the earlier builds' Gen D seeds stay on the global tops (build 045's branch set is a strict subset).
# (2) winner memory in IndexedDB (no 5 MB localStorage cap): cap 8000 -> 20000; localStorage keeps a best-effort trimmed copy.
# usage: python3 patches/w2_build046_patch.py <w2_module_source.html> <build045.html> <YYYYMMDD-HHMM> "<D Mon YYYY HH:MM EDT>"
import sys,os
src_in,html_in,stamp,disp=sys.argv[1:5]
def rep(s,old,new,n=1):
    c=s.count(old);assert c==n,('count %d != %d for: %s'%(c,n,old[:90]));return s.replace(old,new)
m0=open(src_in,encoding='utf-8').read();m=m0;E=[]
m=rep(m,'ld("slc_win2",{winners:[]})','memGet()',6)   # every memory read goes through the cache
E.append(('var HL=ld("slc_win2_hl",{}),EXT=ld("slc_win2_ext",{});',
'var HL=ld("slc_win2_hl",{}),EXT=ld("slc_win2_ext",{});\n'
'/* build 046: winner memory lives in IndexedDB (no 5 MB localStorage cap); localStorage keeps a best-effort trimmed copy for older builds and exports */\n'
'var MEMC=null;function idb(cb){try{var r=indexedDB.open("slc_win2_db",1);r.onupgradeneeded=function(){r.result.createObjectStore("kv")};r.onsuccess=function(){cb(null,r.result)};r.onerror=function(){cb(r.error)}}catch(e){cb(e)}}\n'
'function idbGet(k,cb){idb(function(e,db){if(e)return cb(e);try{var t=db.transaction("kv","readonly").objectStore("kv").get(k);t.onsuccess=function(){cb(null,t.result)};t.onerror=function(){cb(t.error)}}catch(x){cb(x)}})}\n'
'function idbPut(k,v,cb){idb(function(e,db){if(e)return cb&&cb(e);try{var t=db.transaction("kv","readwrite").objectStore("kv").put(v,k);t.onsuccess=function(){cb&&cb(null)};t.onerror=function(){cb&&cb(t.error)}}catch(x){cb&&cb(x)}})}\n'
'function memGet(){return MEMC||ld("slc_win2",{winners:[]})}\n'
'idbGet("slc_win2",function(e,mm){if(!e&&mm&&mm.winners){var l=ld("slc_win2",{winners:[]});if(mm.winners.length>=(l.winners||[]).length){MEMC=mm;try{draw()}catch(x){}}}});'))
E.append(('.slice(0,8000);mem.build=B2;mem.when=Date.now();var trimmed=0;for(;;){try{localStorage.setItem("slc_win2",JSON.stringify(mem));break}catch(e){if(mem.winners.length<=300)break;mem.winners=mem.winners.slice(0,Math.floor(mem.winners.length*0.9));trimmed++}}',
'.slice(0,20000);mem.build=B2;mem.when=Date.now();MEMC=mem;idbPut("slc_win2",mem);var lsm={winners:mem.winners.slice(),build:B2,when:mem.when},trimmed=0;for(;;){try{localStorage.setItem("slc_win2",JSON.stringify(lsm));break}catch(e){if(lsm.winners.length<=300)break;lsm.winners=lsm.winners.slice(0,Math.floor(lsm.winners.length*0.9));trimmed++}}'))
E.append(('(trimmed?" <span class=warn>Browser storage full: memory trimmed to "+mem.winners.length+" best branches - export the winners .txt to keep the full list.</span>":"")+',
'(trimmed?" <span class=dim>(localStorage copy trimmed to "+lsm.winners.length+"; all "+mem.winners.length+" are in the browser DB)</span>":"")+'))
E.append(('["slc_win2","slc_win2_log","slc_win2_alerts"].forEach(function(k){try{localStorage.removeItem(k)}catch(e){}})',
'["slc_win2","slc_win2_log","slc_win2_alerts"].forEach(function(k){try{localStorage.removeItem(k)}catch(e){}});MEMC=null;idbPut("slc_win2",null)'))
E.append(('var top=tierTop(rA,0,12).concat(tierTop(rA,1,8),tierTop(rA,2,6)),B=[];',
'/* build 046: per-timeframe tops (3/2/1 per tier per TF) join the global tops for exits + regimes; MIX pairs and earlier builds\' Gen D seeds stay on the global tops */\n'
'  var topG=tierTop(rA,0,12).concat(tierTop(rA,1,8),tierTop(rA,2,6)),TFS={},topX=[];S.forEach(function(se){TFS[se.tf]=1});Object.keys(TFS).forEach(function(tf){var rT=rA.filter(function(r){return r.tf===tf});topX=topX.concat(tierTop(rT,0,3),tierTop(rT,1,2),tierTop(rT,2,1))});var top=uniqSpecs(topG.concat(topX)),B=[],BGN={};'))
E.append(('top.forEach(function(sp){EXITS.concat(EXITS2,EXITS3).forEach(function(x){var c=JSON.parse(JSON.stringify(sp));c.x=x;B.push(c)})});',
'top.forEach(function(sp){var g=topG.indexOf(sp)>=0;EXITS.concat(EXITS2,EXITS3).forEach(function(x){var c=JSON.parse(JSON.stringify(sp));c.x=x;B.push(c);if(g)BGN[nm(c)]=1})});'))
E.append(('for(var p=0;p<top.length;p++)for(var q=p+1;q<top.length;q++)Cm.push({k:"MIX",a:top[p],b:top[q],w:3});',
'for(var p=0;p<topG.length;p++)for(var q=p+1;q<topG.length;q++)Cm.push({k:"MIX",a:topG[p],b:topG[q],w:3});'))
E.append(('var D=[],seed=top.concat(tierUpTo(rB,0,6),tierUpTo(rC,0,4),tierUpTo(rB,1,6),tierUpTo(rC,1,4),topSpecs(rB,6),topSpecs(rC,4));',
'var rBG=rB.filter(function(r){return BGN[r.sig]}),D=[],seed=top.concat(tierUpTo(rBG,0,6),tierUpTo(rC,0,4),tierUpTo(rBG,1,6),tierUpTo(rC,1,4),topSpecs(rBG,6),topSpecs(rC,4),topSpecs(rB,6));'))
for old,new in E: m=rep(m,old,new)
nb=m.count('build 045');assert nb>=4;m=m.replace('build 045','build 046');m=rep(m,'build045','build046',m.count('build045'))
old_disp=[l for l in m.split('\n') if 'var B2="v0.01d build 046 | ' in l][0].split('var B2="v0.01d build 046 | ')[1].split('"')[0];m=rep(m,old_disp,disp,m.count(old_disp))
open(src_in,'w',encoding='utf-8').write(m)
bk=[f for f in os.listdir('.') if f.startswith('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build045')][0]
hdr='\n'.join(open(bk,encoding='utf-8').read().split('\n')[:4]).replace('build 045','build 046').replace(old_disp,disp)
open('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build046_'+stamp+'.txt','w',encoding='utf-8').write(hdr+'\n'+m)
open('patches/w2_build046_added_code_BACKUP.txt','w',encoding='utf-8').write('Win Logic v2 build 046 patch - added/changed code | '+disp+'\n\nAlso: every ld("slc_win2",{winners:[]}) read -> memGet()\n\n'+'\n\n'.join('--- replaces: '+o[:100]+'\n'+n for o,n in E))
h=open(html_in,encoding='utf-8').read();h=rep(h,m0,m);h=h.replace('build 045','build 046');h=h.replace('build045','build046')
out='Signal_Live_Companion_v0.01d_build046_WinLogicV2_tfseeds_idb_'+stamp+'.html';open(out,'w',encoding='utf-8').write(h)
print('wrote',out,len(h),'| module',len(m),'| "build 045" left:',h.count('build 045'),'| disp',old_disp,'->',disp)
