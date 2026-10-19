#!/usr/bin/env python3
# Win Logic v2 build 045 (on top of 044): new timeframe code M240 (Webull session-clipped 4h bars; H2 already existed) so external
# 2h/4h series never collide with the page's clock-resampled M120/H4 series; build bump 044 -> 045. Exact read-replace with assertions.
# usage: python3 patches/w2_build045_patch.py <w2_module_source.html> <build044.html> <YYYYMMDD-HHMM> "<D Mon YYYY HH:MM EDT>"
import sys,os
src_in,html_in,stamp,disp=sys.argv[1:5]
def rep(s,old,new,n=1):
    c=s.count(old);assert c==n,('count %d != %d for: %s'%(c,n,old[:90]));return s.replace(old,new)
m0=open(src_in,encoding='utf-8').read();m=m0;E=[]
E.append(('var TFM={M1:1,M3:3,M5:5,M15:15,M30:30,M60:60,H1:60,M120:120,H2:120,H4:240,D1:1440};','var TFM={M1:1,M3:3,M5:5,M15:15,M30:30,M60:60,H1:60,M120:120,H2:120,H4:240,M240:240,D1:1440}; /* build 045: M240 = session-clipped 4h bars from an external source (H2 = 2h); M120/H4 stay the clock-resampled series */'))
for old,new in E: m=rep(m,old,new)
nb=m.count('build 044');assert nb>=4;m=m.replace('build 044','build 045');m=rep(m,'build044','build045',m.count('build044'))
old_disp=[l for l in m.split('\n') if 'var B2="v0.01d build 045 | ' in l][0].split('var B2="v0.01d build 045 | ')[1].split('"')[0];m=rep(m,old_disp,disp,m.count(old_disp))
open(src_in,'w',encoding='utf-8').write(m)
bk=[f for f in os.listdir('.') if f.startswith('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build044')][0]
hdr='\n'.join(open(bk,encoding='utf-8').read().split('\n')[:4]).replace('build 044','build 045').replace(old_disp,disp)
open('Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build045_'+stamp+'.txt','w',encoding='utf-8').write(hdr+'\n'+m)
open('patches/w2_build045_added_code_BACKUP.txt','w',encoding='utf-8').write('Win Logic v2 build 045 patch - added/changed code | '+disp+'\n\n'+'\n\n'.join('--- replaces: '+o[:100]+'\n'+n for o,n in E))
h=open(html_in,encoding='utf-8').read();h=rep(h,m0,m);h=h.replace('build 044','build 045');h=h.replace('build044','build045')
out='Signal_Live_Companion_v0.01d_build045_WinLogicV2_MQL2ext_'+stamp+'.html';open(out,'w',encoding='utf-8').write(h)
print('wrote',out,len(h),'| module',len(m),'| "build 044" left:',h.count('build 044'),'| disp',old_disp,'->',disp)
