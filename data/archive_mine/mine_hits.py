import json,glob,os,re,collections
d=r"C:\Users\endos\.claude\projects\C--Users-endos-AppData-Roaming-MetaQuotes-Terminal-6278E353D77D4E501C6775ACEC85F415-MQL4"
out=r"C:\Users\endos\AppData\Local\Temp\claude\C--Users-endos-Signal\c4362a85-effe-4081-bb24-77c06f43475c\scratchpad\hits.tsv"
pat=re.compile(r"(entry|gate|filter|regime|\bWIN\b|PF\s?[=:]?\s?\d|profit factor|\bUse[A-Z]\w+|extern|stoch|slope|ZMax|\bER\b|z-score|daily range|MMR|\bpts\b|verdict|backtest|reject|FAIL|OOS|exit)",re.I)
n=0; per=collections.Counter()
with open(out,"w",encoding="utf-8") as w:
  for f in sorted(glob.glob(os.path.join(d,"*.jsonl"))):
    sid=os.path.basename(f)[:8]
    with open(f,encoding="utf-8",errors="replace") as fh:
        for line in fh:
            try: o=json.loads(line)
            except Exception: continue
            t=o.get("type")
            if t not in("user","assistant"): continue
            m=o.get("message") or {}
            c=m.get("content")
            texts=[]
            if isinstance(c,str): texts.append(c)
            elif isinstance(c,list):
                for b in c:
                    if isinstance(b,dict) and b.get("type")=="text": texts.append(b.get("text",""))
            ts=(o.get("timestamp") or "")[:10]
            for tx in texts:
                if t=="user" and tx.startswith("<relay") is False and len(tx)>4000: pass
                for mm in pat.finditer(tx):
                    s=max(0,mm.start()-120); e=min(len(tx),mm.end()+160)
                    win=re.sub(r"\s+"," ",tx[s:e])[:300]
                    w.write(f"{sid}\t{ts}\t{t}\t{win}\n"); n+=1; per[sid]+=1
print("hits",n); print(per)
