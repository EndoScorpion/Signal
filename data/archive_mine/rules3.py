import re
p=r"C:\Users\endos\AppData\Local\Temp\claude\C--Users-endos-Signal\c4362a85-effe-4081-bb24-77c06f43475c\scratchpad\hits.tsv"
rule=re.compile(r"pullback|breakout|bollinger|ADX|ladder|RLOG|HEDGE|Thursday|BlockADX|Strong2010|\bg\d[a-z]\b|sweep|reclaim|Monday|trail",re.I)
num=re.compile(r"PF\s?\d|\d+\s?pts|[+-]?\$\d|\d+%|p\s?=\s?0?\.\d")
noise=re.compile(r"relay|cross-session|<note>|hub|PAUSE|RAM|Usage:|handoff|sent-at|Desktop Commander|Process",re.I)
seen=set(); rows=[]
for line in open(p,encoding="utf-8"):
    sid,ts,t,win=line.rstrip("\n").split("\t",3)
    if t!="assistant" or not rule.search(win) or not num.search(win) or noise.search(win): continue
    key=re.sub(r"[^a-z0-9]","",win.lower())[:50]
    if key in seen: continue
    seen.add(key); rows.append((sid,ts,win[:210]))
print(len(rows))
for r in rows[:60]: print(r[0],r[1],r[2])
