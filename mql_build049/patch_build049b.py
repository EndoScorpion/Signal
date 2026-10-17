#!/usr/bin/env python3
"""patch_build049b.py — Fix tier-4 broken families in w2_module_source.html
Fixes: VWD thresholds, ACG gate, RVL volume proxy, GAP exhaustion redef, PAV loosen
Improves: VQZ RSI trend filter, PBR RSI fix
"""
import sys

f = '/home/user/mql/w2_module_source.html'
with open(f, 'r', encoding='utf-8') as fh:
    s = fh.read()

orig_len = len(s)

patches = [
    # 1. VWD seeds: d=15,20,10 → d=3,5,7 (0.3%, 0.5%, 0.7% below VWAP proxy)
    (
        '{k:"VWD",n:20,d:15},{k:"VWD",n:14,d:20},{k:"VWD",n:20,d:10}',
        '{k:"VWD",n:20,d:3},{k:"VWD",n:14,d:5},{k:"VWD",n:20,d:7}',
        'VWD seeds loosen to 0.3/0.5/0.7%'
    ),
    # 2. ACG seeds: g=300,250,200 → g=50,100,150 (0.5%, 1%, 1.5% ATR gate)
    (
        '{k:"ACG",n:20,d:20,g:300},{k:"ACG",n:20,d:25,g:250},{k:"ACG",n:14,d:20,g:200}',
        '{k:"ACG",n:20,d:20,g:50},{k:"ACG",n:20,d:25,g:100},{k:"ACG",n:14,d:20,g:150}',
        'ACG gate loosen to 0.5/1/1.5%'
    ),
    # 3. GAP seeds: g=50,100,200 → g=10,15,20 (now ATR multiplier in tenths: 1x,1.5x,2x)
    (
        '{k:"GAP",g:50},{k:"GAP",g:100},{k:"GAP",g:200}',
        '{k:"GAP",g:10},{k:"GAP",g:15},{k:"GAP",g:20}',
        'GAP seeds redef as ATR mult x10'
    ),
    # 4. RVL: replace x.v||0 (always 0) with H-L range proxy (h-l)/c
    (
        'var rvVol=b.map(function(x){return x.v||0})',
        'var rvVol=b.map(function(x){return(x.h-x.l)/x.c})',
        'RVL volume → HL range proxy'
    ),
    # 5. GAP sigOf: replace gap-down logic with exhaustion-bar reversal (large bear bar → next bar closes higher)
    (
        'else if(sp.k==="GAP"){var gpC=C(b);for(i=1;i<n;i++){var gpG=(b[i].o-b[i-1].c)/b[i-1].c*100;ex[i]=gpC[i]>b[i].o+(b[i].o-b[i-1].c)*0.5?1:0;en[i]=(gpG<=-sp.g/100&&b[i].c>b[i].o)?1:0}}',
        'else if(sp.k==="GAP"){var gpC=C(b),gpAt=I(b,"atr",14);for(i=1;i<n;i++){if(gpAt[i]==null)continue;var gpR=b[i-1].h-b[i-1].l;ex[i]=gpC[i]>gpC[i-1]*1.005?1:0;en[i]=(gpR>=gpAt[i]*sp.g/10&&b[i-1].c<b[i-1].o&&gpC[i]>gpC[i-1])?1:0}}',
        'GAP redef: exhaustion bar reversal (large bear bar >= g/10 × ATR14)'
    ),
    # 6. PAV: loosen shr from [1,4] to [0.3,3] and RSI from <40 to <50
    (
        'en[i]=(pvC[i-2]<pvC[i-3]&&pvC[i-1]>pvC[i-2]&&pvC[i]>pvC[i-1]&&pvShr>=1&&pvShr<=4&&pvRs[i]<40)?1:0',
        'en[i]=(pvC[i-2]<pvC[i-3]&&pvC[i-1]>pvC[i-2]&&pvC[i]>pvC[i-1]&&pvShr>=0.3&&pvShr<=3&&pvRs[i]<50)?1:0',
        'PAV loosen shr [0.3,3], RSI<50'
    ),
    # 7. VQZ: add RSI>50 momentum filter to improve win quality
    (
        'en[i]=(bwMin<vqSd[i]&&vqSd[i]>vqSd[i-1]&&(bwMin>0?(vqSd[i]-bwMin)/vqSd[i]*100:100)<sp.d&&vqRs[i]>vqRs[i-1]&&vqRs[i-1]>vqRs[i-2])?1:0',
        'en[i]=(bwMin<vqSd[i]&&vqSd[i]>vqSd[i-1]&&(bwMin>0?(vqSd[i]-bwMin)/vqSd[i]*100:100)<sp.d&&vqRs[i]>50&&vqRs[i]>vqRs[i-1]&&vqRs[i-1]>vqRs[i-2])?1:0',
        'VQZ add RSI>50 momentum filter'
    ),
    # 8. PBR: fix RSI condition — require RSI>50 (positive momentum) and remove upper cap
    (
        'en[i]=(pbC[i-2]>pbEm[i-2]&&pbC[i-1]<pbEm[i-1]*1.005&&pbC[i]>pbEm[i]&&pbRs[i]>40&&pbRs[i]<60)?1:0',
        'en[i]=(pbC[i-2]>pbEm[i-2]&&pbC[i-1]<pbEm[i-1]*1.005&&pbC[i]>pbEm[i]&&pbRs[i]>50)?1:0',
        'PBR RSI>50 only (remove upper cap)'
    ),
]

ok = True
for old, new, desc in patches:
    cnt = s.count(old)
    if cnt != 1:
        print(f'FAIL [{desc}]: count={cnt}')
        ok = False
    else:
        s = s.replace(old, new)
        print(f'OK   [{desc}]')

if ok:
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f'\nWrote {f} ({orig_len} → {len(s)} chars)')
else:
    print('\nAborted — no file written')
    sys.exit(1)
