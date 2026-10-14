import ast
src = open(r"C:\Users\endos\Desktop\RestartExplorer.pyw", encoding="utf-8").read()
ast.parse(src); print("panel syntax ok")
ns = {}
exec(compile(src.split("root = tk.Tk()")[0], "panel_head", "exec"), ns)
ldr = ns["leader"](); ys = ns["year_stats"](ldr)
print("leader:", ldr)
for y, s in ys.items():
    print(y, f"{s['pts']:+.0f} pts, {s['n']} trades, DD {s['dd']:.1f}%, weak: {ns['weak_reason'](s)}")
y = "2024"
if int(y) in ys:
    from collections import defaultdict
    a = defaultdict(lambda: [0.0, 0])
    for mo, p in ys[int(y)]["months"]: a[mo][0] += p; a[mo][1] += 1
    print("2024 months:", {k: (round(v[0]), v[1]) for k, v in sorted(a.items())})
