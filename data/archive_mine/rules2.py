import re
p=r"C:\Users\endos\AppData\Local\Temp\claude\C--Users-endos-Signal\c4362a85-effe-4081-bb24-77c06f43475c\scratchpad\hits.tsv"
pat=re.compile(r"pullback|breakout|bollinger|\bSMA\b|ADX|ladder|RLOG|HEDGE|Thursday|fade|ZGate|ER\b|trail|BlockADX|rule \d|signal \d",re.I)
seen=set(); rows=[]
for line in open(p,encoding="utf-8"):
    sid,ts,t,win=line.rstrip("\n").split("\t",3)
    if not pat.search(win): continue
    key=re.sub(r"[^a-z0-9]","",win.lower())[:60]
    if key in seen: continue
    seen.add(key); rows.append((sid,ts,win[:230]))
print(len(rows))
for r in rows[:70]: print(r[0],r[1],r[2])
