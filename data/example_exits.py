import json
d = json.load(open(r"C:\Users\endos\Signal\data\example_signal.json")); b = d["bars"]
t = [x[0] for x in b]; C = [x[1] for x in b]; M = [x[2] for x in b]; U = [x[3] for x in b]
E = 40; X = 88; entry = C[E]; COST = 5
def pts(px): return round((entry - px) * 1e5 - COST, 1)
def trail(start, dist):
    sl = None; low = entry
    for i in range(E + 1, X + 1):
        low = min(low, C[i])
        if (entry - low) * 1e5 >= start: sl = low + dist * 1e-5 if sl is None else min(sl, low + dist * 1e-5)
        if sl is not None and C[i] >= sl: return i, sl
    return X, C[X]
res = {"time 48 bars": (X, C[X])}
for i in range(E + 1, X + 1):
    if C[i] <= M[i]: res["mean touch"] = (i, C[i]); break
res["trail 150/250"] = trail(150, 250); res["trail 100/150"] = trail(100, 150); res["trail 200/200"] = trail(200, 200)
low_i = min(range(E, X + 1), key=lambda i: C[i]); res["hindsight low"] = (low_i, C[low_i])
for k, (i, px) in res.items(): print(f"{k:16} bar {i} {t[i]} px {px:.5f}  net {pts(px):+.0f} pts")
print("C=", C); print("M=", M); print("U=", U)
