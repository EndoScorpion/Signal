import re,collections
p=r"C:\Users\endos\AppData\Local\Temp\claude\C--Users-endos-Signal\c4362a85-effe-4081-bb24-77c06f43475c\scratchpad\hits.tsv"
strong=re.compile(r"(\bUse[A-Z]\w*\s*[=:]\s*\S+|\b(Max|Min|Z|ER|Stoch\w*|K|D|Slope\w*|Range\w*|Fib\w*|Lookback|Period|Threshold|Level)\w*\s*[=:]\s*[\d.]+|PF\s?[=:]?\s?\d[\d.]*|\+?-?[\d,]{4,}\s?(pts|net|\$)|pts\s?[=:]?\s?[+-]?\d)",re.I)
seen=set(); rows=[]
for line in open(p,encoding="utf-8"):
    sid,ts,t,win=line.rstrip("\n").split("\t",3)
    if not strong.search(win): continue
    key=re.sub(r"[^a-z0-9]","",win.lower())[:90]
    if key in seen: continue
    seen.add(key); rows.append((sid,ts,t,win))
print(len(rows))
with open(p.replace("hits.tsv","strong.tsv"),"w",encoding="utf-8") as w:
    for r in rows: w.write("\t".join(r)+"\n")
