import json, os, re, sys
ROOTS = [r"C:\Users\endos\.claude\projects\C--Users-endos-Desktop",
         r"C:\Users\endos\.claude\projects\C--Users-endos-Desktop--",
         r"C:\Users\endos\.claude\projects\C--Users-endos-Desktop-hst-out",
         r"C:\Users\endos\.claude\projects\C--Users-endos"]
PAT = re.compile(r"stoch|entry|trigger|gate|filter|regime|\bWIN\b|PF |profit|win rate|extern", re.I)
OUT = r"C:\Users\endos\Signal\data\archive_mine\_scan_hits.tsv"
def text_of(msg):
    c = msg.get("content")
    if isinstance(c, str): return c
    out = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "text": out.append(b.get("text", ""))
    return "\n".join(out)
n = 0
with open(OUT, "w", encoding="utf-8") as fo:
    for root in ROOTS:
        if not os.path.isdir(root): continue
        for fn in sorted(os.listdir(root)):
            if not fn.endswith(".jsonl"): continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8", errors="replace") as f:
                for ln, line in enumerate(f):
                    try: o = json.loads(line)
                    except Exception: continue
                    m = o.get("message")
                    if not isinstance(m, dict): continue
                    if m.get("role") != "user": continue  # Nasif's own messages only
                    t = text_of(m)
                    if not t or "Pirates" in t: continue
                    for mt in PAT.finditer(t):
                        s = max(0, mt.start()-150); e = min(len(t), mt.end()+150)
                        w = t[s:e].replace("\t"," ").replace("\n"," / ")
                        fo.write(f"{fn[:8]}\t{o.get('timestamp','')[:10]}\t{ln}\t{w}\n"); n += 1
print("hits", n)
