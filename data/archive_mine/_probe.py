import json,sys,collections
p=sys.argv[1]
c=collections.Counter(); ex={}
with open(p,encoding='utf-8',errors='replace') as f:
    for i,line in enumerate(f):
        if i>400000: break
        try: d=json.loads(line)
        except Exception: c['bad']+=1; continue
        t=d.get('type'); c[t]+=1
        m=d.get('message')
        if isinstance(m,dict) and t not in ex:
            cont=m.get('content')
            ex[t]=(list(d.keys())[:12], m.get('role'), type(cont).__name__, (cont[0].get('type') if isinstance(cont,list) and cont and isinstance(cont[0],dict) else None))
print(c.most_common(12))
for k,v in ex.items(): print(k,v)
