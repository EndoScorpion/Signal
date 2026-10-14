import json,sys,re,os
SKIP=('d9ad0f50','c4362a85')
D='C:/Users/endos/.claude/projects/C--Users-endos-Signal/'
files=[f for f in sorted(os.listdir(D)) if f.endswith('.jsonl') and not f.startswith(SKIP)]
PAT=re.compile(sys.argv[1], re.I)
MODE=sys.argv[2]  # count | hits
W=int(sys.argv[3]) if len(sys.argv)>3 else 150
out=open('C:/Users/endos/Signal/data/archive_mine/_hits.txt','w',encoding='utf-8') if MODE=='hits' else None
from collections import Counter
cnt=Counter(); total=0
for fn in files:
    sid=fn[:8]
    with open(D+fn,encoding='utf-8',errors='replace') as f:
        for ln,line in enumerate(f):
            try: d=json.loads(line)
            except Exception: continue
            t=d.get('type')
            if t not in ('user','assistant'): continue
            m=d.get('message') or {}
            c=m.get('content')
            chunks=[]
            if isinstance(c,str): chunks.append(c)
            elif isinstance(c,list):
                for it in c:
                    if not isinstance(it,dict): continue
                    if it.get('type')=='text': chunks.append(it.get('text',''))
                    elif it.get("type")=="tool_use" and os.environ.get("TU")=="1": chunks.append(json.dumps(it.get('input',{}),ensure_ascii=False))
            ts=(d.get('timestamp') or '')[:10]
            for ch in chunks:
                for mt in PAT.finditer(ch):
                    total+=1; cnt[sid]+=1
                    if out:
                        s=max(0,mt.start()-W); e=min(len(ch),mt.end()+W)
                        win=re.sub(r'\s+',' ',ch[s:e])
                        out.write(f"[{sid} {ts} L{ln}] {win}\n")
print('total',total, dict(cnt))
if out: out.close()
