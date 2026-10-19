#!/usr/bin/env python3
# Win Logic v2 build 047 (on top of 046): (1) memory cap 20000 -> 50000 (build 046 found 20,260 winners on 156 series and cut 260).
# (2) Win Logic v1 (Sept 2026 branch engine B0-B16, Signal repo) ideas ported as a fourth search tier, long-only, real data, 70/30 hold-out:
#     CNV = convergent Stochastic: K(n) crosses up through lv AND at least q of K5/K10/K15/K20 are rising and below 60 (v1 Convergent / Relax-Conv);
#     exits ctp/csl = take profit / stop as multiples of the round-trip cost (v1 tpMulti/slMulti x rtCost);
#     regime ll = v1's loss-learned skip rules as a fixed filter: skip if ATR5/ATR14 < 0.65, if the SMA20 5-bar slope <= -0.03%, or if K14 > 57 and K42 > 58.
#     Earlier tiers are searched exactly as in build 046 (same tops, same MIX pairs, same Gen D seeds), so build 046's branch set is a strict subset.
# usage: python3 patches/w2_build047_patch.py <w2_module_source.html> <build046.html> <YYYYMMDD-HHMM> "<D Mon YYYY HH:MM EDT>"
import sys,os
src_in,html_in,stamp,disp=sys.argv[1:5]
def rep(s,old,new,n=1):
    c=s.count(old);assert c==n,('count %d != %d for: %s'%(c,n,old[:90]));return s.replace(old,new)
