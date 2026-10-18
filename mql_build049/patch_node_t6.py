#!/usr/bin/env python3
"""patch_node_t6.py — Fix w2_node.js to support BASE5 (tier-4 families) in the generation pipeline."""
import sys

f = '/home/user/mql/tools/w2_node.js'
with open(f, 'r', encoding='utf-8') as fh:
    s = fh.read()

orig_len = len(s)

patches = [
    # 1. Add T6 detection (BASE5 = tier-4 families added in build 049)
    (
        'const NEW=typeof BASE2!==\'undefined\',T3=typeof tierOf===\'function\',T4=m.indexOf(\'function memGet(\')>=0,T5=typeof BASE4!==\'undefined\';',
        'const NEW=typeof BASE2!==\'undefined\',T3=typeof tierOf===\'function\',T4=m.indexOf(\'function memGet(\')>=0,T5=typeof BASE4!==\'undefined\',T6=typeof BASE5!==\'undefined\';',
        'Add T6 = BASE5 detection'
    ),
    # 2. Gen A: add BASE5 neighbours after BASE4
    (
        'if(T5)A=A.concat(BASE4.concat.apply(BASE4,BASE4.map(neighbours)));A=uniqSpecs(A);',
        'if(T5)A=A.concat(BASE4.concat.apply(BASE4,BASE4.map(neighbours)));if(T6)A=A.concat(BASE5.concat.apply(BASE5,BASE5.map(neighbours)));A=uniqSpecs(A);',
        'Gen A: add BASE5 + neighbours'
    ),
    # 3. top selection: add tier-4 tops (tierTop index 4) when T6
    (
        'let top4=[];if(T5){top4=tierTop(rA,3,6);Object.keys(TFS).forEach(tf=>{top4=top4.concat(tierTop(rA.filter(r=>r.tf===tf),3,1))})}top=uniqSpecs(topG.concat(topX,top4))}',
        'let top4=[];if(T5){top4=tierTop(rA,3,6);Object.keys(TFS).forEach(tf=>{top4=top4.concat(tierTop(rA.filter(r=>r.tf===tf),3,1))})}let top5=[];if(T6){top5=tierTop(rA,4,6);Object.keys(TFS).forEach(tf=>{top5=top5.concat(tierTop(rA.filter(r=>r.tf===tf),4,1))})}top=uniqSpecs(topG.concat(topX,top4,top5))}',
        'top selection: add tier-4 tops'
    ),
    # 4. Gen B exits: add EXITS5 when T6
    (
        '(T5?EXITS.concat(EXITS2,EXITS3,EXITS4):T3?EXITS.concat(EXITS2,EXITS3):NEW?EXITS.concat(EXITS2):EXITS)',
        '(T6?EXITS.concat(EXITS2,EXITS3,EXITS4,EXITS5):T5?EXITS.concat(EXITS2,EXITS3,EXITS4):T3?EXITS.concat(EXITS2,EXITS3):NEW?EXITS.concat(EXITS2):EXITS)',
        'Gen B: add EXITS5'
    ),
    # 5. Gen C MIX pool: add tier-4 tops
    (
        'const tg4=T5?topG.concat(tierTop(rA,3,6)):topG;',
        'const tg4=T6?topG.concat(tierTop(rA,3,6),tierTop(rA,4,6)):T5?topG.concat(tierTop(rA,3,6)):topG;',
        'Gen C: add tier-4 to MIX pool'
    ),
    # 6. Gen D seeds: add tierUpTo for tier-4
    (
        'T5?tierUpTo(rB,3,6):[],T5?tierUpTo(rC,3,4):[]):',
        'T6?tierUpTo(rB,4,6):[],T6?tierUpTo(rC,4,4):[],T5?tierUpTo(rB,3,6):[],T5?tierUpTo(rC,3,4):[]):',
        'Gen D seeds: add tier-4 from rB/rC'
    ),
    # 7. Gen D regimes: add REGS5 when T6
    (
        '(T5?REGS2.concat(REGS3,REGS4):T3?REGS2.concat(REGS3):NEW?REGS2:["quiet","trend"])',
        '(T6?REGS2.concat(REGS3,REGS4,REGS5):T5?REGS2.concat(REGS3,REGS4):T3?REGS2.concat(REGS3):NEW?REGS2:["quiet","trend"])',
        'Gen D: add REGS5'
    ),
    # 8. W2_CAP: keep 50000 cap for T6 (same as T5)
    (
        '.slice(0,+process.env.W2_CAP||(T5?50000:T4?20000:T3?8000:NEW?5000:300))',
        '.slice(0,+process.env.W2_CAP||(T6?50000:T5?50000:T4?20000:T3?8000:NEW?5000:300))',
        'W2_CAP: T6 = 50000'
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
