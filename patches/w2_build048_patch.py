#!/usr/bin/env python3
# Win Logic v2 build 048 (on top of 047): default commission = 8 points per round trip, flat (no margin or balance link), per Nasif 11 Oct 2026.
# Point = 0.01 at price >= 10, 0.001 at 1-10, 0.0001 at 0.01-1, 0.00001 below; converted to % of the series' mean close and ADDED to the class
# commission %/side (stock/crypto/perp 0, Bloxwap builder fee 0.05 stays separate). Exchange fee, spread, swap, tax unchanged. Editable per class
# in the cost table ("Commission points / round trip"); older saved cost tables without the field get 8.
# usage: python3 patches/w2_build048_patch.py <w2_module_source.html> <build047.html> <YYYYMMDD-HHMM> "<D Mon YYYY HH:MM EDT>"
import sys,os
src_in,html_in,stamp,disp=sys.argv[1:5]
def rep(s,old,new,n=1):
    c=s.count(old);assert c==n,('count %d != %d for: %s'%(c,n,old[:90]));return s.replace(old,new)
m0=open(src_in,encoding='utf-8').read();m=m0;E=[]
for c in ['stock','crypto','perp','bloxwap']:
    E.append((c+':{comm:',c+':{pts:8,comm:'))
E.append(('function costOf(se){return COSTS[clsOf(se)]||COSTS.stock}',
'/* build 048: commission in points per round trip (default 8, flat), point by price level, as % of the series mean close, added to comm %/side */\n'
'function ptOf(px){return px>=10?0.01:px>=1?0.001:px>=0.01?0.0001:0.00001}\n'
'function costOf(se){var c=COSTS[clsOf(se)]||COSTS.stock,p=c.pts==null?8:+c.pts;if(!p||!se.b||!se.b.length)return c;if(se._mc==null){var s=0;se.b.forEach(function(x){s+=x.c});se._mc=s/se.b.length}var o={};for(var k in c)o[k]=c[k];o.comm=(+c.comm||0)+p*ptOf(se._mc)/2/se._mc*100;return o}'))
E.append(('var K=["comm","fee","spread","swap","tax"],H=["Commission %/side",','var K=["pts","comm","fee","spread","swap","tax"],H=["Commission points / round trip (point 0.01 at price &ge;10)","Extra commission %/side",'))
E.append(('value="\'+COSTS[c][k]+\'"','value="\'+(COSTS[c][k]==null?(k==="pts"?8:0):COSTS[c][k])+\'"'))
E.append(('Every trade pays commission + fee on both sides,','Commission = the points (round trip, flat, default 8) converted to % of the symbol price, plus any extra %/side; every trade pays fee on both sides,'))
for old,new in E: m=rep(m,old,new)
nb=m.count('build 047');assert nb>=4;m=m.replace('build 047','build 048');m=rep(m,'build047','build048',m.count('build047'))
old_disp=[l for l in m.split('\n') if 'var B2="v0.01d build 048 | ' in l][0].split('var B2="v0.01d build 048 | ')[1].split('"')[0];m=rep(m,old_disp,disp,m.count(old_disp))
open(src_in,'w',encoding='utf-8').write(m)
bk=[f for f in os.listdir('.') if f.startswith('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build047')][0]
hdr='\n'.join(open(bk,encoding='utf-8').read().split('\n')[:4]).replace('build 047','build 048').replace(old_disp,disp).replace('v1 port)','v1 port + 8 pt commission)')
open('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build048_'+stamp+'.txt','w',encoding='utf-8').write(hdr+'\n'+m)
open('patches/w2_build048_added_code_BACKUP.txt','w',encoding='utf-8').write('Win Logic v2 build 048 patch - added/changed code | '+disp+'\n\n'+'\n\n'.join('--- replaces: '+o[:100]+'\n'+n for o,n in E))
h=open(html_in,encoding='utf-8').read();h=rep(h,m0,m);h=h.replace('build 047','build 048');h=h.replace('build047','build048')
out='Signal_Live_Companion_v0.01d_build048_WinLogicV2_8ptcomm_'+stamp+'.html';open(out,'w',encoding='utf-8').write(h)
print('wrote',out,len(h),'| module',len(m),'| "build 047" left:',h.count('build 047'),'| disp',old_disp,'->',disp)