m0=open(src_in,encoding='utf-8').read();m=m0;E=[]
E.append(('(x.atr?" atrail"+x.atr:"")','(x.atr?" atrail"+x.atr:"")+(x.ctp?" ctp"+x.ctp:"")+(x.csl?" csl"+x.csl:"")'))
E.append(('k==="STD"?"SlowStoch"+sp.n+"/"+sp.s+" "+sp.lo+"/"+sp.hi:k;',
'k==="STD"?"SlowStoch"+sp.n+"/"+sp.s+" "+sp.lo+"/"+sp.hi:k==="CNV"?"ConvStoch"+sp.n+" x"+sp.lv+" q"+sp.q+"/"+sp.hi:k;'))
E.append(('return{en:en,ex:ex}}\nfunction regOK',
' /* build 047: Win Logic v1 port - convergent Stochastic (K(n) crosses up through lv, at least q of K5/10/15/20 rising and below 60) */\n'
' else if(sp.k==="CNV"){var kc=I(b,"sto",sp.n),K4=[5,10,15,20].map(function(p){return I(b,"sto",p)});for(i=1;i<n;i++){if(kc[i]==null||kc[i-1]==null)continue;ex[i]=kc[i]>sp.hi?1:0;if(!(kc[i-1]<sp.lv&&kc[i]>=sp.lv))continue;var ag=0;K4.forEach(function(a){if(a[i]!=null&&a[i-1]!=null&&a[i]>a[i-1]&&a[i]<60)ag++});en[i]=ag>=sp.q?1:0}}\n'
' return{en:en,ex:ex}}\nfunction regOK'))
E.append((' if(sp.reg==="trend"){',
' /* build 047: ll = Win Logic v1 loss-learned skip rules as a fixed filter (ATR contraction, falling SMA20, stretched fast + slow Stochastic) */\n'
' if(sp.reg==="ll"){var l5=I(b,"atr",5),l14=I(b,"atr",14),l20=I(b,"sma",20),lk=I(b,"sto",14),lk3=I(b,"sto",42);if(i<5||l5[i]==null||l14[i]==null||!l14[i]||l20[i]==null||l20[i-5]==null)return false;if(l5[i]/l14[i]<0.65)return false;if((l20[i]-l20[i-5])/l20[i]*100<=-0.03)return false;return!(lk[i]!=null&&lk3[i]!=null&&lk[i]>57&&lk3[i]>58)}\n'
' if(sp.reg==="trend"){'))
E.append(('else if(x.hold?i-pos.i>=x.hold:s.ex[i])done=true',
'else if(x.ctp&&g>=x.ctp*rt)done=true\nelse if(x.csl&&g<=-x.csl*rt)done=true\nelse if(x.hold?i-pos.i>=x.hold:s.ex[i])done=true'))
E.append(('STD:["n","s","lo","hi"]}[sp.k]||[];','STD:["n","s","lo","hi"],CNV:["n","lv","hi"]}[sp.k]||[];'))
E.append(('if((c.lo!=null)&&c.k!=="CCI"&&c.lo>=c.hi)return','if((c.lo!=null)&&c.k!=="CCI"&&c.lo>=c.hi)return;if(c.k==="CNV"&&c.lv>=c.hi)return'))
E.append(('EXITS3.forEach(function(x){XT[JSON.stringify(x)]=2});',
'EXITS3.forEach(function(x){XT[JSON.stringify(x)]=2});\n'
'/* build 047: fourth tier = Win Logic v1 port (CNV family, cost-multiple exits, ll regime) */\n'
'var BASE4=[{k:"CNV",n:5,lv:20,q:2,hi:80},{k:"CNV",n:10,lv:20,q:2,hi:80},{k:"CNV",n:10,lv:20,q:1,hi:80},{k:"CNV",n:10,lv:50,q:2,hi:80},{k:"CNV",n:15,lv:20,q:3,hi:80}];\n'
'var EXITS4=[{ctp:3,csl:2},{ctp:4,csl:2.5},{ctp:3,csl:1.5},{ctp:3,csl:2,hold:12},{ctp:4,csl:3,hold:8}],REGS4=["ll"];KT.CNV=3;RT.ll=3;EXITS4.forEach(function(x){XT[JSON.stringify(x)]=3});'))
E.append(('BASE3.concat.apply(BASE3,BASE3.map(neighbours))));','BASE3.concat.apply(BASE3,BASE3.map(neighbours)),BASE4.concat.apply(BASE4,BASE4.map(neighbours))));'))
E.append(('var top=uniqSpecs(topG.concat(topX))',
'var top4=tierTop(rA,3,6);Object.keys(TFS).forEach(function(tf){top4=top4.concat(tierTop(rA.filter(function(r){return r.tf===tf}),3,1))});var top=uniqSpecs(topG.concat(topX,top4))'))
E.append(('EXITS.concat(EXITS2,EXITS3).forEach','EXITS.concat(EXITS2,EXITS3,EXITS4).forEach'))
E.append(('for(var p=0;p<topG.length;p++)for(var q=p+1;q<topG.length;q++)Cm.push({k:"MIX",a:topG[p],b:topG[q],w:3});',
'var tg4=topG.concat(tierTop(rA,3,6));for(var p=0;p<tg4.length;p++)for(var q=p+1;q<tg4.length;q++)Cm.push({k:"MIX",a:tg4[p],b:tg4[q],w:3});'))
E.append(('topSpecs(rB,6));','topSpecs(rB,6),tierUpTo(rB,3,6),tierUpTo(rC,3,4));'))
E.append(('REGS2.concat(REGS3).forEach','REGS2.concat(REGS3,REGS4).forEach'))
E.append(('.slice(0,20000)','.slice(0,50000)'))
for old,new in E: m=rep(m,old,new)
nb=m.count('build 046');assert nb>=4;m=m.replace('build 046','build 047');m=rep(m,'build046','build047',m.count('build046'))
old_disp=[l for l in m.split('\n') if 'var B2="v0.01d build 047 | ' in l][0].split('var B2="v0.01d build 047 | ')[1].split('"')[0];m=rep(m,old_disp,disp,m.count(old_disp))
open(src_in,'w',encoding='utf-8').write(m)
bk=[f for f in os.listdir('.') if f.startswith('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build046')][0]
hdr='\n'.join(open(bk,encoding='utf-8').read().split('\n')[:4]).replace('build 046','build 047').replace(old_disp,disp).replace('MQL families)','MQL families + v1 port)')
open('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build047_'+stamp+'.txt','w',encoding='utf-8').write(hdr+'\n'+m)
open('patches/w2_build047_added_code_BACKUP.txt','w',encoding='utf-8').write('Win Logic v2 build 047 patch - added/changed code | '+disp+'\n\n'+'\n\n'.join('--- replaces: '+o[:100]+'\n'+n for o,n in E))
h=open(html_in,encoding='utf-8').read();h=rep(h,m0,m);h=h.replace('build 046','build 047');h=h.replace('build046','build047')
h=h.replace('<title>Signal Live Companion v0.01d build 047 | 9 Oct 2026','<title>Signal Live Companion v0.01d build 047 | '+' '.join(disp.split()[:3]))
out='Signal_Live_Companion_v0.01d_build047_WinLogicV2_v1port_'+stamp+'.html';open(out,'w',encoding='utf-8').write(h)
print('wrote',out,len(h),'| module',len(m),'| "build 046" left:',h.count('build 046'),'| disp',old_disp,'->',disp)
