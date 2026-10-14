import json,re,os,sys
from collections import OrderedDict
D='C:/Users/endos/.claude/projects/C--Users-endos-Signal/'
SKIP=('d9ad0f50','c4362a85')
files=[f for f in sorted(os.listdir(D)) if f.endswith('.jsonl') and not f.startswith(SKIP)]
IDEA=re.compile(sys.argv[1],re.I)
VERD=re.compile(sys.argv[2],re.I)
MAXC=int(sys.argv[3]) if len(sys.argv)>3 else 260
res=OrderedDict()
for fn in files:
    sid=fn[:8]
    with open(D+fn,encoding='utf-8',errors='replace') as f:
        for ln,line in enumerate(f):
            try: d=json.loads(line)
            except Exception: continue
            t=d.get('type')
            if t not in ('user','assistant'): continue
            c=(d.get('message') or {}).get('content')
            chunks=[]
            if isinstance(c,str): chunks.append(c)
            elif isinstance(c,list):
                for it in c:
                    if isinstance(it,dict) and it.get('type')=='text': chunks.append(it.get('text',''))
            ts=(d.get('timestamp') or '')[:10]
            for ch in chunks:
                for s in re.split(r'(?<=[.!?])\s+|\n+|\s\|\s',ch):
                    s=re.sub(r'\s+',' ',s).strip()
                    if len(s)<25: continue
                    if IDEA.search(s) and VERD.search(s):
                        key=re.sub(r'[^a-z0-9]','',s.lower())[:90]
                        if key not in res:
                            res[key]=(sid,ts,s[:MAXC])
OUT=open(sys.argv[4],"w",encoding="utf-8") if len(sys.argv)>4 else sys.stdout
for k,(sid,ts,s) in res.items():
    print(f"{sid} {ts} {s}",file=OUT)
print('COUNT',len(res),file=sys.stderr)
