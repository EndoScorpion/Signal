import json,glob,os,collections
d=r"C:\Users\endos\.claude\projects\C--Users-endos-AppData-Roaming-MetaQuotes-Terminal-6278E353D77D4E501C6775ACEC85F415-MQL4"
cnt=collections.Counter(); ex={}
for f in sorted(glob.glob(os.path.join(d,"*.jsonl"))):
    with open(f,encoding="utf-8",errors="replace") as fh:
        for line in fh:
            try: o=json.loads(line)
            except Exception: cnt["bad"]+=1; continue
            t=o.get("type"); cnt[t]+=1
            if t not in ex and isinstance(o.get("message"),dict):
                ex[t]=json.dumps(o)[:400]
print(cnt)
for k,v in ex.items(): print(k, v[:400])
