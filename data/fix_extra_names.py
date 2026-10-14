import json
p = r"C:\Users\endos\Signal\data\extra_candidates.json"
x = json.load(open(p))
n = 0
for e in x:
    if "." in e["name"]: e["name"] = e["name"].replace(".", "p"); n += 1
json.dump(x, open(p, "w"), indent=1); print("renamed", n, "candidates; total", len(x))
