import json,sys,glob,os
d=r"C:\Users\endos\.claude\projects\C--Users-endos-AppData-Roaming-MetaQuotes-Terminal-6278E353D77D4E501C6775ACEC85F415-MQL4"
f=sorted(glob.glob(os.path.join(d,"*.jsonl")))[0]
with open(f,encoding="utf-8",errors="replace") as fh:
    for i,line in enumerate(fh):
        if i>=3: break
        o=json.loads(line)
        print({k:(type(v).__name__) for k,v in o.items()})
        m=o.get("message")
        if isinstance(m,dict):
            c=m.get("content")
            print(" content type", type(c).__name__, (c[0].get("type") if isinstance(c,list) and c and isinstance(c[0],dict) else ""))
