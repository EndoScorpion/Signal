import re,collections
p=r"C:\Users\endos\AppData\Local\Temp\claude\C--Users-endos-Signal\c4362a85-effe-4081-bb24-77c06f43475c\scratchpad\hits.tsv"
terms=["ZGate","MMR","ChaosRegime","Hurst","ZMax","SMA","stoch","ADX","ladder","RLOG","HEDGE","SELLSTOP","Strong2010","BlockADX","RiskGuard","Monday","Thursday","hour","breakout","pullback","mean","fade","bollinger","BBW","news","NFP","spread","trail","TP\d+","SL\d+","PF 1\.\d+"]
cnt=collections.Counter()
for line in open(p,encoding="utf-8"):
    w=line.lower()
    for t in terms:
        if re.search(t.lower(),w): cnt[t]+=1
for t in terms: print(t,cnt[t])
